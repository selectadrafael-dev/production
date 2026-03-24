from odoo import models, fields
import base64
import logging
import json
# 🔥 ONLY ADD THIS IMPORT AT TOP
import requests
import time
import pandas as pd
import io
from openpyxl import load_workbook
from PIL import Image
from io import BytesIO

_logger = logging.getLogger(__name__)


class VendorImportJob(models.Model):

    _name = "vendor.import.job"
    _description = "Vendor Import Job"

    name = fields.Char(default="Vendor Data Import")

    data_url = fields.Char()
    extra_info = fields.Text()

    pdf_file = fields.Binary()
    excel_file = fields.Binary()
    logo_file = fields.Binary()

    extracted_text = fields.Text()
    ai_response = fields.Text()

    state = fields.Selection([
        ('draft', 'Draft'),
        ('processing', 'Processing'),
        ('ai_processing', 'AI Processing'),
        ('review', 'Vendor Review'),
        ('done', 'Completed'),
        ('error', 'Error')
    ], default='draft')

    #------excel processing methof---------------
    def parse_excel(self):
        _logger.warning("PROCESSING EXCEL FILE (WITH IMAGE SUPPORT)")

        excel_bytes = base64.b64decode(self.excel_file)

        #---------------- LOAD DATAFRAME ----------------
        try:
            df = pd.read_excel(io.BytesIO(excel_bytes))
        except Exception:
            df = pd.read_csv(io.BytesIO(excel_bytes))

        #---------------- LOAD WORKBOOK (FOR IMAGES) ----------------
        wb = load_workbook(filename=BytesIO(excel_bytes))
        ws = wb.active

        #---------------- EXTRACT EMBEDDED IMAGES ----------------
        image_map = {}  # row_index → [base64 images]

        for image in getattr(ws, '_images', []):
            try:
                row = image.anchor._from.row  # row position
                img_bytes = image._data()

                # ✅ FILTER HERE
                if len(img_bytes) > 5000:
                    img_base64 = base64.b64encode(img_bytes).decode("utf-8")
                    image_map.setdefault(row, []).append(img_base64)

            except Exception:
                continue

        _logger.warning(f"EMBEDDED IMAGES FOUND: {len(image_map)} ROWS")

        # ---------------- PROCESS ROWS ----------------
        pages = []
        page_size = 20
        current_page = []
        page_number = 1

        for idx, row in df.iterrows():

            row_text_parts = []
            row_images = []

            # 🔹 TEXT + URL EXTRACTION
            for col in df.columns:
                val = str(row[col])

                if val and val != "nan":

                    # detect image URL
                    if val.startswith("http") and any(ext in val.lower() for ext in [".jpg", ".png", ".jpeg", ".webp"]):
                        try:
                            response = requests.get(val, timeout=10)

                            if response.status_code == 200:
                                img_bytes = response.content

                                # ✅ FILTER HERE
                                if len(img_bytes) > 5000:
                                    img_base64 = base64.b64encode(img_bytes).decode("utf-8")
                                    row_images.append(img_base64)
                        except Exception:
                            pass
                    else:
                        row_text_parts.append(val)

            # 🔹 EMBEDDED IMAGES
            if idx in image_map:
                row_images.extend(image_map[idx])

            row_text = " | ".join(row_text_parts)

            current_page.append({
                "text": row_text,
                "images": row_images
            })

            # ---------------- PAGINATION ----------------
            if len(current_page) >= page_size:

                pages.append({
                    "page": page_number,
                    "rows": current_page
                })

                current_page = []
                page_number += 1

        if current_page:
            pages.append({
                "page": page_number,
                "rows": current_page
            })

        # ---------------- CONVERT TO STANDARD FORMAT ----------------
        final_pages = []

        for page in pages:

            combined_text = "\n".join([r["text"] for r in page["rows"]])
            combined_images = []

            for r in page["rows"]:
                combined_images.extend(r["images"])

            final_pages.append({
                "page": page["page"],
                "text": combined_text,
                "images": combined_images
            })

        self.extracted_text = json.dumps(final_pages)

        _logger.warning(f"EXCEL PARSED → {len(final_pages)} PAGES (WITH IMAGES)")

    # ---------------- MAIN FLOW ----------------

    def process_import(self):

        _logger.warning(f"PROCESS START → Job {self.id}")
        self.state = "processing"

        try:

            self.extracted_text = ""

            if self.pdf_file:
                _logger.warning("STEP → Extracting PDF")
                self.extract_pdf()

            if self.excel_file:
                _logger.warning("STEP → Parsing Excel")
                self.parse_excel()

            if self.data_url:
                _logger.warning("STEP → Scraping URL")
                self.scrape_website()

            if not self.extracted_text:
                _logger.error("NO TEXT EXTRACTED → STOPPING")
                self.state = "error"
                return

            _logger.warning("STEP → Sending to OpenAI")
            self.send_to_openai()

            _logger.warning("STEP → Creating products")
            self.create_product_drafts()

            self.state = "done"

            _logger.warning(f"PROCESS DONE → Job {self.id}")

        except Exception:
            _logger.exception("PROCESS FAILED")
            self.state = "error"

    # ---------------- PDF ----------------
    def extract_pdf(self):

        pdf_bytes = base64.b64decode(self.pdf_file)

        for attempt in range(2):

            try:
                _logger.warning(f"FLASK CALL ATTEMPT {attempt + 1}")

                response = requests.post(
                    "https://pdf-extractor-staging.onrender.com/extract",
                    files={"file": ("catalog.pdf", pdf_bytes, "application/pdf")},
                    timeout=180
                )

                if response.status_code == 200:
                    pages = response.json()

                    _logger.warning(f"RECEIVED {len(pages)} PAGES FROM FLASK")

                    self.extracted_text = json.dumps(pages)

                    return

                else:
                    _logger.warning(f"FLASK ERROR: {response.status_code}")

            except Exception:
                _logger.exception("FLASK CALL FAILED")

            time.sleep(7)

        self.state = "error"

    # ---------------- URL ----------------

    def scrape_website(self):

        from bs4 import BeautifulSoup

        try:
            r = requests.get(self.data_url, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")

            text = soup.get_text()

            self.extracted_text = json.dumps([{
                "page": 1,
                "text": text[:15000]
            }])

        except Exception:
            _logger.warning("URL scraping failed")

    # ---------------- OPENAI ----------------

    def send_to_openai(self):

        from openai import OpenAI

        self.state = "ai_processing"

        api_key = self.env['ir.config_parameter'].sudo().get_param('openai.api.key')

        if not api_key:
            raise Exception("OpenAI API key not configured")

        client = OpenAI(api_key=api_key)

        pages = json.loads(self.extracted_text or "[]")

        page_products = []

        for page in pages:

            page_no = page.get("page")
            text = page.get("text", "")

            if not text.strip():
                continue

            _logger.warning(f"AI → PAGE {page_no}")


            prompt = f"""
            You are a product extraction engine.

            Extract ALL products from this page.

            IMPORTANT:
            - Return ONLY valid JSON
            - No explanation
            - No markdown
            - No text outside JSON
            - If no products found, return []

            FORMAT:
            [
            {{
                "name": "",
                "description": "",
                "category": ""
            }}
            ]

            TEXT:
            {text}
            """

            try:
                response = client.responses.create(
                    model="gpt-4.1-mini",
                    input=prompt,
                    timeout=60
                )

                result = response.output_text.strip()
                _logger.warning(f"RAW AI RESPONSE PAGE {page_no} → {result[:200]}")

                # 🔥 CLEAN RESPONSE
                if "```" in result:
                    result = result.split("```")[1]

                if result.lower().startswith("json"):
                    result = result[4:]

                result = result.strip()

                # 🔥 SAFE PARSE
                try:
                    parsed = json.loads(result)
                except Exception:
                    _logger.warning(f"INVALID JSON → PAGE {page_no}")
                    continue

                if isinstance(parsed, list):
                    _logger.warning(f"PAGE {page_no} → {len(parsed)} products")
                    page_products.append({
                        "page": page_no,
                        "products": parsed
                    })

            except Exception as e:
                _logger.warning(f"PAGE {page_no} FAILED → {str(e)}")
                continue

                 # ✅ SAVE AI RESULT
            self.ai_response = json.dumps(page_products)

            _logger.warning(f"AI TOTAL PAGES STORED: {len(page_products)}")

     #-----------scoring image to pick---------------------------

    def pick_best_image(images):

        def score(img):
            try:
                img_bytes = base64.b64decode(img)

                size_score = len(img_bytes)

                # bonus for reasonable size
                if 20000 < size_score < 500000:
                    size_score += 50000

                return size_score

            except:
                return 0

        if not images:
            return None

        # 🔥 pick highest score
        best = sorted(images, key=score, reverse=True)[0]

        return best

    #---------------- PRODUCT CREATION ----------------
    def create_product_drafts(self):

        if not self.ai_response or not self.extracted_text:
            return

        import base64

        def is_valid_product_image(img_base64):
            try:
                img_bytes = base64.b64decode(img_base64)
                return len(img_bytes) > 5000
            except Exception:
                return False

        product_obj = self.env['product.template']
        category_obj = self.env['product.category']

        pages = json.loads(self.extracted_text)
        ai_pages = json.loads(self.ai_response)

        _logger.warning("CREATING PRODUCTS WITH PAGE-AWARE MAPPING")
        _logger.warning(f"AI PAGES COUNT: {len(ai_pages)}")

        for page_data in pages:

            page_no = page_data.get("page")

            raw_images = page_data.get("images", [])
            images = [img for img in raw_images if is_valid_product_image(img)]

            # ✅ find matching AI page
            ai_page = next((p for p in ai_pages if p.get("page") == page_no), None)

            if not ai_page:
                _logger.warning(f"NO AI DATA FOR PAGE {page_no}")
                continue

            products = ai_page.get("products", [])

            if not products:
                _logger.warning(f"NO PRODUCTS FOUND ON PAGE {page_no}")
                continue

            _logger.warning(f"PAGE {page_no} → {len(products)} PRODUCTS")

            for i, product in enumerate(products):

                name = product.get("name")
                if not name:
                    _logger.warning("SKIPPING EMPTY PRODUCT")
                    continue

                description = product.get("description", "")
                category_name = product.get("category", "Uncategorized")

                category = category_obj.search([('name', '=', category_name)], limit=1)

                if not category:
                    category = category_obj.create({'name': category_name})

                vals = {
                    'name': name,
                    'description_sale': description,
                    'categ_id': category.id,
                    'sale_ok': True,
                    'website_published': False,
                }

                best_image = pick_best_image(images)

                if best_image:
                    vals['image_1920'] = best_image
                    _logger.warning(f"BEST IMAGE SELECTED → {name}")
                else:
                    _logger.warning(f"NO IMAGE → {name}")

                product_obj.create(vals)

                _logger.warning(f"CREATED → {name}")
                _logger.warning(f"AI RESPONSE SAMPLE: {self.ai_response[:500]}")
    #---------------- CRON ----------------

    def run_pending_jobs(self):

        jobs = self.search([('state', '=', 'draft')])

        _logger.warning(f"CRON → Found {len(jobs)} jobs")

        for job in jobs:
            try:
                job.state = 'processing'
                job.process_import()
            except Exception:
                _logger.exception("CRON FAILED")
                job.state = 'error'  
    
    def ping_flask_server(self):
      
        try:
            requests.get("https://pdf-extractor-staging.onrender.com", timeout=10)
            _logger.info("FLASK PING SUCCESS")
        except Exception:
            _logger.warning("FLASK PING FAILED")
