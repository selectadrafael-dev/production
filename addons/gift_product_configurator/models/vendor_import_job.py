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
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from openai import OpenAI
import re
import fitz

 

_logger = logging.getLogger(__name__)

# ✅ Extend existing model
class ResPartner(models.Model):
    _inherit = 'res.partner'

    #Vendor user role
    is_vendor_user = fields.Boolean(
        string="Vendor User",
        default=False
    )


class VendorImportJob(models.Model):

    _name = "vendor.import.job"
    _description = "Vendor Import Job"

    partner_id = fields.Many2one("res.partner", string="Vendor")  # ✅ LINK instead

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
    excel_created_index = fields.Integer(
        string="Excel Created Index",
        default=0
    )

    apify_run_id = fields.Char()
    apify_dataset_id = fields.Char()
    url_batch_index = fields.Integer(default=0)
    last_processed_product_index = fields.Integer(default=0)
    last_created_page = fields.Integer(default=0)
    lock = fields.Boolean(default=False)
    is_excel_parsed = fields.Boolean(default=False)
    excel_ai_index = fields.Integer(default=0)
    upload_signature = fields.Char(string="Upload Signature")

    source_type = fields.Selection([
        ("pdf", "PDF"),
        ("excel", "Excel"),
        ("url", "URL"),
    ])


    state = fields.Selection([
        ('draft', 'Draft'),
        ('processing', 'Processing'),
        ('review', 'Vendor Review'),
        ('done', 'Completed'),
        ('error', 'Error'),
        ('failed', 'Failed'),

         #New
        ('url_scraping', 'URL Scraping'),
        ('url_ai', 'URL AI'),
        ('url_creating', 'URL Creating'),

        ('pdf_extracting', 'PDF Extracting'),
        ('pdf_ai', 'PDF AI'),
        ('pdf_creating', 'PDF Creating'),

        ('excel_parsing', 'Excel Parsing'),
        ('excel_ai', 'Excel AI'),
        ('excel_creating', 'Excel Creating'),

    ], default='draft')


     #============================= MAIN FLOW (process steps) =====================

    def process_import(self):

        _logger.warning(f"PROCESS START → Job {self.id}")

        try:
            if self.state == 'review':
                self.state = 'processing'

            if self.state == 'draft':
                self.state = 'processing'

            self._process_step()

        except Exception as e:
            _logger.error(f"PROCESS FAILED → {str(e)}")
            self.state = "failed"


    #============Procsing Jobs===================================================

    def _process_step(self):

        _logger.warning(f"[STEP] JOB {self.id} STATE → {self.state}")

        # 🔥 FIX STUCK STATE
        if self.state == 'review':
            self.state = 'processing'
            return True

        # 🔥 GLOBAL SAFE GUARD

        if self.state == 'processing':

            _logger.warning("STATE = PROCESSING → RESUME WORKFLOW")

            if self.data_url:
                self.state = 'url_scraping'

            elif self.excel_file and not self.pdf_file:
                self.state = 'excel_parsing'

            elif self.pdf_file:
                self.state = 'pdf_extracting'

    # 🔥 DO NOT RETURN → CONTINUE EXECUTION

        # ================= URL =================
        if self.data_url:

            if self.state in ['draft']:
                self.state = 'url_scraping'
                return True
            
            if self.state == 'url_scraping':
                self.parse_url()

                if self.extracted_text:
                    self.state = 'url_ai'

                return True

            if self.state == 'url_ai':
                self.send_to_openai_url()

                if self.url_batch_index >= getattr(self, "url_total_batches", 9999):
                    self.state = 'url_creating'

                return True

            if self.state == 'url_creating':
                self.create_products_url()

                try:
                    total = len(json.loads(self.ai_response or "[]"))
                except:
                    total = 0

                if self.last_processed_product_index >= total:
                    self.state = 'done'
                else:
                    self.state = 'processing'

                return True


        # ================= EXCEL =================
     
        elif self.excel_file:
            _logger.warning("FLOW = EXCEL CONFIRMED")
            if self.state in ['draft']:
                self.state = 'excel_parsing'
                return True

            if self.state == 'excel_parsing':

                self.parse_excel()

                # 🔥 IMPORTANT: CHECK COMPLETION
                if self.is_excel_parsed:
                    _logger.warning("EXCEL → MOVE TO AI")
                    self.state = 'excel_ai'
                else:
                    self.state = 'processing'

                return True

            if self.state == 'excel_ai':

                _logger.warning("STEP → SEND TO AI (EXCEL)")
                self.send_to_openai_pdf_excel()

                # 🔥 WAIT FOR AI TO FINISH
                if self.state == 'processing':
                    return True

                self.state = 'excel_creating'
                return True

            if self.state == 'excel_creating':

                self.create_products_pdf_excel()

                total_rows = 0
                try:
                    data = json.loads(self.extracted_text or "[]")
                    total_rows = len(data)
                except:
                    total_rows = 0

                _logger.warning(f"[FLOW CHECK] created_index → {self.excel_created_index}")
                _logger.warning(f"[FLOW CHECK] total_rows → {total_rows}")

                if self.excel_created_index >= total_rows:
                    _logger.warning("EXCEL → ALL PRODUCTS CREATED ✅")
                    self.state = 'done'
                else:
                    _logger.warning("EXCEL → CONTINUE NEXT BATCH 🔁")
                    self.state = 'excel_ai'

        # ================= PDF =================
        elif self.pdf_file:

            if self.state in ['draft']:
                self.state = 'pdf_extracting'
                return True

            if self.state == 'pdf_extracting':
                self.extract_pdf()

                if self.current_page >= self.total_pages:
                    self.state = 'pdf_ai'
                else:
                    self.state = 'processing'

                return True

            if self.state == 'pdf_ai':
                self.send_to_openai_pdf_excel()

                if self.last_ai_page >= self.total_pages:
                    self.state = 'pdf_creating'
                else:
                    self.state = 'processing'

                return True

            if self.state == 'pdf_creating':
                self.create_products_pdf_excel()
                self.state = 'done'
                return True

    #------------parse url------------------------------------
    def parse_url(self):

        _logger.warning(f"APIFY SCRAPE → {self.data_url}")

        raw_data = self._run_apify_actor(self.data_url)

        _logger.warning(f"RAW APIFY DATA SAMPLE → {str(raw_data)[:200]}")

        # 🔥 VERY IMPORTANT FIX
        if raw_data is None:
            _logger.warning("APIFY NOT READY → WAIT NEXT CRON")
            return

        if not raw_data:
            _logger.error("APIFY FAILED → EMPTY DATASET")
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

        _logger.warning("EXCEL → START PARSING (BATCH MODE)")

        excel_bytes = base64.b64decode(self.excel_file)
        wb = load_workbook(filename=BytesIO(excel_bytes))

        headers = {"User-Agent": "Mozilla/5.0"}

        pages = []

        # 🔥 BATCH CONTROL
        BATCH_SIZE = 20
        start_index = self.last_processed_product_index or 0
        current_count = 0
        global_index = 0  # counts ONLY valid rows

        _logger.warning(f"EXCEL RESUME FROM INDEX → {start_index}")

        # ================= 🔥 REAL TOTAL ROWS (FIXED) =================
        total_rows = 0

        for sheet in wb.worksheets:
            for idx, row in enumerate(sheet.iter_rows()):

                if idx == 0:
                    continue  # skip header

                # 🔍 SAME LOGIC AS PROCESSING
                row_text_parts = []
                for cell in row:
                    val = str(cell.value or "").strip()
                    if val:
                        row_text_parts.append(val)

                if not row_text_parts:
                    continue

                total_rows += 1

        _logger.warning(f"[DEBUG] REAL TOTAL ROWS → {total_rows}")

        # ================= MAIN LOOP =================
        for sheet in wb.worksheets:

            _logger.warning(f"PROCESSING SHEET → {sheet.title}")
            image_loader = SheetImageLoader(sheet)

            for idx, row in enumerate(sheet.iter_rows()):

                if current_count >= BATCH_SIZE:
                    _logger.warning("BATCH LIMIT REACHED → NEXT CRON")
                    break

                if idx == 0:
                    continue

                row_text_parts = []
                for cell in row:
                    val = str(cell.value or "").strip()
                    if val:
                        row_text_parts.append(val)

                if not row_text_parts:
                    continue

                # 🔥 COUNT ONLY VALID ROWS
                global_index += 1

                if global_index <= start_index:
                    continue

                # ================= FORMAT =================
                row_text = f"""
                ROW_DATA:
                {" | ".join(row_text_parts)}
                """

                row_images = []

                # ================= IMAGE (EMBEDDED) =================
                for cell in row:
                    try:
                        if image_loader.image_in(cell.coordinate):
                            pil_img = image_loader.get(cell.coordinate)
                            buffer = BytesIO()
                            pil_img.save(buffer, format="JPEG")
                            img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
                            row_images.append(img_base64)
                            break
                    except:
                        continue

                # ================= IMAGE (URL) =================
                if not row_images:
                    for cell in row:
                        val = str(cell.value or "").strip()
                        if val.startswith("http"):
                            try:
                                response = requests.get(val, headers=headers, timeout=5)
                                if response.status_code == 200 and "image" in response.headers.get("Content-Type", ""):
                                    img_base64 = base64.b64encode(response.content).decode("utf-8")
                                    row_images.append(img_base64)
                                    break
                            except:
                                continue

                pages.append({
                    "page": global_index,
                    "text": row_text,
                    "images": row_images,
                    "row_index": global_index
                })

                current_count += 1

            if current_count >= BATCH_SIZE:
                break

        # ================= STORE =================
        existing = []
        if self.extracted_text:
            try:
                existing = json.loads(self.extracted_text)
            except:
                existing = []

        combined = existing + pages
        self.extracted_text = json.dumps(combined)

        # ================= SAVE PROGRESS =================
        new_index = start_index + current_count
        self.last_processed_product_index = new_index

        # ================= DEBUG =================
        remaining = max(total_rows - new_index, 0)
        progress = round((new_index / total_rows) * 100, 2) if total_rows else 0

        _logger.warning(f"[DEBUG] CURRENT INDEX → {new_index}")
        _logger.warning(f"[DEBUG] REMAINING ROWS → {remaining}")
        _logger.warning(f"[DEBUG] PROGRESS → {progress}%")

        _logger.warning(f"EXCEL NEW INDEX → {new_index}")
        _logger.warning(f"EXCEL BATCH STORED → {len(pages)} rows")

        # ================= COMPLETION =================
        if new_index >= total_rows:
            _logger.warning("EXCEL → PARSING COMPLETED ✅")
            self.is_excel_parsed = True
        else:
            _logger.warning("EXCEL → MORE DATA REMAIN → NEXT CRON")
            self.state = "processing"

    # ---------------- PDF ----------------

    def extract_pdf(self):

        _logger.warning("PDF → START EXTRACTION (BATCH MODE)")
        pdf_bytes = base64.b64decode(self.pdf_file)

        MAX_RETRIES = 3

        # 🔥 BATCH CONFIG
        BATCH_SIZE = 3
    
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

                    # 👉 AFTER finishing with page (VERY IMPORTANT)
                    pdf_bytes_io.close()
                    single_pdf.close()

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

                # time.sleep(5)

            if not page_success:
                _logger.error(f"PAGE {i+1} FAILED AFTER RETRIES")

            # time.sleep(PAGE_DELAY)

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

            self.state = "pdf_extracting"

        else:

            _logger.warning("ALL PAGES PROCESSED ✅")
            self.state = "done"

        _logger.warning("PDF EXTRACTION BATCH COMPLETED")


    # ---------------- OPENAI ----------------
    def send_to_openai_url(self):

        import re
        import json


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

        # ================= LOAD EXISTING =================
        existing_products = []
        if self.ai_response:
            try:
                existing_products = json.loads(self.ai_response)
            except:
                existing_products = []

        current_batch = getattr(self, "url_batch_index", 0)

        # ================= FLATTEN =================
        all_blocks = [
            b for p in pages for b in p.get("blocks", [])
        ]

        _logger.warning(f"RAW BLOCKS → {len(all_blocks)}")

        # ================= CLEAN =================
        cleaned_blocks = self._clean_scraped_blocks(all_blocks)

        _logger.warning(f"CLEAN BLOCKS → {len(cleaned_blocks)}")
        _logger.warning(f"REMOVED BLOCKS → {len(all_blocks) - len(cleaned_blocks)}")

        # Sort for consistency
        cleaned_blocks = sorted(cleaned_blocks, key=lambda x: (x.get("text") or "")[:50])

        # ================= BATCH =================
        BLOCK_BATCH_SIZE = 20  # 🔥 SAFE for memory

        batched_blocks = [
            cleaned_blocks[i:i + BLOCK_BATCH_SIZE]
            for i in range(0, len(cleaned_blocks), BLOCK_BATCH_SIZE)
        ]

        total_batches = len(batched_blocks)
        self.url_total_batches = total_batches

        _logger.warning(f"TOTAL BLOCK BATCHES → {total_batches}")
        _logger.warning(f"CURRENT BATCH → {current_batch}")

        # ================= STOP IF DONE =================
        if current_batch >= total_batches:
            _logger.warning("ALL URL BATCHES PROCESSED ✅")
            return

        # ================= PROCESS ONE BATCH =================
        block_batch = batched_blocks[current_batch]

        _logger.warning(f"PROCESSING BLOCK COUNT → {len(block_batch)}")
        _logger.warning(f"AI → PROCESSING BLOCK BATCH {current_batch + 1}")

        # 🔥 DO NOT LIMIT AGAIN (FIXED)
        combined_text = "\n\n---\n\n".join([
            f"{b.get('text','')}\nIMAGE_URL: {b.get('image','')}"
            for b in block_batch
        ])

        if not combined_text.strip():
            _logger.warning("EMPTY COMBINED TEXT → SKIP")
            return

        # ================= SAFETY LIMIT =================
        if len(combined_text) > 15000:
            combined_text = combined_text[:15000]
            _logger.warning("TEXT TRIMMED → PREVENT TOKEN OVERFLOW")

        # ================= PROMPT =================
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

        # ================= OPENAI =================
        try:
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=prompt,
                temperature=0,
                timeout=60
            )

            result = response.output_text.strip()
            result = re.sub(r"^```(?:json)?|```$", "", result).strip()

            parsed = json.loads(result)

            if isinstance(parsed, list):

                cleaned = [p for p in parsed if p.get("name")]

                _logger.warning(f"AI RETURNED → {len(cleaned)} PRODUCTS")

                if len(cleaned) < 5:
                    _logger.warning("⚠️ LOW EXTRACTION → CHECK BLOCK QUALITY")

                existing_products.extend(cleaned)

                _logger.warning(f"TOTAL ACCUMULATED → {len(existing_products)}")

            else:
                _logger.warning("AI RESPONSE NOT LIST")

        except Exception as e:
            _logger.warning(f"AI ERROR → {str(e)}")
            return

        # ================= SAVE PROGRESS =================
        self.ai_response = json.dumps(existing_products)
        self.url_batch_index = current_batch + 1

        _logger.warning(f"NEXT BATCH INDEX → {self.url_batch_index}")

        # ================= SAFE EXIT =================
        _logger.warning("CRON EXIT → CONTINUE NEXT RUN")
        return

    #===========pdf and excel open ai OPENAI=========================

    def send_to_openai_pdf_excel(self):

        import json

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

        is_excel = any("row_index" in p for p in pages)

        _logger.warning(f"MODE DETECTED → {'EXCEL' if is_excel else 'PDF'}")

        # ================= EXCEL MODE (FIXED) =================
        if is_excel:

            BATCH_SIZE = 20
            start = self.excel_ai_index or 0
            end = min(start + BATCH_SIZE, len(pages))

            batch = pages[start:end]

            _logger.warning(f"EXCEL AI → PROCESSING ROWS {start} to {end}")

            existing_products = []
            if self.ai_response:
                try:
                    existing_products = json.loads(self.ai_response)[0]["products"]
                except:
                    existing_products = []

            new_products = []

            for idx, row in enumerate(batch, start=start):

                row_text = row.get("text", "")
                images = row.get("images", [])

                prompt = f"""
                You are a structured Excel product parser.

                Each input represents EXACTLY ONE ROW = ONE PRODUCT.

                =====================================
                COLUMN UNDERSTANDING (CRITICAL)
                =====================================

                The row contains mixed values like:

                - ID (e.g. 94601, 12345)
                - Range (e.g. 2-66, 11-00)
                - Stock numbers
                - Prices
                - Links (http...)
                - Image references

                YOU MUST:

                1. IDENTIFY PRODUCT ID
                - Usually numeric (e.g. 94601)
                - Column name may vary (KOD, SKU, ID, CODE)

                2. IDENTIFY PRODUCT NAME
                - MUST NOT be:
                    - pure numbers
                    - ranges (e.g. 2-66)
                    - links
                    - dates
                    - column headers like FOTO

                - If no clear name:
                    → GENERATE NAME like:
                    "Product <ID>"

                3. DESCRIPTION:
                - Short summary from row

                4. CATEGORY:
                - Guess intelligently (e.g. bottle → Drinkware)

                =====================================
                VARIANT DETECTION (VERY IMPORTANT)
                =====================================

                - If multiple rows share SAME ID
                → they are VARIANTS of same product
                - ALSO extract variant attributes from the row:
    
                Examples:
                - Colors → Black, Blue, Red
                - Sizes → S, M, L
                - Range values (e.g. 2-66) → treat as Size or Option

                - If row contains variation info:
                    → put inside "variants"

                - If no clear attribute:
                    → create:
                       "attributes": {{
                            "Variant": "<value from row>"
                        }}

               =====================================
                VARIANT GROUPING (MANDATORY - STRICT)
                =====================================

                - Every product MUST have "variant_group"

                - Extract product ID from the row:
                    (examples: 94601, 92070, ANT021)

                - That ID MUST be used as variant_group

                - RULES:
                    - SAME ID → SAME variant_group
                    - DIFFERENT ID → DIFFERENT product
                    - NEVER leave variant_group empty
                    - NEVER return null

                - If ID exists → use it
                - If ID is a mixture of numerical data and string → use it, but never use date or range
                - If ID unclear → use first numeric value in row

                =====================================
                OUTPUT FORMAT (STRICT)
                =====================================

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

                =====================================
                ROW DATA
                =====================================

                {row_text}
                """

                try:
                    response = client.responses.create(
                        model="gpt-4.1-mini",
                        input=prompt,
                        timeout=60
                    )

                    result = response.output_text.strip()
                    parsed = json.loads(result)

                    if isinstance(parsed, list) and parsed:
                        parsed = parsed[0]

                    if images:
                        parsed["image"] = images[0]

                    new_products.append(parsed)

                    _logger.warning(f"ROW {idx} → OK")

                except Exception as e:
                    _logger.warning(f"ROW {idx} FAILED → {str(e)}")

            combined = existing_products + new_products

            self.ai_response = json.dumps([{
                "page": 1,
                "products": combined
            }])

            # ✅ CRITICAL FIX
            self.excel_ai_index = end

            _logger.warning(f"EXCEL AI PROGRESS → {end}/{len(pages)}")

            if end < len(pages):
                self.state = "excel_ai"
            else:
                _logger.warning("EXCEL AI COMPLETE ✅")
                self.state = "excel_creating"

            return

        # ================= PDF MODE (UNCHANGED — SAFE) =================

        page_products = []
        start_index = self.last_ai_page or 0

        for i, page in enumerate(pages[start_index:], start=start_index):

            page_no = page.get("page")
            page_text = page.get("text", "")
            images = page.get("images", [])

            if not page_text.strip() and not images:
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
            - This page contains product images

            TEXT TO ANALYZE:
            {page_text}
            """

            try:
                response = client.responses.create(
                    model="gpt-4.1-mini",
                    input=page_text,
                    timeout=60
                )
                result = response.output_text.strip()
                parsed = json.loads(result)

            except Exception as e:
                _logger.warning(f"PAGE {page_no} FAILED → {str(e)}")
                parsed = []

            page_products.append({
                "page": page_no,
                "products": parsed
            })

            self.last_ai_page = i + 1

        self.ai_response = json.dumps(page_products)

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

        TOTAL_PRODUCTS = len(products)
        start_index = self.last_processed_product_index or 0

        _logger.warning(f"TOTAL AI PRODUCTS → {TOTAL_PRODUCTS}")
        _logger.warning(f"START INDEX → {start_index}")

        created_count = 0
        skipped_count = 0

        MAX_PRODUCTS_PER_RUN = 10

        CATEGORY_MAPPING = {
            "t-shirt": "Apparel",
            "shirt": "Apparel",
            "polo": "Apparel",
            "bag": "Bags",
            "backpack": "Bags",
            "cap": "Headwear",
            "hat": "Headwear",
            "bottle": "Drinkware",
            "cup": "Drinkware",
            "drinkware": "Drinkware",
            "pen": "Stationery",
            "notebook": "Stationery",
            "powerbank": "Electronics",
            "charger": "Electronics",
            "laptop": "Electronics",
        }

        parent_category = category_obj.search([('name', '=', "All Products")], limit=1)
        if not parent_category:
            parent_category = category_obj.create({'name': "All Products"})

        end_index = min(start_index + MAX_PRODUCTS_PER_RUN, TOTAL_PRODUCTS)

        _logger.warning(f"PROCESSING RANGE → {start_index} to {end_index}")

        for idx in range(start_index, end_index):

            product = products[idx]

            name = product.get("name")
            if not name:
                skipped_count += 1
                continue

            description = product.get("description", "")
            raw_category = (product.get("category") or "").lower()

            # ================= CATEGORY =================
            mapped_category = "General"
            for key, val in CATEGORY_MAPPING.items():
                if key in raw_category:
                    mapped_category = val
                    break

            category = category_obj.search([
                ('name', '=', mapped_category),
                ('parent_id', '=', parent_category.id)
            ], limit=1)

            if not category:
                category = category_obj.create({
                    'name': mapped_category,
                    'parent_id': parent_category.id
                })

            # ================= DUPLICATE CHECK =================
            existing = product_obj.search([
                ('name', 'ilike', name.strip())
            ], limit=1)

            if existing:
                _logger.warning(f"SKIPPED DUPLICATE → {name}")
                skipped_count += 1
                continue

            vals = {
                'name': name.strip(),
                'description_sale': description,
                'categ_id': category.id,
                'sale_ok': True,
                'website_published': False,
            }

            # ================= IMAGE =================
            image_url = product.get("image")

            if image_url and isinstance(image_url, str) and image_url.startswith("http"):

                try:
                    _logger.warning(f"FETCHING IMAGE → {image_url}")

                    res = requests.get(image_url, timeout=5, stream=True)

                    if res.status_code != 200:
                        _logger.warning(f"IMAGE HTTP ERROR → {res.status_code}")
                        continue

                    content_type = res.headers.get("Content-Type", "")
                    if "image" not in content_type:
                        _logger.warning(f"NOT AN IMAGE → {content_type}")
                        continue

                    content = res.raw.read(500000, decode_content=True)

                    if not content:
                        _logger.warning("EMPTY IMAGE CONTENT")
                        continue

                    vals['image_1920'] = base64.b64encode(content).decode("utf-8")

                    _logger.warning("IMAGE STORED SUCCESSFULLY")

                except Exception as e:
                    _logger.warning(f"IMAGE FAILED → {str(e)}")

            else:
                _logger.warning(f"NO VALID IMAGE URL → {image_url}")

            # ================= CREATE =================
            try:
                product_obj.create(vals)
                created_count += 1

            except Exception as e:
                _logger.error(f"CREATE FAILED → {name} | {str(e)}")
                skipped_count += 1
                continue

            if created_count % 10 == 0:
                self.env.cr.commit()

        # ================= SAVE PROGRESS =================
        self.last_processed_product_index = end_index

        _logger.warning(f"CREATED THIS RUN → {created_count}")
        _logger.warning(f"SKIPPED THIS RUN → {skipped_count}")
        _logger.warning(f"NEXT START INDEX → {self.last_processed_product_index}")

        if self.last_processed_product_index >= TOTAL_PRODUCTS:
            _logger.warning("ALL PRODUCTS CREATED ✅")
        else:
            _logger.warning("MORE PRODUCTS REMAIN → NEXT CRON")

        self.env.cr.commit()

    #==========create pdf and excel product======================

    def create_products_pdf_excel(self):

        import json
        import re

        if not self.ai_response or not self.extracted_text:
            _logger.warning("NO AI OR EXTRACTED DATA → STOP")
            return

        product_obj = self.env['product.template']
        category_obj = self.env['product.category']

        try:
            pages = json.loads(self.extracted_text)
            ai_pages = json.loads(self.ai_response)
        except:
            _logger.error("INVALID JSON")
            return

        created_count = 0

        CATEGORY_MAPPING = {
            "t-shirt": "Apparel",
            "shirt": "Apparel",
            "polo": "Apparel",
            "bag": "Bags",
            "backpack": "Bags",
            "cap": "Headwear",
            "hat": "Headwear",
            "bottle": "Drinkware",
            "pen": "Stationery",
            "notebook": "Stationery",
        }

        parent_category = category_obj.search([('name', '=', "All Products")], limit=1)
        if not parent_category:
            parent_category = category_obj.create({'name': "All Products"})

        # =====================================================
        # 🔥 EXCEL FLOW (FULLY PRESERVED + BATCH CONTROL)
        # =====================================================
        if self.excel_file:

            start = self.excel_created_index or 0
            end = min(start + 20, len(pages))

            _logger.warning(f"[EXCEL CREATE RANGE] → {start} to {end}")

            for page_data in pages[start:end]:

                page_no = page_data.get("page")

                ai_page = next((p for p in ai_pages if p.get("page") == 1), None)
                if not ai_page:
                    continue

                products = ai_page.get("products", [])
                if not products:
                    continue

                # ================= ORIGINAL EXCEL LOGIC =================
                grouped_products = {}

                for p in products:
                    raw_name = (p.get("name") or "").strip()

                    match = re.search(r'(?:Product\s*)?([A-Z]*\d+)', raw_name, re.I)

                    if match:
                        group_id = match.group(1).upper()
                    else:
                        group_id = raw_name.upper()

                    grouped_products.setdefault(group_id, []).append(p)

                _logger.warning(f"[EXCEL] GROUPS → {len(grouped_products)}")

                for group_id, group_items in grouped_products.items():

                    main_product = group_items[0]

                    name = (main_product.get("name") or "").strip()
                    description = main_product.get("description", "")
                    raw_category = (main_product.get("category") or "").lower()

                    mapped_category = "General"
                    for key, val in CATEGORY_MAPPING.items():
                        if key in raw_category:
                            mapped_category = val
                            break

                    category = category_obj.search([
                        ('name', '=', mapped_category),
                        ('parent_id', '=', parent_category.id)
                    ], limit=1)

                    if not category:
                        category = category_obj.create({
                            'name': mapped_category,
                            'parent_id': parent_category.id
                        })

                    product = product_obj.search([
                        ('default_code', '=', group_id)
                    ], limit=1)

                    if not product:
                        vals = {
                            'name': name,
                            'default_code': group_id,
                            'description_sale': description,
                            'categ_id': category.id,
                            'sale_ok': True,
                            'website_published': False,
                        }

                        image = main_product.get("image")
                        if image:
                            vals['image_1920'] = image

                        product = product_obj.create(vals)
                        created_count += 1

                    # ================= VARIANTS (UNCHANGED) =================
                    for idx, item in enumerate(group_items):

                        attr_value = f"Variant {idx+1}"

                        attribute = self.env['product.attribute'].search([
                            ('name', '=', "Variant")
                        ], limit=1)

                        if not attribute:
                            attribute = self.env['product.attribute'].create({
                                'name': "Variant"
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

                        # ✅ VARIANT IMAGE
                        variant_record = self.env['product.product'].search([
                            ('product_tmpl_id', '=', product.id),
                            ('product_template_attribute_value_ids.product_attribute_value_id', '=', value.id)
                        ], limit=1)

                        if variant_record:
                            variant_image = item.get("image")
                            if variant_image:
                                variant_record.image_1920 = variant_image
                                _logger.warning(f"[EXCEL] VARIANT IMAGE SET → {group_id} | {value.name}")

            self.excel_created_index = end
            self.env.cr.commit()

            _logger.warning(f"[EXCEL] UPDATED CREATED INDEX → {end}")
            _logger.warning(f"TOTAL PRODUCTS CREATED (THIS RUN): {created_count}")

            return  # 🔥 CRITICAL → STOP BEFORE PDF

        # =====================================================
        # 🔥 PDF FLOW (FULL ORIGINAL — UNTOUCHED)
        # =====================================================
        for page_data in pages:

            page_no = page_data.get("page")
            ai_page = next((p for p in ai_pages if p.get("page") == page_no), None)

            if not ai_page:
                continue

            products = ai_page.get("products", [])
            images = page_data.get("images", [])

            _logger.warning(f"[PDF] IMAGES FOUND → {len(images)}")

            for product_data in products:

                try:
                    name = (product_data.get("name") or "").strip()
                    description = product_data.get("description", "")
                    raw_category = (product_data.get("category") or "").lower()
                    variants = product_data.get("variants", [])

                    variant_group = product_data.get("variant_group") or name
                    variant_group = str(variant_group).strip().upper()

                    category = category_obj.search([
                        ('name', '=', "General"),
                        ('parent_id', '=', parent_category.id)
                    ], limit=1)

                    if not category:
                        category = category_obj.create({
                            'name': "General",
                            'parent_id': parent_category.id
                        })

                    product = product_obj.search([
                        ('default_code', '=', variant_group)
                    ], limit=1)

                    if not product:
                        vals = {
                            'name': name,
                            'default_code': variant_group,
                            'description_sale': description,
                            'categ_id': category.id,
                            'sale_ok': True,
                            'website_published': False,
                        }

                        if images:
                            vals['image_1920'] = images[0]

                        product = product_obj.create(vals)
                        created_count += 1

                except Exception as e:
                    _logger.error(f"PDF PRODUCT FAILED → {str(e)}")

        self.env.cr.commit()

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

    #---------------- CRON ---------------
    def run_pending_jobs(self):

        # 🔥 STRICT STATE FILTER (ONLY ACTIVE STATES)
        active_states = [
            'draft', 'processing',
            'excel_parsing', 'excel_ai', 'excel_creating',
            'pdf_extracting', 'pdf_ai', 'pdf_creating',
            'url_scraping', 'url_ai', 'url_creating'
        ]

        # =====================================================
        # 🔥 REMOVE DUPLICATE UPLOADS (SAFE)
        # =====================================================
        jobs = self.search(
            [('state', 'in', active_states)],
            order="id desc"
        )

        _logger.warning(f"CRON → TOTAL ACTIVE JOBS → {len(jobs)}")

        seen = {}
        duplicates = self.env['vendor.import.job']

        for j in jobs:

            sig = j.upload_signature

            if not sig:
                continue

            if sig not in seen:
                seen[sig] = j
            else:
                if j.id > seen[sig].id:
                    duplicates |= seen[sig]
                    seen[sig] = j
                else:
                    duplicates |= j

        if duplicates:
            _logger.warning(f"CRON → REMOVING DUPLICATES → {len(duplicates)}")
            duplicates.unlink()

            # 🔥 CRITICAL: commit after deletion
            self.env.cr.commit()

        # =====================================================
        # 🔥 ALWAYS PICK LATEST JOB
        # =====================================================
        job = self.search(
            [('state', 'in', active_states)],
            order="id desc",
            limit=1
        )

        _logger.warning(f"CRON → Found {1 if job else 0} job")

        if not job:
            return

        _logger.warning(f"CRON → SELECTED JOB ID → {job.id}")
        _logger.warning(
            f"CRON → JOB INPUT → "
            f"excel={bool(job.excel_file)} "
            f"pdf={bool(job.pdf_file)} "
            f"url={bool(job.data_url)}"
        )

        # 🔒 LOCK CHECK
        if job.lock:
            _logger.warning(f"JOB {job.id} IS LOCKED → SKIP")
            return

        try:
            _logger.warning(f"CRON → START JOB {job.id}")
            job.lock = True
            self.env.cr.commit()  # 🔥 ensure lock is saved immediately

            job._process_step()

            # 🔥🔥🔥 MOST IMPORTANT FIX
            self.env.cr.commit()
            _logger.warning("CRON → STEP COMMITTED ✅")

        except Exception as e:
            _logger.exception(f"PROCESS FAILED → {str(e)}")
            job.state = 'failed'
            self.env.cr.commit()

        finally:
            job.lock = False
            self.env.cr.commit()
            _logger.warning("CRON → JOB UNLOCKED & COMMITTED 🔓")

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

            text = (item.get("text") or "").strip()
            image = item.get("image")

            # 🔥 STRICT VALIDATION
            if not text or len(text) < 5:
                continue

            if image and isinstance(image, str) and not image.startswith("http"):
                image = None

            blocks.append({
                "text": text,
                "image": image
            })

        _logger.warning(f"NORMALIZED BLOCKS → {len(blocks)}")

        # =====================================================
        # 🔥 SPLIT INTO MULTIPLE PAGES (CRITICAL FIX)
        # =====================================================

        PAGE_SIZE = 20  # 🔥 prevents AI overload

        pages = []

        for i in range(0, len(blocks), PAGE_SIZE):

            chunk = blocks[i:i + PAGE_SIZE]

            pages.append({
                "page": len(pages) + 1,
                "blocks": chunk
            })

        _logger.warning(f"NORMALIZED PAGES → {len(pages)}")

        return pages

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

        ACTOR_ID = "selectad~my-actor"

        # =====================================================
        # 🔥 STEP 1: START ACTOR (ONLY IF NOT STARTED)
        # =====================================================

        if not getattr(self, "apify_run_id", False):

            run_url = f"https://api.apify.com/v2/acts/{ACTOR_ID}/runs?token={token}"

            payload = {
                "startUrls": [{"url": url}]
            }

            headers = {
                "Content-Type": "application/json"
            }

            response = requests.post(run_url, json=payload, headers=headers, timeout=30)

            if response.status_code != 201:
                raise Exception(f"Apify run failed: {response.text}")

            run_data = response.json()

            # ✅ SAVE FOR NEXT CRON
            self.apify_run_id = run_data["data"]["id"]
            self.apify_dataset_id = run_data["data"]["defaultDatasetId"]

            _logger.warning(f"APIFY STARTED → RUN ID {self.apify_run_id}")

            # 🔥 IMPORTANT: STOP HERE (NON-BLOCKING)
            return None

        # =====================================================
        # 🔥 STEP 2: CHECK STATUS
        # =====================================================

        status_url = f"https://api.apify.com/v2/actor-runs/{self.apify_run_id}?token={token}"

        status_res = requests.get(status_url, timeout=20).json()
        status = status_res["data"]["status"]

        _logger.warning(f"APIFY STATUS → {status}")

        if status in ["RUNNING", "READY"]:
            _logger.warning("APIFY STILL RUNNING → WAIT NEXT CRON")
            return None

        if status in ["FAILED", "ABORTED", "TIMED-OUT"]:
            raise Exception(f"Apify run failed with status: {status}")

        # =====================================================
        # 🔥 STEP 3: FETCH DATA (ONLY WHEN DONE)
        # =====================================================

        dataset_url = f"https://api.apify.com/v2/datasets/{self.apify_dataset_id}/items"

        params = {
            "token": token,
            "limit": 1000,
            "clean": "true"
        }

        dataset_res = requests.get(dataset_url, params=params, timeout=30)

        if dataset_res.status_code != 200:
            raise Exception(f"Failed to fetch dataset: {dataset_res.text}")

        data = dataset_res.json()

        _logger.warning(f"APIFY ITEMS FETCHED → {len(data)}")

        if not data:
            raise Exception("Apify returned empty dataset")

        # 🔥 CLEAN UP (IMPORTANT)
        self.apify_run_id = False
        self.apify_dataset_id = False

        return data

    #=======validation===================
    def validate_ai_output(products):
        for p in products:
            if "variants" in p:
                if not isinstance(p["variants"], list):
                    p["variants"] = []

                for v in p["variants"]:
                    if "attributes" not in v:
                        v["attributes"] = {"Variant": "Default"}

        return products
    
    #=======keep cron alive================
    def keep_alive(self):
        _logger.warning("KEEP ALIVE PING")
    