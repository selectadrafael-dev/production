from odoo import models, fields
import base64
import logging
import json

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

        import pdfplumber, io

        pdf_bytes = base64.b64decode(self.pdf_file)

        pages = []

        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for i, page in enumerate(pdf.pages):
                content = page.extract_text()

                if content:
                    pages.append({
                        "page": i + 1,
                        "text": content
                    })

        self.extracted_text = json.dumps(pages)

        _logger.warning(f"TOTAL PAGES → {len(pages)}")

    # ---------------- EXCEL ----------------

    def parse_excel(self):

        import pandas as pd
        import io

        excel_bytes = base64.b64decode(self.excel_file)

        try:
            df = pd.read_excel(io.BytesIO(excel_bytes))
        except Exception:
            df = pd.read_csv(io.BytesIO(excel_bytes))

        self.extracted_text = df.to_json()

    # ---------------- URL ----------------

    def scrape_website(self):

        import requests
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

        all_products = []

        for page in pages:

            page_no = page.get("page")
            text = page.get("text", "")

            if not text.strip():
                continue

            _logger.warning(f"AI → PAGE {page_no}")

            #old
            prompt = f"""
            You are a product extraction engine.

            Extract ALL products from this page.

            IMPORTANT:
            - Return ONLY valid JSON
            - Do NOT skip products
            - Do NOT merge products
            - Each product must be separate
            - Translate to English
            - Extract product image URL if available, else null
            - No explanation
            - No markdown
            - No text outside JSON
            - If no products found, return []


            FORMAT:
            [
            {{
                "name": "",
                "description": "",
                "category": "",
                "image_url": ""
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

                #result = response.output_text.strip()

                #parsed = json.loads(result)

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
                    all_products.extend(parsed)

            except Exception as e:
                _logger.warning(f"PAGE {page_no} FAILED → {str(e)}")
                continue

        # -------- REMOVE DUPLICATES --------
        unique = {}

        for p in all_products:
            name = p.get("name", "").strip().lower()
            if name and name not in unique:
                unique[name] = p

        final_products = list(unique.values())

        _logger.warning(f"FINAL PRODUCT COUNT → {len(final_products)}")

        if not final_products:
            raise Exception("No products extracted")

        self.ai_response = json.dumps(final_products)

    #---------------- PRODUCT CREATION ----------------

    def create_product_drafts(self):

        if not self.ai_response:
            return

        product_obj = self.env['product.template']
        category_obj = self.env['product.category']

        data = json.loads(self.ai_response)

        _logger.warning(f"CREATING {len(data)} PRODUCTS")

        for item in data:

            name = item.get("name", "Unnamed Product")

            # 🔥 PREVENT DUPLICATES
            existing = product_obj.search([('name', 'ilike', name)], limit=1)
            if existing:
                _logger.warning(f"SKIPPING DUPLICATE → {name}")
                continue

            description = item.get("description", "")
            category_name = item.get("category", "Uncategorized")

            category = category_obj.search([('name', '=', category_name)], limit=1)

            if not category:
                category = category_obj.create({'name': category_name})

            product_obj.create({
                'name': name,
                'description_sale': description,
                'categ_id': category.id,
                'sale_ok': True,
                'website_published': False,
            })

            _logger.info(f"Product created: {name}")

    # ---------------- CRON ----------------

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