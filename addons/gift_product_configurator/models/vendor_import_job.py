from odoo import models, fields
import base64
import logging
import io
import requests
import pandas as pd

from io import BytesIO
from openpyxl import load_workbook
from openpyxl_image_loader import SheetImageLoader
from PIL import Image
import time
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin


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
        ('error', 'Error'),
         ('failed', 'Failed'),
    ], default='draft')

    #---------image processing-------------------

    def is_clean_pdf_image(img_base64):
        try:
            import base64
            from PIL import Image
            import io

            img_bytes = base64.b64decode(img_base64)
            img = Image.open(io.BytesIO(img_bytes))

            width, height = img.size

            # ❌ reject tiny (logos/icons)
            if width < 200 or height < 200:
                return False

            # ❌ reject extreme shapes (banners / strips)
            ratio = width / float(height)
            if ratio > 2.2 or ratio < 0.5:
                return False

            # ❌ reject complex scenes (likely humans/background)
            colors = img.convert("RGB").getcolors(maxcolors=1000000)
            if colors and len(colors) > 4000:
                return False

            # ❌ reject overly wide images (catalog layouts)
            if width > 1200:
                return False

            return True

        except Exception:
            return False

    #------excel processing methof---------------

    def parse_excel(self):
        _logger.warning("EXCEL → START PARSING")

        excel_bytes = base64.b64decode(self.excel_file)

        wb = load_workbook(filename=BytesIO(excel_bytes))
        sheet = wb.active

        image_loader = SheetImageLoader(sheet)

        headers = {
            "User-Agent": "Mozilla/5.0",
        }

        pages = []
        current_page = []
        page_number = 1
        page_size = 20

        for idx, row in enumerate(sheet.iter_rows()):

            _logger.warning(f"ROW {idx} PROCESSING")

            row_text_parts = []
            row_images = []

            # -------- TEXT --------
            for cell in row:
                val = str(cell.value or "").strip()
                if val:
                    row_text_parts.append(val)

            row_text = " ".join(row_text_parts).strip()

            if not row_text:
                _logger.warning(f"ROW {idx} EMPTY → SKIPPED")
                continue

            # -------- 1️⃣ TRY EMBEDDED IMAGE --------
            for cell in row:
                try:
                    if image_loader.image_in(cell.coordinate):

                        pil_img = image_loader.get(cell.coordinate)

                        buffer = BytesIO()
                        pil_img.save(buffer, format="JPEG")

                        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

                        row_images.append(img_base64)

                        _logger.warning(f"ROW {idx} → EMBED IMAGE USED")
                        break

                except Exception:
                    continue

            # -------- 2️⃣ TRY URL SCRAPING --------
            if not row_images:

                for cell in row:
                    val = str(cell.value or "").strip()

                    if val.startswith("http"):

                        try:
                            response = requests.get(val, headers=headers, timeout=10)

                            if response.status_code != 200:
                                continue

                            content_type = response.headers.get("Content-Type", "")

                            # DIRECT IMAGE
                            if "image" in content_type:

                                if len(response.content) > 5000:
                                    img_base64 = base64.b64encode(response.content).decode("utf-8")
                                    row_images.append(img_base64)

                                    _logger.warning(f"ROW {idx} → DIRECT IMAGE URL")
                                    break

                            # HTML PAGE → SCRAPE IMAGE
                            elif "text/html" in content_type:

                                soup = BeautifulSoup(response.text, "html.parser")

                                best_img = None

                                # 🔥 PRIORITY: PRODUCT IMAGES
                                for img in soup.find_all("img"):

                                    src = img.get("src")
                                    if not src:
                                        continue

                                    if src.startswith("/"):
                                        src = urljoin(val, src)

                                    if any(k in src.lower() for k in ["product", "large", "main"]):

                                        try:
                                            img_res = requests.get(src, headers=headers, timeout=5)

                                            if img_res.status_code == 200 and len(img_res.content) > 10000:
                                                best_img = img_res.content
                                                break

                                        except Exception:
                                            continue

                                # 🔥 FALLBACK: ANY VALID IMAGE
                                if not best_img:
                                    for img in soup.find_all("img"):

                                        src = img.get("src")
                                        if not src:
                                            continue

                                        if src.startswith("/"):
                                            src = urljoin(val, src)

                                        try:
                                            img_res = requests.get(src, headers=headers, timeout=5)

                                            if img_res.status_code == 200 and len(img_res.content) > 10000:
                                                best_img = img_res.content
                                                break

                                        except Exception:
                                            continue

                                if best_img:
                                    img_base64 = base64.b64encode(best_img).decode("utf-8")
                                    row_images.append(img_base64)

                                    _logger.warning(f"ROW {idx} → SCRAPED IMAGE")
                                    break

                        except Exception:
                            _logger.warning(f"ROW {idx} → URL FAILED")

            # -------- FINAL DEBUG --------
            _logger.warning(f"ROW {idx} → TEXT LENGTH: {len(row_text)}")
            _logger.warning(f"ROW {idx} → IMAGES FOUND: {len(row_images)}")

            # -------- STORE ROW --------
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

        # -------- LAST PAGE --------
        if current_page:
            pages.append({
                "page": page_number,
                "rows": current_page
            })

        # -------- FINAL STRUCTURE --------
        final_pages = []

        for page in pages:

            combined_text = "\n".join([r["text"] for r in page["rows"]])

            final_pages.append({
                "page": page["page"],
                "text": combined_text,
                "images": page["rows"]
            })

            _logger.warning(f"PAGE {page['page']} → ROWS: {len(page['rows'])}")

        self.extracted_text = json.dumps(final_pages)

        _logger.warning(f"EXCEL DONE → {len(final_pages)} PAGES")

    #---------------- MAIN FLOW ----------------

    def process_import(self):

        _logger.warning(f"PROCESS START → Job {self.id}")

        # ✅ DEBUG (keep temporarily)
        _logger.warning(f"AVAILABLE FIELDS → {list(self._fields.keys())}")

        try:

            # ---------------- FILE TYPE ----------------
            if self.excel_file:
                _logger.warning("STEP → Parsing Excel")
                self.parse_excel()

            elif self.pdf_file:
                _logger.warning("STEP → Extracting PDF")
                self.extract_pdf()

            else:
                raise Exception("No file found (excel/pdf missing)")

            # ---------------- VALIDATION ----------------
            if not self.extracted_text:
                _logger.error("NO TEXT EXTRACTED → STOPPING")
                return

            _logger.warning(f"EXTRACTED TEXT SAMPLE → {self.extracted_text[:200]}")

            # ---------------- AI ----------------
            _logger.warning("STEP → Sending to OpenAI")
            self.send_to_openai()

            if not self.ai_response:
                _logger.error("NO AI RESPONSE → STOPPING")
                return

            # ---------------- CREATE ----------------
            _logger.warning("STEP → Creating products")
            self.create_product_drafts()

            self.state = "done"

        except Exception as e:
            _logger.error(f"PROCESS FAILED → {str(e)}")
            self.state = "failed"

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
            You are an advanced product extraction and interpretation engine for catalog PDFs.

            Your job is to extract ALL products on this page AND understand how images relate to products.

            =====================
            CORE RULES (STRICT)
            =====================

            1. RETURN ONLY VALID JSON
            2. NO explanations
            3. NO markdown
            4. NO text outside JSON
            5. DO NOT duplicate products
            6. DO NOT skip any product
            7. EACH product must appear exactly once

            =====================
            PRODUCT DETECTION LOGIC
            =====================

            A page may contain:

            (A) ONE large product (hero layout)
            (B) MULTIPLE products (grid/catalog layout)
            (C) MIX of large + small supporting products

            You MUST:

            - If SINGLE main product:
            → return ONE product

            - If MULTIPLE products (grid/list/table):
            → return EACH product separately

            - If variants (same product different colors):
            → treat as SEPARATE products ONLY if clearly labeled differently

            =====================
            IMAGE UNDERSTANDING LOGIC (CRITICAL)
            =====================

            Each product may have multiple images on the page.

            You MUST decide the BEST image for each product using these rules:

            PRIORITY ORDER:

            1. CLEAN PRODUCT IMAGE (BEST)
            - Plain background
            - Centered object
            - No human interaction

            2. PRODUCT-FOCUSED IMAGE
            - Product clearly dominant
            - May include minor props

            3. LIFESTYLE IMAGE (USE ONLY IF NECESSARY)
            - Human holding/wearing product
            - ONLY if:
                - product is clearly visible
                - no better clean image exists

            4. NEVER USE:
            - Logos
            - Icons
            - Decorative graphics
            - Background textures
            - Cropped fragments
            - Zoomed partial product

            =====================
            IMPORTANT VISUAL INTERPRETATION
            =====================

            When multiple images exist for same product:

            → Compare ALL images
            → Choose the MOST REPRESENTATIVE one

            Examples:

            - Backpack page:
            - Ignore person wearing bag ❌
            - Prefer isolated product image ✅

            - Pen grid:
            - Extract EACH pen model
            - Use closest matching image per pen

            - Product + detail thumbnails:
            - Use main product image, NOT thumbnails

            =====================
            OUTPUT FORMAT
            =====================

            [
            {{
                "name": "",
                "description": "",
                "category": ""
            }}
            ]

            =====================
            TEXT TO ANALYZE
            =====================

            {text}
            """

            try:
                response = client.responses.create(
                    model="gpt-4.1-mini",
                    input=prompt,
                    timeout=60
                )
                time.sleep(1)
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
                    for p in batch:
                        page_products.append({
                            "page": p.get("page"),
                            "products": parsed
                        })

            except Exception as e:
                _logger.warning(f"BATCH FAILED → {str(e)}")
                continue

        #✅ SAVE AFTER LOOP (CRITICAL)
        self.ai_response = json.dumps(page_products)

        _logger.warning(f"AI TOTAL PAGES STORED: {len(page_products)}")

     #-----------clean image-------------
     
     #-----------scoring image before picking best/quality image (inage logic)-------------

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

        def is_valid_product_image(img_base64):
            return True

        if not self.ai_response or not self.extracted_text:
            return

        product_obj = self.env['product.template']
        category_obj = self.env['product.category']

        pages = json.loads(self.extracted_text)
        ai_pages = json.loads(self.ai_response)

        _logger.warning("CREATING PRODUCTS WITH PAGE-AWARE MAPPING")
        _logger.warning(f"AI PAGES COUNT: {len(ai_pages)}")

        created_count = 0

        # ================= LOOP 1 (PAGES) =================
        for page_data in pages:

            page_no = page_data.get("page")

            ai_page = next((p for p in ai_pages if p.get("page") == page_no), None)

            if not ai_page:
                _logger.warning(f"NO AI DATA FOR PAGE {page_no}")
                continue

            products = ai_page.get("products", [])

            if not products:
                _logger.warning(f"NO PRODUCTS FOUND ON PAGE {page_no}")
                continue

            _logger.warning(f"PAGE {page_no} → {len(products)} PRODUCTS")

            used_images = set()

            # ================= LOOP 2 (PRODUCTS) =================
            for i, product in enumerate(products):

                _logger.warning(f"---- PRODUCT LOOP START → INDEX {i} ----")

                name = product.get("name")
                _logger.warning(f"PRODUCT {i} → {name}")

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

                # ================= IMAGE ENGINE (FIXED) =================
                row_data = page_data.get("images", [])
                selected_image = None

                if row_data:

                    # ================= PDF MODE (STRICT + PAGE LOCK) =================
                    
                    if isinstance(row_data, list) and row_data and isinstance(row_data[0], str):

                        _logger.warning(f"PDF IMAGE MODE → {len(row_data)} images")

                        # ✅ STEP 1: filter ONLY clean product images
                        clean_images = [
                            img for img in row_data
                            if is_clean_pdf_image(img)
                        ]

                        _logger.warning(f"PDF CLEAN IMAGES → {len(clean_images)}")

                        # ✅ STEP 2: remove already used (avoid duplication)
                        available = [img for img in clean_images if img not in used_images]

                        # ✅ STEP 3: strict sequential mapping per page
                        if available:
                            selected_image = available[0]
                            _logger.warning("PDF IMAGE SELECTED → CLEAN UNUSED")

                        else:
                            _logger.warning("PDF → NO CLEAN UNUSED IMAGES")

                            # 🔥 fallback: still avoid reuse if possible
                            fallback = [img for img in row_data if img not in used_images]

                            if fallback:
                                selected_image = fallback[0]
                                _logger.warning("PDF FALLBACK IMAGE USED")

                    # ================= EXCEL MODE (FIXED HERE) =================
                    elif isinstance(row_data, list) and row_data and isinstance(row_data[0], dict):

                        total_rows = len(row_data)

                        _logger.warning(f"EXCEL IMAGE MODE → {total_rows} rows")

                        # ✅ CYCLIC INDEX (KEY FIX)
                        row_index = i % total_rows
                        row_images = row_data[row_index].get("images", [])

                        _logger.warning(f"EXCEL → USING ROW INDEX {row_index} FOR PRODUCT INDEX {i}")

                        valid_images = [img for img in row_images if is_valid_product_image(img)]

                        if valid_images:
                            selected_image = valid_images[0]
                            _logger.warning(f"EXCEL IMAGE SELECTED → ROW {row_index}")
                        else:
                            _logger.warning(f"EXCEL → NO VALID IMAGE AT ROW {row_index}")

                # ================= APPLY IMAGE =================
                if selected_image:
                    vals['image_1920'] = selected_image
                    used_images.add(selected_image)
                    _logger.warning(f"IMAGE ASSIGNED → {name}")
                else:
                    _logger.warning(f"NO IMAGE → {name}")

                # ================= CREATE PRODUCT =================
                product_obj.create(vals)
                created_count += 1

                _logger.warning(f"CREATED → {name}")

            _logger.warning(f"PAGE {page_no} DONE")

        # ================= FINAL COMMIT =================
        self.env.cr.commit()
        _logger.warning("DB COMMIT DONE")

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

    #def create_product_drafts(self):
