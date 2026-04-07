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
from openai import OpenAI
import re
import fitz

 

_logger = logging.getLogger(__name__)


class VendorImportJob(models.Model):

    _name = "vendor.import.job"
    _description = "Vendor Import Job"

    name = fields.Char(default="Vendor Data Import")

    data_url = fields.Char()
    #data_url = fields.Char(string="Vendor URL")
    extra_info = fields.Text()

    pdf_file = fields.Binary()
    excel_file = fields.Binary()
    logo_file = fields.Binary()

    extracted_text = fields.Text()
    current_page = fields.Integer(
        string="Current PDF Page",
        default=0
    )
    total_pages = fields.Integer(string="Total Pages", default=0)
    last_ai_page = fields.Integer(string="Last AI Page", default=0)
    ai_response = fields.Text()
    priority = fields.Integer(default=10)

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

        _logger.warning(f"APIFY SCRAPE → {self.data_url}")

        raw_data = self._run_apify_actor(self.data_url)
        _logger.warning(f"RAW APIFY DATA SAMPLE → {str(raw_data)[:300]}")

        if not raw_data:
            _logger.error("APIFY FAILED → NO DATA")
            return

        structured_data = self._normalize_url_data(raw_data)

        if not structured_data:
            _logger.error("NORMALIZATION FAILED → EMPTY DATA")
            return

        # ✅ Convert to same format used by Excel/PDF
        self.extracted_text = json.dumps(structured_data)

        _logger.warning(f"APIFY DONE → {len(structured_data)} ITEMS")
      


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

            #-------- DEBUG --------
            _logger.warning(f"ROW {idx} → TEXT LENGTH: {len(row_text)}")
            _logger.warning(f"ROW {idx} → IMAGES FOUND: {len(row_images)}")

            #-------- STORE --------
            current_page.append({
                "text": row_text,
                "images": row_images
            })

            #-------- PAGINATION --------
            if len(current_page) >= page_size:
                pages.append({
                    "page": page_number,
                    "rows": current_page
                })
                current_page = []
                page_number += 1

        #-------- LAST PAGE --------
        if current_page:
            pages.append({
                "page": page_number,
                "rows": current_page
            })

        #-------- FINAL FORMAT --------
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

        try:

            #================= URL FLOW =================
            if self.data_url:
                _logger.warning("FLOW → URL")

                self.parse_url()

                if not self.extracted_text:
                    _logger.error("URL PARSE FAILED")
                    return

                self.send_to_openai_url()

                if not self.ai_response:
                    _logger.error("URL AI FAILED")
                    return

                self.create_products_url()

            # ================= EXCEL FLOW =================
            elif self.excel_file:
                _logger.warning("FLOW → EXCEL")

                self.parse_excel()
                self.send_to_openai_pdf_excel()
                self.create_products_pdf_excel()

            # ================= PDF FLOW =================
            elif self.pdf_file:
                _logger.warning("FLOW → PDF")

                self.extract_pdf()
                self.send_to_openai_pdf_excel()
                self.create_products_pdf_excel()

            else:
                raise Exception("No input found")

            # ONLY mark done if FULL PDF processed
            if self.current_page >= self.total_pages:
                _logger.warning("PROCESS IMPORT → ALL PAGES COMPLETED")
                self.state = 'done'
            else:
                _logger.warning("PROCESS IMPORT → WAITING FOR NEXT BATCH")
                self.state = 'processing'

        except Exception as e:
            _logger.error(f"PROCESS FAILED → {str(e)}")
            self.state = "failed"

   
    # ---------------- PDF ----------------

    def extract_pdf(self):

        _logger.warning("PDF → START EXTRACTION (BATCH MODE)")
        pdf_bytes = base64.b64decode(self.pdf_file)

        MAX_RETRIES = 3

        # 🔥 BATCH CONFIG
        BATCH_SIZE = 3
        PAGE_DELAY = 2
        BATCH_DELAY = 5

        all_pages = []

        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        except Exception as e:
            _logger.exception(f"PDF OPEN FAILED → {str(e)}")
            self.state = "failed"
            return

        total_pages = len(doc)
        self.total_pages = total_pages

        # 🔥 RESUME LOG (NEW)
        _logger.warning(f"RESUMING FROM PAGE → {self.current_page or 0}")

        start_page = self.current_page or 0
        end_page = min(start_page + BATCH_SIZE, total_pages)

        _logger.warning(f"PDF TOTAL PAGES → {total_pages}")
        _logger.warning(f"BATCH → Processing pages {start_page+1} to {end_page}")

        for i in range(start_page, end_page):

            page = doc[i]
            _logger.warning(f"PROCESSING PAGE {i + 1}")

            # ================= CREATE SINGLE PAGE PDF =================
            try:
                single_pdf = fitz.open()
                single_pdf.insert_pdf(doc, from_page=i, to_page=i)

                pdf_bytes_io = io.BytesIO()
                single_pdf.save(pdf_bytes_io)
                pdf_bytes_io.seek(0)

            except Exception as e:
                _logger.exception(f"FAILED TO SPLIT PAGE {i+1} → {str(e)}")
                continue

            # ================= CALL FLASK =================
            page_success = False

            for attempt in range(MAX_RETRIES):

                try:
                    _logger.warning(f"FLASK CALL PAGE {i+1} → ATTEMPT {attempt + 1}")

                    response = requests.post(
                        "https://pdf-extractor-staging.onrender.com/extract",
                        files={"file": ("page.pdf", pdf_bytes_io, "application/pdf")},
                        timeout=120
                    )

                    if response.status_code != 200:
                        _logger.warning(f"FLASK ERROR PAGE {i+1}: {response.status_code}")
                        continue

                    page_data = response.json()

                    # ================= FORMAT SUPPORT =================
                    if isinstance(page_data, dict):
                        pages = page_data.get("pages", [])
                    elif isinstance(page_data, list):
                        pages = page_data
                    else:
                        pages = []

                    if not pages:
                        _logger.warning(f"EMPTY PAGE DATA PAGE {i+1}")
                        continue

                    _logger.warning(f"PAGE {i+1} → RECEIVED {len(pages)} BLOCKS")

                    # ================= NORMALIZATION =================
                    for p in pages:

                        text = p.get("text", "")
                        images = p.get("images", [])

                        if not text and not images:
                            continue

                        all_pages.append({
                            "page": i + 1,
                            "text": text,
                            "images": images
                        })

                    page_success = True
                    break

                except Exception as e:
                    _logger.exception(f"FLASK CALL FAILED PAGE {i+1} → {str(e)}")

                time.sleep(5)

            if not page_success:
                _logger.error(f"PAGE {i+1} FAILED AFTER RETRIES")

            time.sleep(PAGE_DELAY)

        # ================= UPDATE PROGRESS =================
        self.current_page = end_page

        # ================= STORE =================
        try:
            existing = []

            if self.extracted_text:
                try:
                    existing = json.loads(self.extracted_text)
                except Exception:
                    existing = []

            combined = existing + all_pages

            self.extracted_text = json.dumps(combined)

            _logger.warning(f"BATCH STORED → {len(all_pages)} pages")
            _logger.warning(f"TOTAL STORED → {len(combined)} pages")
            _logger.warning(f"EXTRACTED DATA SIZE → {len(self.extracted_text)}")

        except Exception as e:
            _logger.exception(f"FAILED TO STORE DATA → {str(e)}")
            self.state = "failed"
            return

        # ================= 🔥 CRITICAL FIX =================
        if self.current_page < total_pages:

            _logger.warning(f"JOB NOT FINISHED → NEXT START PAGE {self.current_page + 1}")

            # 🔥 FORCE JOB TO CONTINUE
            self.state = "processing"

            time.sleep(BATCH_DELAY)

        else:

            _logger.warning("ALL PAGES PROCESSED ✅")
            self.state = "done"

        _logger.warning("PDF EXTRACTION BATCH COMPLETED")

    # ---------------- OPENAI ----------------

    def send_to_openai_url(self):

        import time
        import re

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

        # 🔥 FLATTEN BLOCKS
        all_blocks = [
            b for p in pages for b in p.get("blocks", [])
        ]

        # 🔥 MAKE ORDER CONSISTENT
        all_blocks = sorted(all_blocks, key=lambda x: (x.get("text") or "")[:50])

        _logger.warning(f"TOTAL BLOCKS → {len(all_blocks)}")

        # 🔥 LIMIT TO PREVENT OVERLOAD
        MAX_BLOCKS = 400
        if len(all_blocks) > MAX_BLOCKS:
            all_blocks = all_blocks[:MAX_BLOCKS]

        # ======================================================
        # 🔥🔥 NEW: FILTER OUT NON-PRODUCT BLOCKS (SAFE INSERT)
        # ======================================================

        def is_valid_block(text):
            if not text:
                return False

            text = text.lower().strip()

            # ❌ noise
            noise_keywords = [
                "cookie", "privacy", "login", "menu",
                "navigation", "home", "accept", "terms"
            ]

            if any(n in text for n in noise_keywords):
                return False

            # ✅ allow more product-like text
            if len(text) < 15:
                return False

            return True

        # 🔥 APPLY FILTER
        all_blocks = [
            b for b in all_blocks
            if is_valid_block(b.get("text", ""))
        ]

        _logger.warning(f"FILTERED BLOCKS → {len(all_blocks)}")

        # =====================================================
        # 🔥 CONTINUE NORMAL FLOW (UNCHANGED)
        # =====================================================

        BLOCK_BATCH_SIZE = 20

        batched_blocks = [
            all_blocks[i:i + BLOCK_BATCH_SIZE]
            for i in range(0, len(all_blocks), BLOCK_BATCH_SIZE)
        ]

        _logger.warning(f"TOTAL BLOCK BATCHES → {len(batched_blocks)}")

        all_products = []

        for batch_index, block_batch in enumerate(batched_blocks):

            _logger.warning(f"AI → PROCESSING BLOCK BATCH {batch_index + 1}")

            combined_text = "\n\n".join([
                f"{b.get('text','')} | IMAGE: {b.get('image','')}"
                for b in block_batch
            ])

            # 🔥 HARD LIMIT (prevents timeout)
            combined_text = combined_text[:12000]

            if not combined_text.strip():
                continue

            # ✅ FULL STRONG PROMPT (UNCHANGED)
            
            prompt = f"""
            You are a highly precise e-commerce product extraction engine.

            You are processing raw scraped website content.

            =====================================
            YOUR GOAL
            =====================================

            Extract ALL individual products from the text.

            IMPORTANT:
            - A single block may contain MULTIPLE products → you MUST split them
            - Each product MUST be returned separately
            - NEVER merge multiple products into one

            =====================================
            HOW TO IDENTIFY A PRODUCT
            =====================================

            A product usually contains:
            - product name
            - price (e.g. $, £, €, numbers)
            - specs or description
            - sometimes reviews

            Strong indicators:
            - currency symbols ($, £, €)
            - model names (Dell, Lenovo, etc.)
            - numbers like GB, inch, SSD, RAM, etc.

            =====================================
            STRICT RULES
            =====================================

            1. RETURN ONLY VALID JSON ARRAY
            2. NO explanation
            3. NO markdown
            4. NO text outside JSON

            5. EACH product must be unique
            6. REMOVE duplicates
            7. DO NOT skip products
            8. SPLIT combined text into multiple products

            =====================================
            REMOVE THIS NOISE
            =====================================

            Ignore anything related to:
            - navigation (Home, Login, Pricing)
            - cookies/privacy
            - footer text
            - categories only (no product info)
            - repeated headers

            =====================================
            OUTPUT FORMAT
            =====================================

            [
            {{
                "name": "Clean product name",
                "description": "Short product description (max 30 words)",
                "category": "Best guess category",
                "image": "image_url_or_null"
            }}
            ]

            =====================================
            EXTRA RULES
            =====================================

            - Keep names SHORT and CLEAN
            - Description must be concise
            - Infer category intelligently
            - If no image exists → return null
            - If unsure → still extract

            =====================================
            TEXT TO PROCESS
            =====================================

            {combined_text}
            """

            try:
                response = client.responses.create(
                    model="gpt-4.1-mini",
                    input=prompt,
                    temperature=0,  
                    timeout=60
                )

                result = response.output_text.strip()

                # 🔥 SAFE MARKDOWN CLEANUP
                result = re.sub(r"^```(?:json)?|```$", "", result).strip()

                # 🔥 SAFE JSON PARSE
                try:
                    parsed = json.loads(result)
                except Exception:
                    _logger.warning("JSON PARSE FAILED → SKIPPING BATCH")
                    continue

                # 🔥 FILTER EMPTY PRODUCTS
                if isinstance(parsed, list):
                    cleaned = [p for p in parsed if p.get("name")]
                    all_products.extend(cleaned)
                    _logger.warning(f"BATCH PRODUCTS → {len(cleaned)}")

            except Exception as e:
                _logger.warning(f"AI ERROR → {str(e)}")
                continue

            time.sleep(1)

        # 🔥 DEDUPLICATE PRODUCTS
        unique = {}
        for p in all_products:
            key = (p.get("name") or "").lower().strip()[:40]
            if key and key not in unique:
                unique[key] = p

        all_products = list(unique.values())

        _logger.warning(f"FINAL UNIQUE PRODUCTS → {len(all_products)}")

        self.ai_response = json.dumps(all_products)

        _logger.warning(f"TOTAL AI PRODUCTS → {len(all_products)}")


    #===========pdf and excel open ai OPENAI=========================

    def send_to_openai_pdf_excel(self):

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

        _logger.warning(f"TOTAL PAGES → {len(pages)}")

        # ================= 🔥 RESUME LOGIC =================
        start_index = self.last_ai_page or 0
        _logger.warning(f"AI RESUME FROM PAGE INDEX → {start_index}")

        # ================= PRESERVE EXISTING DATA =================
        existing_ai = []
        if self.ai_response:
            try:
                existing_ai = json.loads(self.ai_response)
            except Exception:
                existing_ai = []

        page_products = existing_ai.copy()

        # ================= PROCESS ONLY NEW PAGES =================
        for i, page in enumerate(pages[start_index:], start=start_index):

            page_no = page.get("page")
            page_text = page.get("text", "")
            images = page.get("images", [])
            image_count = len(images)

            if not page_text.strip() and not images:
                _logger.warning(f"EMPTY PAGE → SKIP PAGE {page_no}")
                continue

            _logger.warning(f"AI → PROCESSING PAGE {page_no}")

            prompt = f""" You are an advanced product extraction and interpretation engine for catalog PDFs.

            =====================
            CORE RULES (STRICT)
            =====================

            1. RETURN ONLY VALID JSON
            2. NO explanation
            3. NO markdown
            4. NO text outside JSON
            5. DO NOT duplicate products WITHIN THE SAME PAGE
            6. DO NOT skip any product
            7. EACH product must appear exactly once PER PAGE

            IMPORTANT GLOBAL RULE:

            - This input represents ONLY ONE PAGE of a catalog
            - You MUST extract ONLY products visible on THIS PAGE
            - DO NOT repeat products from previous pages
            - DO NOT assume products continue across pages

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

            - If MULTIPLE distinct products:
            → extract EACH product separately

            IMPORTANT:

            - If multiple images exist → assume multiple products
            - DO NOT collapse multiple items into one product
            - If unsure → split into multiple products instead of merging

            CRITICAL:

            - Products are typically aligned with images
            - Each image or grouped images usually represent a product
            - DO NOT treat the whole page as one product

            =====================
            VARIANT DETECTION LOGIC (CRITICAL)
            =====================

            Products in catalogs may appear as multiple similar images WITHOUT explicit labels like "color" or "size".

            You MUST detect variants using visual, structural, and contextual clues.

            A product HAS VARIANTS ONLY IF:

            - The items are clearly the SAME product design
            - Differences are ONLY color, size, or minor variation
            - The items would share the same product name in a store

            DO NOT group items as variants if:
            - They are different product types
            - They have different shapes or purposes
            - They would be listed separately in an e-commerce store

            =====================
            🔥 CRITICAL VARIANT COUNT RULE (NEW)
            =====================

            - If multiple similar items are displayed in a row or grid:
            → EACH visible item MUST be treated as a variant

            - You MUST COUNT the number of visible items
            - DO NOT estimate
            - DO NOT reduce the count

            EXAMPLES:

            - If 10 shirts are visible → return 10 variants
            - If 6 bottles are shown → return 6 variants

            GRID RULE:

            - Each grid item = 1 variant

            VISUAL PRIORITY:

            - Images override text
            - If images show more items than text → trust images

            FAIL CONDITION:

            - Returning fewer variants than visible items is WRONG

            =====================
            VARIANT RULES
            =====================

            - Each product appears ONLY ONCE per page
            - Variants must be grouped under "variants"
            - If no variants exist → DO NOT include "variants"

            ATTRIBUTE INFERENCE:

            - If difference looks like color → use "Color"
            - If difference looks like size → use "Size"
            - If unclear → use "Variant"

            =====================
            VARIANT IMAGE MAPPING (VERY IMPORTANT)
            =====================

            - Each variant MUST map to an image

            - Provide:
            "image_index": index of image (starting from 0)

            STRICT RULE:

            - Number of variants MUST NOT exceed number of images
            - If multiple variants exist → distribute across images

            =====================
            WHEN TO SPLIT PRODUCTS
            =====================

            Treat items as SEPARATE products ONLY IF:
            - Names are clearly different
            - Designs are significantly different
            - They are unrelated items

            If unsure:
            → Prefer splitting into separate products

            =====================
            ANTI-REPETITION RULE
            =====================

            - If same product appears multiple times on THIS PAGE → return it ONLY ONCE

            =====================
            MINIMUM EXTRACTION RULE
            =====================

            - You MUST extract at least ONE product
            - NEVER return empty list

            =====================
            OUTPUT FORMAT
            =====================

            [
                {{
                    "name": "",
                    "description": "",
                    "category": "",
                    "variants": [
                        {{
                            "attributes": {{
                                "Color": ""
                            }},
                            "image_index": 0,
                            "stock": null
                        }}
                    ]
                }}
            ]

            PAGE CONTEXT:
            - This page contains {image_count} product images

            TEXT TO ANALYZE:
            {page_text}
            """

            MAX_RETRIES = 3
            success = False

            for attempt in range(MAX_RETRIES):
                try:

                    image_inputs = [
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{img}"
                        }
                        for img in images[:10]
                    ]

                    response = client.responses.create(
                        model="gpt-4.1-mini",
                        input=[{
                            "role": "user",
                            "content": [{"type": "input_text", "text": prompt}] + image_inputs
                        }],
                        temperature=0,
                        timeout=60
                    )

                    result = response.output_text.strip()
                    _logger.warning(f"RAW AI OUTPUT PAGE {page_no} → {result[:300]}")

                    success = True
                    break

                except Exception as e:
                    _logger.warning(f"PAGE {page_no} → RETRY {attempt+1} FAILED → {str(e)}")

            if not success:
                _logger.error(f"PAGE {page_no} → FINAL FAILURE")
                continue

            # ================= CLEAN =================
            if "```" in result:
                result = result.split("```")[1]

            if result.lower().startswith("json"):
                result = result[4:]

            result = result.strip()

            try:
                parsed = json.loads(result)
            except Exception:
                _logger.warning(f"PAGE {page_no} → INVALID JSON")
                parsed = []

            if not isinstance(parsed, list):
                parsed = []

            page_products.append({
                "page": page_no,
                "products": parsed
            })

            # ================= SAVE PROGRESS =================
            self.last_ai_page = i + 1

            _logger.warning(f"PAGE {page_no} → STORED PRODUCTS: {len(parsed)}")

            time.sleep(1)

        # ================= FINAL SAVE =================
        self.ai_response = json.dumps(page_products)

        _logger.warning(f"AI TOTAL PAGES STORED: {len(page_products)}")
        _logger.warning(f"AI LAST PROCESSED PAGE → {self.last_ai_page}")

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


    # ---------------- PRODUCT CREATION URL----------------

    def create_products_url(self):

        import requests
        import base64
        import json

        if not self.ai_response:
            _logger.warning("NO AI RESPONSE")
            return

        product_obj = self.env['product.template']
        category_obj = self.env['product.category']

        try:
            products = json.loads(self.ai_response)

            if isinstance(products, dict):
                products = [products]

        except Exception as e:
            _logger.error(f"INVALID AI JSON → {str(e)}")
            return

        created_count = 0
        processed = 0

        MAX_PRODUCTS_PER_RUN = 20  # 🔥 CRITICAL LIMIT

        for product in products:

            if processed >= MAX_PRODUCTS_PER_RUN:
                _logger.warning("CRON LIMIT REACHED → CONTINUE NEXT RUN")
                break

            processed += 1

            name = product.get("name")
            if not name:
                continue

            name_clean = name.strip().lower()

            description = product.get("description", "")
            category_name = product.get("category") or "Uncategorized"

            # ================= CATEGORY =================
            category = category_obj.search([('name', '=', category_name)], limit=1)
            if not category:
                category = category_obj.create({'name': category_name})

            # ================= STRONG DUPLICATE CHECK =================
            existing = product_obj.search([
                '|',
                ('name', '=', name.strip()),
                ('name', '=', name_clean)
            ], limit=1)

            if existing:
                _logger.warning(f"DUPLICATE SKIPPED → {name}")
                continue

            vals = {
                'name': name.strip(),
                'description_sale': description,
                'categ_id': category.id,
                'sale_ok': True,
                'website_published': False,
            }

            # ================= IMAGE HANDLING =================
            image_url = (
                product.get("image")
                or product.get("image_url")
                or product.get("raw_image")
            )

            if image_url and isinstance(image_url, str) and image_url.startswith("http"):

                try:
                    _logger.warning(f"FETCHING IMAGE → {image_url}")

                    res = requests.get(image_url, timeout=10)

                    if res.status_code == 200 and res.content:
                        vals['image_1920'] = base64.b64encode(res.content).decode("utf-8")
                    else:
                        _logger.warning(f"INVALID IMAGE RESPONSE → {image_url}")

                except Exception as e:
                    _logger.warning(f"IMAGE FETCH FAILED → {image_url} | {str(e)}")

            else:
                _logger.warning(f"NO VALID IMAGE → {name}")

            # ================= CREATE =================
            try:
                product_obj.create(vals)
                created_count += 1

            except Exception as e:
                _logger.error(f"PRODUCT CREATE FAILED → {name} | {str(e)}")
                continue

            # ================= SAFE COMMIT =================
            if created_count % 10 == 0:
                self.env.cr.commit()

        self.env.cr.commit()

        _logger.warning(f"TOTAL PRODUCTS CREATED THIS RUN: {created_count}")

    #==========create pdf and excel product======================

    def create_products_pdf_excel(self):

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

            for i, product_data in enumerate(products):

                try:

                    name = (product_data.get("name") or "").strip()

                    if not name or len(name) < 3:
                        continue

                    _logger.warning(f"PROCESSING PRODUCT → {name}")

                    description = product_data.get("description", "")
                    category_name = product_data.get("category") or "Uncategorized"

                    # CATEGORY
                    category = category_obj.search([('name', '=', category_name)], limit=1)
                    if not category:
                        category = category_obj.create({'name': category_name})

                    # DEDUP
                    existing_product = product_obj.search([
                        ('name', 'ilike', name)
                    ], limit=1)

                    if existing_product:
                        product = existing_product
                        _logger.warning(f"DUPLICATE SKIPPED → {name}")
                    else:
                        vals = {
                            'name': name,
                            'description_sale': description,
                            'categ_id': category.id,
                            'sale_ok': True,
                            'website_published': False,
                        }

                        # IMAGE (basic fallback)
                        images = page_data.get("images", [])
                        if images:
                            vals['image_1920'] = images[0]

                        product = product_obj.create(vals)
                        created_count += 1

                        self.env.cr.commit()

                    # ================= 🔥 VARIANT FIX START =================

                    variants = product_data.get("variants", [])
                    images = page_data.get("images", [])

                    # 🔥 FALLBACK: AUTO EXPAND VARIANTS IF AI FAILED
                    if len(variants) < len(images) and len(images) > 1:
                        _logger.warning(f"VARIANT AUTO-EXPANSION TRIGGERED → PAGE {page_no}")

                        variants = []
                        for idx in range(len(images)):
                            variants.append({
                                "attributes": {"Variant": f"Option {idx+1}"},
                                "image_index": idx
                            })

                    # 🔥 APPLY VARIANTS
                    for variant in variants:

                        attributes = variant.get("attributes", {})
                        image_index = variant.get("image_index")

                        created_values = []

                        for attr_name, attr_value in attributes.items():

                            if not attr_value:
                                continue

                            attribute = self.env['product.attribute'].search([
                                ('name', '=', attr_name)
                            ], limit=1)

                            if not attribute:
                                attribute = self.env['product.attribute'].create({
                                    'name': attr_name
                                })

                            value = self.env['product.attribute.value'].search([
                                ('name', '=', attr_value),
                                ('attribute_id', '=', attribute.id)
                            ], limit=1)

                            if not value:
                                value = self.env['product.attribute.value'].create({
                                    'name': attr_value,
                                    'attribute_id': attribute.id
                                })

                            created_values.append(value)

                            line = self.env['product.template.attribute.line'].search([
                                ('product_tmpl_id', '=', product.id),
                                ('attribute_id', '=', attribute.id)
                            ], limit=1)

                            if not line:
                                self.env['product.template.attribute.line'].create({
                                    'product_tmpl_id': product.id,
                                    'attribute_id': attribute.id,
                                    'value_ids': [(6, 0, [value.id])]
                                })
                            else:
                                if value.id not in line.value_ids.ids:
                                    line.value_ids = [(4, value.id)]

                        # 🔥 NOW FIND CORRECT VARIANT RECORD
                        if created_values:

                            variant_record = self.env['product.product'].search([
                                ('product_tmpl_id', '=', product.id),
                                ('product_template_attribute_value_ids.product_attribute_value_id', 'in',
                                [v.id for v in created_values])
                            ], limit=1)

                            # 🔥 ASSIGN CORRECT IMAGE
                            if variant_record and image_index is not None:
                                if 0 <= image_index < len(images):
                                    variant_record.image_1920 = images[image_index]
                                    _logger.warning(f"VARIANT IMAGE ASSIGNED → {attributes}")

                    # ================= 🔥 VARIANT FIX END =================

                except Exception as e:
                    _logger.error(f"PRODUCT FAILED → {str(e)}")
                    self.env.cr.rollback()
                    continue

            _logger.warning(f"PAGE {page_no} DONE")

        _logger.warning(f"TOTAL PRODUCTS CREATED: {created_count}")
        _logger.warning("PRODUCT CREATION LOOP COMPLETED")

    #-----URL API FLOW-------------------------------------------

    def scrape_with_playwright(self):

        from playwright.sync_api import sync_playwright
        import subprocess
        import os

        _logger.warning(f"PLAYWRIGHT SCRAPE → {self.data_url}")

        #✅ CHECK IF BROWSER EXISTS FIRST
        browser_path = os.path.expanduser("~/.cache/ms-playwright")

        if not os.path.exists(browser_path):
            _logger.warning("PLAYWRIGHT → INSTALLING BROWSER (FIRST RUN)")

            try:
                subprocess.run(
                    ["python", "-m", "playwright", "install", "chromium"],
                    check=True
                )
                _logger.warning("PLAYWRIGHT BROWSER INSTALLED")
            except Exception as e:
                _logger.error(f"PLAYWRIGHT INSTALL FAILED → {str(e)}")
                return

        products = []

        with sync_playwright() as p:

            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(self.data_url, timeout=60000)
            page.wait_for_timeout(5000)

            # ✅ Cookie handling
            try:
                page.locator("button:has-text('Accept')").click(timeout=3000)
            except:
                pass

            items = page.query_selector_all("a, div")

            _logger.warning(f"PLAYWRIGHT ELEMENTS FOUND → {len(items)}")

            for item in items[:200]:

                try:
                    text = item.inner_text().strip()

                    if not text or len(text) < 5:
                        continue

                    img_el = item.query_selector("img")
                    img_url = img_el.get_attribute("src") if img_el else None

                    if img_url and img_url.startswith("//"):
                        img_url = "https:" + img_url

                    img_base64 = None

                    if img_url:
                        try:
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

        jobs = self.search(
            [('state', 'in', ['draft', 'processing'])],
            order="priority asc, id asc",
            limit=1
        )

        _logger.warning(f"CRON → Found {len(jobs)} jobs")

        for job in jobs:
            try:
                _logger.warning(f"CRON → START JOB {job.id}")
                _logger.warning(f"CRON → JOB {job.id} CURRENT STATE: {job.state}")

                job.state = 'processing'

                job.process_import()

                _logger.warning(f"CRON → JOB {job.id} FINAL STATE: {job.state}")

                # ❌ DO NOT TOUCH STATE HERE

                _logger.warning(f"CRON → JOB {job.id} DONE")

            except Exception as e:
                _logger.exception(f"PROCESS FAILED → {str(e)}")
                job.state = 'failed'

   #=============flask setup/installation=================== 
    def ping_flask_server(self):
      
        try:
            requests.get("https://pdf-extractor-staging.onrender.com", timeout=10)
            _logger.info("FLASK PING SUCCESS")
        except Exception:
            _logger.warning("FLASK PING FAILED")

    #---------------normalizer-------------------------------
   
    def _normalize_url_data(self, items):

        blocks = []

        for item in items:

            # ✅ FIX: USE "text" FROM APIFY
            text = (item.get("text") or "").strip()
            image = item.get("image")

            if not text:
                continue

            blocks.append({
                "text": text,
                "image": image
            })

        _logger.warning(f"NORMALIZED BLOCKS → {len(blocks)}")

        return [{
            "page": 1,
            "blocks": blocks
        }]

    #---------------clean_scraped_blocks-------------------------------
    def _clean_scraped_blocks(self, raw_blocks):
        """
        Clean Apify output before sending to AI
        """

        cleaned = []
        seen = set()

        for item in raw_blocks:

            text = (item.get("text") or "").strip()
            image = item.get("image")

            # ❌ REMOVE NOISE
            if not text:
                continue

            if len(text) < 15:
                continue

            if any(x in text.lower() for x in [
                "privacy", "cookie", "terms", "login",
                "menu", "navigation", "home"
            ]):
                continue

            # ❌ REMOVE DUPLICATES
            key = text[:120]  # allow more variation

            if key in seen:
                continue

            seen.add(key)

            cleaned.append({
                "text": text,
                "image": image
            })

        return cleaned
    

    #======apify url fetch/scrapp products=============== 
    def _run_apify_actor(self, url):

        token = self.env['ir.config_parameter'].sudo().get_param('apify.api_token')

        if not token:
            raise Exception("Apify API token not configured")

        ACTOR_ID = "princ_adex~my-actor"

        run_url = f"https://api.apify.com/v2/acts/{ACTOR_ID}/runs?token={token}"
        _logger.warning(f"APIFY RUN URL → {run_url}")

        payload = {
            "startUrls": [
                {"url": url}
            ]
        }

        headers = {
            "Content-Type": "application/json"
        }

        # 🚀 START ACTOR
        response = requests.post(run_url, json=payload, headers=headers, timeout=30)

        if response.status_code != 201:
            raise Exception(f"Apify run failed: {response.text}")

        run_data = response.json()
        run_id = run_data["data"]["id"]
        dataset_id = run_data["data"]["defaultDatasetId"]

        _logger.warning(f"APIFY RUN ID → {run_id}")
        _logger.warning(f"APIFY DATASET ID → {dataset_id}")

        # 🔁 WAIT FOR ACTOR TO FINISH
        for _ in range(30):  # ~90 seconds max
            status_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={token}"

            status_res = requests.get(status_url, timeout=20).json()
            status = status_res["data"]["status"]

            _logger.warning(f"APIFY STATUS → {status}")

            if status == "SUCCEEDED":
                break

            if status in ["FAILED", "ABORTED", "TIMED-OUT"]:
                raise Exception(f"Apify run failed with status: {status}")

            time.sleep(3)
        else:
            raise Exception("Apify run timeout exceeded")

        # 📦 FETCH DATA WITH LIMIT
        dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items"

        params = {
            "token": token,
            "limit": 1000,
            "clean": "true"   # ✅ MUST be string
        }

        dataset_res = requests.get(dataset_url, params=params, timeout=30)

        if dataset_res.status_code != 200:
            raise Exception(f"Failed to fetch dataset: {dataset_res.text}")

        data = dataset_res.json()

        _logger.warning(f"APIFY ITEMS FETCHED → {len(data)}")

        # ❗ SAFETY CHECK
        if not data:
            raise Exception("Apify returned empty dataset")

        return data
    
    def validate_ai_output(products):
        for p in products:
            if "variants" in p:
                if not isinstance(p["variants"], list):
                    p["variants"] = []

                for v in p["variants"]:
                    if "attributes" not in v:
                        v["attributes"] = {"Variant": "Default"}

        return products