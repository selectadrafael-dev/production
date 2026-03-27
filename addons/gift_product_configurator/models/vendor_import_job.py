from odoo import models, fields
import base64
import logging
import io
import requests
import pandas as pd
from io import BytesIO
from openpyxl import load_workbook
from openpyxl_image_loader import SheetImageLoader
from playwright.sync_api import sync_playwright
from PIL import Image
import time
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from openai import OpenAI
import re

 

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

    
    #------------parse url----------------------------
    def parse_url(self):

        _logger.warning(f"URL PARSE START → {self.data_url}")

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/html",
        }

        # ================= FETCH HTML =================
        try:
            response = requests.get(self.data_url, headers=headers, timeout=20)

            if response.status_code != 200:
                raise Exception("Failed to fetch URL")

            html = response.text

        except Exception as e:
            _logger.error(f"URL FETCH FAILED → {str(e)}")
            return

        products = []

        # ================= API DETECTION =================
        api_urls = []

        api_urls += re.findall(r'https://[^"]*api[^"]*', html)
        api_urls += re.findall(r'https://[^"]*\.json', html)

        _logger.warning(f"API CANDIDATES FOUND → {len(api_urls)}")

        # ================= TRY API =================
        for api_url in api_urls[:5]:

            try:
                _logger.warning(f"TRY API → {api_url}")

                res = requests.get(api_url, headers=headers, timeout=15)

                if res.status_code != 200:
                    continue

                data = res.json()

                def extract(obj):
                    if isinstance(obj, dict):

                        name = (
                            obj.get("name")
                            or obj.get("title")
                            or obj.get("productName")
                        )

                        image = (
                            obj.get("image")
                            or obj.get("image_url")
                            or obj.get("thumbnail")
                        )

                        if name:
                            products.append({
                                "name": name,
                                "image": image
                            })

                        for v in obj.values():
                            extract(v)

                    elif isinstance(obj, list):
                        for i in obj:
                            extract(i)

                extract(data)

                if products:
                    _logger.warning(f"API SUCCESS → {len(products)} PRODUCTS")
                    break

            except Exception as e:
                _logger.warning(f"API FAILED → {str(e)}")

        # ================= HTML FALLBACK =================
        if not products:

            _logger.warning("API FAILED → TRY HTML")

            soup = BeautifulSoup(html, "html.parser")

            items = soup.select("""
                a[href*="/product"],
                .product-card,
                .product-item,
                .card
            """)

            _logger.warning(f"HTML ITEMS FOUND → {len(items)}")

            for item in items:

                text = item.get_text(strip=True)

                if not text or len(text) < 5:
                    continue

                img_tag = item.select_one("img")
                img_url = img_tag.get("src") if img_tag else None

                if img_url and img_url.startswith("//"):
                    img_url = "https:" + img_url

                products.append({
                    "name": text,
                    "image": img_url
                })

        # ================= PLAYWRIGHT FALLBACK =================
        if not products:

            _logger.warning("HTML FAILED → USING PLAYWRIGHT")

            self.scrape_with_playwright()
            return

        # ================= CLEAN =================
        clean_products = [
            p for p in products
            if p.get("name") and len(p.get("name")) > 3
        ]

        _logger.warning(f"CLEAN PRODUCTS → {len(clean_products)}")

        if not clean_products:
            _logger.error("NO VALID PRODUCTS FROM URL")
            return

        # ================= IMAGE DOWNLOAD =================
        def image_to_base64(url):
            try:
                res = requests.get(url, timeout=10)
                if res.status_code == 200:
                    return base64.b64encode(res.content).decode("utf-8")
            except:
                pass
            return None

        final_products = []

        for p in clean_products[:50]:

            img_b64 = image_to_base64(p.get("image")) if p.get("image") else None

            final_products.append({
                "name": p.get("name"),
                "image": img_b64
            })

        pages = [{
            "page": 1,
            "text": "\n".join([p["name"] for p in final_products]),
            "images": [p["image"] for p in final_products if p["image"]]
        }]

        self.extracted_text = json.dumps(pages)

        _logger.warning(f"URL PARSE DONE → {len(final_products)} PRODUCTS")

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

            # -------- 1️⃣ EMBEDDED IMAGE --------
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

            # -------- 2️⃣ URL IMAGE --------
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

                            # HTML PAGE
                            elif "text/html" in content_type:

                                soup = BeautifulSoup(response.text, "html.parser")

                                best_img = None

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

            # -------- DEBUG --------
            _logger.warning(f"ROW {idx} → TEXT LENGTH: {len(row_text)}")
            _logger.warning(f"ROW {idx} → IMAGES FOUND: {len(row_images)}")

            # -------- STORE --------
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

        # -------- FINAL FORMAT --------
        final_pages = []

        for page in pages:

            combined_text = "\n".join([r["text"] for r in page["rows"]])

            final_pages.append({
                "page": page["page"],
                "text": combined_text,
                "images": page["rows"]
            })

        self.extracted_text = json.dumps(final_pages)

        _logger.warning(f"EXCEL DONE → {len(final_pages)} PAGES")

    #---------------- MAIN FLOW ----------------

    def process_import(self):

        _logger.warning(f"PROCESS START → Job {self.id}")

        # ✅ DEBUG (keep temporarily)
        _logger.warning(f"AVAILABLE FIELDS → {list(self._fields.keys())}")

        try:

            # ================= INPUT ROUTING =================

            # ✅ PRIORITY 1: URL
            if self.data_url:
                _logger.warning("STEP → Parsing URL")
                self.parse_url()

            # ✅ PRIORITY 2: Excel
            elif self.excel_file:
                _logger.warning("STEP → Parsing Excel")
                self.parse_excel()

            # ✅ PRIORITY 3: PDF
            elif self.pdf_file:
                _logger.warning("STEP → Extracting PDF")
                self.extract_pdf()

            else:
                raise Exception("No input found (URL / Excel / PDF missing)")

            # ================= VALIDATION =================
            if not self.extracted_text:
                _logger.error("NO TEXT EXTRACTED → STOPPING")
                return

            _logger.warning(f"EXTRACTED TEXT SAMPLE → {self.extracted_text[:200]}")

            # ================= AI =================
            _logger.warning("STEP → Sending to OpenAI")
            self.send_to_openai()

            if not self.ai_response:
                _logger.error("NO AI RESPONSE → STOPPING")
                return

            # ================= CREATE =================
            _logger.warning("STEP → Creating products")
            self.create_product_drafts()

            self.state = "done"

        except Exception as e:
            _logger.error(f"PROCESS FAILED → {str(e)}")
            self.state = "failed"

    # ---------------- PDF ----------------

    def extract_pdf(self):

        _logger.warning("PDF → START EXTRACTION")

        pdf_bytes = base64.b64decode(self.pdf_file)

        MAX_RETRIES = 2
        success = False

        for attempt in range(MAX_RETRIES):

            try:
                _logger.warning(f"FLASK CALL ATTEMPT {attempt + 1}")

                response = requests.post(
                    "https://pdf-extractor-staging.onrender.com/extract",
                    files={"file": ("catalog.pdf", pdf_bytes, "application/pdf")},
                    timeout=180
                )

                if response.status_code != 200:
                    _logger.warning(f"FLASK ERROR: {response.status_code}")
                    continue

                pages = response.json()

                # ================= VALIDATION =================
                if not isinstance(pages, list) or not pages:
                    _logger.error("INVALID FLASK RESPONSE → EMPTY OR WRONG FORMAT")
                    continue

                _logger.warning(f"RECEIVED {len(pages)} PAGES FROM FLASK")

                # ================= NORMALIZATION =================
                normalized_pages = []

                for page in pages:

                    text = page.get("text", "")
                    images = page.get("images", [])

                    if not text and not images:
                        continue

                    normalized_pages.append({
                        "page": page.get("page"),
                        "text": text,
                        "images": images
                    })

                if not normalized_pages:
                    _logger.error("NO VALID PAGES AFTER NORMALIZATION")
                    continue

                # ================= STORE =================
                self.extracted_text = json.dumps(normalized_pages)

                _logger.warning(
                    f"PDF EXTRACTED SAMPLE → {self.extracted_text[:200]}"
                )

                success = True
                break

            except Exception as e:
                _logger.exception(f"FLASK CALL FAILED → {str(e)}")

            time.sleep(5)

        # ================= FINAL STATUS =================
        if not success:
            _logger.error("PDF EXTRACTION FAILED AFTER RETRIES")
            self.state = "failed"

    # ---------------- OPENAI ----------------

    def send_to_openai(self):

        self.state = "ai_processing"

        api_key = self.env['ir.config_parameter'].sudo().get_param('openai.api.key')

        if not api_key:
            raise Exception("OpenAI API key not configured")

        client = OpenAI(api_key=api_key)

        try:
            pages = json.loads(self.extracted_text or "[]")
        except Exception:
            _logger.error("INVALID extracted_text JSON")
            return

        if not pages:
            _logger.error("NO PAGES TO PROCESS")
            return

        # ================= BATCHING =================
        BATCH_SIZE = 5

        batched_pages = [
            pages[i:i + BATCH_SIZE]
            for i in range(0, len(pages), BATCH_SIZE)
        ]

        _logger.warning(f"TOTAL BATCHES → {len(batched_pages)}")

        page_products = []

        # ================= LOOP =================
        for batch_index, batch in enumerate(batched_pages):

            _logger.warning(f"AI → PROCESSING BATCH {batch_index + 1}")

            combined_text = "\n\n".join([
                p.get("text", "") for p in batch if p.get("text")
            ])

            if not combined_text.strip():
                _logger.warning("EMPTY TEXT → SKIP BATCH")
                continue

            prompt = f"""
            You are an advanced product extraction and interpretation engine for catalog PDFs.

            =====================
            CORE RULES (STRICT)
            =====================

            1. RETURN ONLY VALID JSON
            2. NO explanation
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

            - If MULTIPLE products:
            → extract EACH product separately

            - If repeated items:
            → treat EACH visible item as a unique product

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

            {combined_text}
            """

            MAX_RETRIES = 3
            success = False

            for attempt in range(MAX_RETRIES):
                try:
                    response = client.responses.create(
                        model="gpt-4.1-mini",
                        input=prompt,
                        timeout=60
                    )

                    result = response.output_text.strip()
                    success = True
                    break

                except Exception as e:
                    _logger.warning(f"RETRY {attempt+1} FAILED → {str(e)}")

            if not success:
                _logger.error("FINAL FAILURE → SKIP BATCH")
                continue

            # ================= CLEAN RESPONSE =================
            if "```" in result:
                result = result.split("```")[1]

            if result.lower().startswith("json"):
                result = result[4:]

            result = result.strip()

            try:
                parsed = json.loads(result)
            except Exception:
                _logger.warning("INVALID JSON → SKIP BATCH")
                continue

            if isinstance(parsed, list) and parsed:

                for page in batch:

                    page_products.append({
                        "page": page.get("page"),
                        "products": parsed
                    })

                _logger.warning(f"BATCH PRODUCTS → {len(parsed)}")

            import time
            time.sleep(1)

        # ================= FINAL =================
        self.ai_response = json.dumps(page_products)

        _logger.warning(f"AI TOTAL PAGES STORED: {len(page_products)}")

       #self.state = "ai_done"

    #-----------scoring image before picking best/quality image (inage logic)-------------

    def pick_best_image(self, images):

        best_img = None
        best_score = 0
        seen_hashes = set()

        for img in images:

            try:
                img_bytes = base64.b64decode(img)
                size = len(img_bytes)

                # ❌ Skip tiny images (logos/icons)
                if size < 10000:
                    continue

                # ❌ Skip extremely large (full lifestyle pages)
                if size > 800000:
                    continue

                # ================= IMAGE ANALYSIS =================
                pil_img = Image.open(BytesIO(img_bytes))
                width, height = pil_img.size

                # ❌ Skip extremely small resolution
                if width < 150 or height < 150:
                    continue

                # ❌ Skip extreme aspect ratios (banners, strips)
                aspect_ratio = width / height if height else 1

                if aspect_ratio > 3 or aspect_ratio < 0.3:
                    continue

                # ================= DUPLICATE CHECK =================
                img_hash = hash(img_bytes[:100])  # fast partial hash

                if img_hash in seen_hashes:
                    continue

                seen_hashes.add(img_hash)

                # ================= SCORING =================
                score = 0

                # ✅ Prefer medium-good sizes
                if 20000 < size < 300000:
                    score += 200

                # ✅ Prefer square-ish product images
                if 0.7 < aspect_ratio < 1.5:
                    score += 150

                # ✅ Prefer decent resolution
                if width > 400 and height > 400:
                    score += 150

                # ❌ Penalize too wide/tall
                if aspect_ratio > 2 or aspect_ratio < 0.5:
                    score -= 100

                # ❌ Penalize very large images (likely lifestyle)
                if size > 500000:
                    score -= 150

                # Base size contribution
                score += size / 2000

                # ================= SELECT BEST =================
                if score > best_score:
                    best_score = score
                    best_img = img

            except Exception:
                continue

        return best_img


    #----marchin AI-----------------------------------
    def match_image_with_ai(self, product_name, images):

        api_key = self.env['ir.config_parameter'].sudo().get_param('openai.api.key')
        client = OpenAI(api_key=api_key)

        if not images:
            return None

        # limit images for performance
        images = images[:5]
        image_inputs = [
        {
                "type": "input_image",
                "image_url": f"data:image/jpeg;base64,{img}"
            }
            for img in images
        ]

        prompt = f"""
        You are an expert product image matcher.

        Select the image that BEST represents this product:

        PRODUCT:
        {product_name}

        RULES:
        - Return ONLY the index (0-based integer)
        - No explanation
        - No text

        PRIORITY:
        1. Clean product image (plain background)
        2. Product centered and clearly visible
        3. No human interaction preferred
        4. If only lifestyle images exist, choose the clearest one

        DO NOT PICK:
        - logos
        - icons
        - background-only images
        - cropped fragments
        """

        try:
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=[{
                    "role": "user",
                    "content": [{"type": "input_text", "text": prompt}] + image_inputs
                }],
                timeout=30
            )

            result = response.output_text.strip()

            index = int(result)

            if 0 <= index < len(images):
                return images[index]

        except Exception as e:
            _logger.warning(f"AI IMAGE MATCH FAILED → {str(e)}")

        return None

    #----------------PRODUCT CREATION ----------------

    def create_product_drafts(self):

        def is_valid_product_image(img_base64):
            return True  # keep Excel safe

        if not self.ai_response or not self.extracted_text:
            _logger.warning("NO AI OR EXTRACTED DATA → STOP")
            return

        product_obj = self.env['product.template']
        category_obj = self.env['product.category']

        try:
            pages = json.loads(self.extracted_text)
            ai_pages = json.loads(self.ai_response)
        except Exception:
            _logger.error("INVALID JSON → STOP")
            return

        _logger.warning("CREATING PRODUCTS WITH PAGE-AWARE MAPPING")
        _logger.warning(f"AI PAGES COUNT: {len(ai_pages)}")

        created_count = 0

        # ✅ GLOBAL CACHE (VERY IMPORTANT)
        used_images = set()
        image_cache = {}

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

            # ================= LOOP 2 (PRODUCTS) =================
            for i, product in enumerate(products):

                name = product.get("name")

                if not name:
                    _logger.warning("SKIPPING EMPTY PRODUCT")
                    continue

                description = product.get("description", "")
                category_name = product.get("category") or "Uncategorized"

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

                # ================= IMAGE ENGINE =================
                row_data = page_data.get("images", [])
                selected_image = None

                if row_data:

                    # ================= PDF MODE =================
                    if isinstance(row_data, list) and row_data and isinstance(row_data[0], str):

                        available_images = [img for img in row_data if img not in used_images]

                        _logger.warning(f"PDF IMAGE MODE → {len(available_images)} usable images")

                        if available_images:

                            if len(available_images) == 1:
                                selected_image = available_images[0]

                            else:
                                if name in image_cache:
                                    selected_image = image_cache[name]
                                    _logger.warning(f"CACHE HIT → {name}")

                                else:
                                    selected_image = self.match_image_with_ai(name, available_images)

                                    if selected_image:
                                        image_cache[name] = selected_image
                                        _logger.warning("AI MATCHED IMAGE SUCCESS")
                                    else:
                                        selected_image = available_images[0]
                                        _logger.warning("AI FALLBACK USED")

                    # ================= EXCEL MODE =================
                    elif isinstance(row_data, list) and row_data and isinstance(row_data[0], dict):

                        total_rows = len(row_data)

                        row_index = i % total_rows
                        row_images = row_data[row_index].get("images", [])

                        valid_images = [img for img in row_images if is_valid_product_image(img)]

                        if valid_images:
                            selected_image = valid_images[0]
                            _logger.warning(f"EXCEL IMAGE SELECTED → ROW {row_index}")

                # ================= APPLY IMAGE =================
                if selected_image:
                    vals['image_1920'] = selected_image
                    used_images.add(selected_image)
                    _logger.warning(f"IMAGE ASSIGNED → {name}")
                else:
                    _logger.warning(f"NO IMAGE → {name}")

                # ================= CREATE =================
                product_obj.create(vals)
                created_count += 1

                # ✅ COMMIT EVERY 50 PRODUCTS (VERY IMPORTANT)
                if created_count % 50 == 0:
                    self.env.cr.commit()
                    _logger.warning(f"PARTIAL COMMIT → {created_count}")

            _logger.warning(f"PAGE {page_no} DONE")

        # ================= FINAL COMMIT =================
        self.env.cr.commit()

        _logger.warning(f"TOTAL PRODUCTS CREATED: {created_count}")
        _logger.warning("PRODUCT CREATION LOOP COMPLETED")

    #-----URL API FLOW-------------------------------------------

    def scrape_with_playwright(self):

        _logger.warning(f"PLAYWRIGHT SCRAPE → {self.data_url}")

        products = []

        with sync_playwright() as p:

            #browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # 🔥 Go to page
            page.goto(self.data_url, timeout=60000)

            # 🔥 Wait for content to load
            page.wait_for_timeout(5000)

            # 🔥 Handle cookie popup (auto-click common buttons)
            try:
                page.locator("button:has-text('Accept')").click(timeout=3000)
            except:
                pass

            html = page.content()

            # 🔥 Extract product cards
            items = page.query_selector_all("a, div")

            _logger.warning(f"PLAYWRIGHT ELEMENTS FOUND → {len(items)}")

            for item in items[:200]:  # limit for safety

                try:
                    text = item.inner_text().strip()

                    if not text or len(text) < 5:
                        continue

                    img_el = item.query_selector("img")
                    img_url = img_el.get_attribute("src") if img_el else None

                    if img_url and img_url.startswith("//"):
                        img_url = "https:" + img_url

                    # 🔥 Convert image to base64
                    img_base64 = None

                    if img_url:
                        try:
                            import requests
                            res = requests.get(img_url, timeout=10)
                            if res.status_code == 200:
                                img_base64 = base64.b64encode(res.content).decode("utf-8")
                        except:
                            pass

                    products.append({
                        "name": text[:120],
                        "image": img_base64
                    })

                except:
                    continue

            browser.close()

        _logger.warning(f"PLAYWRIGHT PRODUCTS → {len(products)}")

        if not products:
            _logger.error("PLAYWRIGHT FAILED → NO PRODUCTS")
            return

        pages = [{
            "page": 1,
            "text": "\n".join([p["name"] for p in products]),
            "images": [p["image"] for p in products if p["image"]]
        }]

        self.extracted_text = json.dumps(pages)

        _logger.warning(f"PLAYWRIGHT DONE → {len(products)} PRODUCTS")

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


