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

        _logger.warning("EXCEL → START PARSING")

        excel_bytes = base64.b64decode(self.excel_file)

        # ---------------- LOAD DATA ----------------
        df = pd.read_excel(io.BytesIO(excel_bytes)).fillna("")

        wb = load_workbook(filename=BytesIO(excel_bytes))
        ws = wb.active

        # ---------------- EXTRACT EMBEDDED IMAGES ----------------
        image_map = {}

        for image in getattr(ws, '_images', []):
            try:
                row_excel = image.anchor._from.row  # 0-based

                # ✅ FIX: align Excel row index with pandas index
                row_index = row_excel - 1  # IMPORTANT FIX

                img_bytes = image._data()

                # ✅ FILTER SMALL IMAGES
                if len(img_bytes) < 5000:
                    continue

                img_base64 = base64.b64encode(img_bytes).decode("utf-8")

                image_map.setdefault(row_index, []).append(img_base64)

            except Exception as e:
                _logger.warning(f"IMAGE MAP ERROR → {str(e)}")

        _logger.warning(f"EMBEDDED IMAGE ROWS: {len(image_map)}")

        # ---------------- PROCESS ROWS ----------------
        pages = []
        current_page = []
        page_number = 1
        page_size = 20

        for idx, row in df.iterrows():

            row_text_parts = []
            row_images = []

            # 🔍 DEBUG START
            _logger.warning(f"ROW {idx} PROCESSING")

            # -------- TEXT + URL --------
            for col in df.columns:

                val = str(row[col]).strip()

                if not val:
                    continue

                # ✅ FIX: stricter image URL detection
                if val.startswith("http") and any(ext in val.lower() for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                    try:
                        response = requests.get(val, timeout=10)

                        if response.status_code == 200:
                            img_bytes = response.content

                            if len(img_bytes) > 5000:
                                img_base64 = base64.b64encode(img_bytes).decode("utf-8")
                                row_images.append(img_base64)

                                _logger.warning(f"ROW {idx} → URL IMAGE OK")

                    except Exception:
                        _logger.warning(f"ROW {idx} → URL FAILED")

                else:
                    row_text_parts.append(val)

            # -------- EMBEDDED IMAGES --------
            if idx in image_map:
                row_images.extend(image_map[idx])
                _logger.warning(f"ROW {idx} → EMBED IMAGE FOUND")

            row_text = " | ".join(row_text_parts)

            # ✅ FIX: ensure row always meaningful for AI
            if not row_text and row_images:
                row_text = f"Product Row {idx}"
                _logger.warning(f"ROW {idx} HAD NO TEXT → GENERATED PLACEHOLDER")

            # 🔍 DEBUG IMAGE COUNT
            _logger.warning(f"ROW {idx} → IMAGES: {len(row_images)}")

            current_page.append({
                "text": row_text,
                "images": row_images
            })

            # -------- PAGINATION --------
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

        # ---------------- FINAL FORMAT ----------------
        final_pages = []

        for page in pages:

            combined_text = "\n".join([r["text"] for r in page["rows"]])

            # ✅ FIX: KEEP ROW STRUCTURE (DO NOT MERGE)
            combined_images = page["rows"]

            _logger.warning(
                f"PAGE {page['page']} → ROWS: {len(page['rows'])}, IMAGES: {len(combined_images)}"
            )

            final_pages.append({
                "page": page["page"],
                "text": combined_text,
                "images": combined_images
            })

        self.extracted_text = json.dumps(final_pages)

        _logger.warning(f"EXCEL DONE → {len(final_pages)} PAGES")
        

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

        # ✅ FIX 1: batch processing (prevents missing products)
        batch_size = 3

        for i in range(0, len(pages), batch_size):

            batch = pages[i:i + batch_size]

            combined_text = "\n\n".join([
                f"PAGE {p.get('page')}:\n{p.get('text','')}"
                for p in batch if p.get("text", "").strip()
            ])

            if not combined_text.strip():
                continue

            _logger.warning(f"AI → PROCESSING BATCH {i // batch_size + 1}")

            prompt = f"""
            You are a product extraction engine.

            Extract ALL distinct products.

            RULES:
            - Return ONLY valid JSON
            - No explanation
            - No markdown
            - No text outside JSON

            IMPORTANT LOGIC:
            1. If content looks like structured rows (Excel):
            → EACH LINE = ONE product

            2. If catalog grid:
            → extract ALL items

            3. If single product page:
            → extract ONE product

            4. DO NOT merge products
            5. DO NOT skip products

            FORMAT:
            [
            {{
                "name": "",
                "description": "",
                "category": ""
            }}
            ]

            TEXT:
            {combined_text}
            """

            try:
                response = client.responses.create(
                    model="gpt-4.1-mini",
                    input=prompt,
                    timeout=60
                )

                result = response.output_text.strip()

                _logger.warning(f"RAW AI RESPONSE → {result[:200]}")

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
                    _logger.warning("INVALID JSON → SKIPPED")
                    continue

                if isinstance(parsed, list) and parsed:
                    _logger.warning(f"BATCH → {len(parsed)} products extracted")

                    # ✅ IMPORTANT: map batch to FIRST page only (stable mapping)
                    page_products.append({
                        "page": batch[0].get("page"),
                        "products": parsed
                    })

            except Exception as e:
                _logger.warning(f"BATCH FAILED → {str(e)}")
                continue

        # ✅ SAVE AFTER LOOP (CRITICAL)
        self.ai_response = json.dumps(page_products)

        _logger.warning(f"AI TOTAL PAGES STORED: {len(page_products)}")

     #-----------clean image-------------
    def is_clean_product_image(self, img_base64):
        try:
            import base64
            from PIL import Image
            import io

            img_bytes = base64.b64decode(img_base64)
            img = Image.open(io.BytesIO(img_bytes)).convert("RGB")

            width, height = img.size

            # ❌ reject tiny images (logos/icons)
            if width < 200 or height < 200:
                return False

            pixels = list(img.getdata())
            total_pixels = len(pixels)

            # 🔥 detect dominant color (logos usually 1 color)
            color_counts = {}
            for p in pixels[::100]:  # sample pixels (faster)
                color_counts[p] = color_counts.get(p, 0) + 1

            dominant_ratio = max(color_counts.values()) / (total_pixels / 100)

            # ❌ too uniform → likely logo
            if dominant_ratio > 0.6:
                return False

            # 🔥 detect white background ratio
            white_pixels = sum(1 for p in pixels if p[0] > 240 and p[1] > 240 and p[2] > 240)
            white_ratio = white_pixels / total_pixels

            # ✅ prefer clean product shots (white bg)
            if white_ratio > 0.4:
                return True

            # ❌ reject lifestyle/human images
            if width > 1000 and height > 1000:
                return False

            return True

        except Exception:
            return False
     
     #-----------scoring image before picking best/quality image (inage logic)-------------
    _logger.warning(f"PAGE {page_no} IMAGE TYPE → {type(row_data)}")

    if row_data:
        _logger.warning(f"FIRST IMAGE TYPE → {type(row_data[0])}")


    def pick_best_image(self, images):
        import base64

        best_img = None
        best_score = 0

        for img in images:
            try:
                img_bytes = base64.b64decode(img)
                size = len(img_bytes)

                # ❌ skip tiny images (icons, logos)
                if size < 8000:
                    continue

                score = 0

                # ✅ 1. Prefer large images
                score += size / 1000

                # ✅ 2. Penalize overly large (full-page lifestyle)
                if size > 500000:
                    score -= 200

                # ✅ 3. Prefer medium size (typical product image)
                if 20000 < size < 200000:
                    score += 200

                # ✅ 4. Penalize duplicates (same image reused)
                if best_img and img == best_img:
                    score -= 300

                if score > best_score:
                    best_score = score
                    best_img = img

            except Exception:
                continue

        return best_img

    #----------------PRODUCT CREATION ----------------
    def create_product_drafts(self):
        if not self.ai_response or not self.extracted_text:
            return

        import base64

        def is_valid_product_image(img_base64):
            try:
                img_bytes = base64.b64decode(img_base64)
                return len(img_bytes) > 1500
            except Exception:
                return False

        product_obj = self.env['product.template']
        category_obj = self.env['product.category']

        pages = json.loads(self.extracted_text)
        ai_pages = json.loads(self.ai_response)

        _logger.warning("CREATING PRODUCTS WITH PAGE-AWARE MAPPING")
        _logger.warning(f"AI PAGES COUNT: {len(ai_pages)}")

        created_count = 0  # ✅ debug counter

        # ================= LOOP 1 (PAGES) =================
        for page_data in pages:

            page_no = page_data.get("page")

            # ---------------- AI MATCH ----------------
            ai_page = next((p for p in ai_pages if p.get("page") == page_no), None)

            if not ai_page:
                _logger.warning(f"NO AI DATA FOR PAGE {page_no}")
                continue

            products = ai_page.get("products", [])

            if not products:
                _logger.warning(f"NO PRODUCTS FOUND ON PAGE {page_no}")
                continue

            _logger.warning(f"PAGE {page_no} → {len(products)} PRODUCTS")

            # ✅ ONE used_images PER PAGE
            used_images = set()

            # ================= LOOP 2 (PRODUCTS) =================
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

                # ================= DUPLICATE PROTECTION =================
                existing = product_obj.search([('name', '=', name)], limit=1)
                if existing:
                    _logger.warning(f"SKIPPED DUPLICATE → {name}")
                    continue

                # ================= IMAGE LOGIC =================
                row_data = page_data.get("images", [])
                selected_image = None

                if row_data:

                    # ================= EXCEL =================
                    if isinstance(row_data[0], dict):

                        if i < len(row_data):
                            row_images = row_data[i].get("images", [])

                            valid_images = [
                                img for img in row_images
                                if is_valid_product_image(img)
                            ]

                            clean_images = [
                                img for img in valid_images
                                if self.is_clean_product_image(img) and img not in used_images
                            ]

                            if clean_images:
                                selected_image = clean_images[0]
                            else:
                                fallback = [
                                    img for img in valid_images
                                    if img not in used_images
                                ]
                                if fallback:
                                    selected_image = fallback[0]

                    # ================= PDF =================
                    elif isinstance(row_data[0], str):

                        valid_images = [
                            img for img in row_data
                            if is_valid_product_image(img)
                        ]

                        clean_images = [
                            img for img in valid_images
                            if self.is_clean_product_image(img) and img not in used_images
                        ]

                        if i < len(clean_images):
                            selected_image = clean_images[i]
                        else:
                            fallback = [
                                img for img in valid_images
                                if img not in used_images
                            ]
                            if fallback:
                                selected_image = fallback[0]

                # ================= APPLY IMAGE =================
                if selected_image:
                    vals['image_1920'] = selected_image
                    used_images.add(selected_image)
                    _logger.warning(f"IMAGE ASSIGNED (CLEAN FIRST) → {name}")
                else:
                    _logger.warning(f"NO IMAGE → {name}")

                # ================= CREATE PRODUCT =================
                product_obj.create(vals)
                created_count += 1

                _logger.warning(f"CREATED → {name}")
                _logger.warning(f"AI RESPONSE SAMPLE: {self.ai_response[:500]}")

        # ================= FINAL COMMIT (ONLY ONCE) =================
        self.env.cr.commit()
        _logger.warning("DB COMMIT DONE")

        # ================= FINAL LOG =================
        _logger.warning(f"TOTAL PRODUCTS CREATED: {created_count}")
        _logger.warning("PRODUCT CREATION LOOP COMPLETED")
    

    #---------------- CRON ----------------

    def run_pending_jobs(self):

        jobs = self.search([('state', '=', 'draft')])

        _logger.warning(f"CRON → Found {len(jobs)} jobs")

        for job in jobs:
            try:
                _logger.warning(f"CRON → START JOB {job.id}")

                job.state = 'processing'

                job.process_import()

                # ✅ VERY IMPORTANT — mark as done
                job.state = 'done'

                _logger.warning(f"CRON → JOB {job.id} DONE")

            except Exception:
                _logger.exception("CRON FAILED")
                job.state = 'error'
    
    def ping_flask_server(self):
      
        try:
            requests.get("https://pdf-extractor-staging.onrender.com", timeout=10)
            _logger.info("FLASK PING SUCCESS")
        except Exception:
            _logger.warning("FLASK PING FAILED")
