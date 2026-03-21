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

            # Ensure text exists
            self.extracted_text = self.extracted_text or ""

            # -------- DATA EXTRACTION --------
            if self.pdf_file:
                _logger.warning("STEP → Extracting PDF")
                self.extract_pdf()

            if self.excel_file:
                _logger.warning("STEP → Parsing Excel")
                self.parse_excel()

            if self.data_url:
                _logger.warning("STEP → Scraping URL")
                self.scrape_website()

            _logger.warning(f"TEXT LENGTH → {len(self.extracted_text or '')}")

            # -------- STOP IF NO TEXT --------
            if not self.extracted_text:
                _logger.error("NO TEXT EXTRACTED → STOPPING")
                self.state = "error"
                return

            # -------- TRACK PREVIOUS COUNT (BEFORE AI) --------
            previous_count = len(json.loads(self.ai_response or "[]"))
            _logger.warning(f"PREVIOUS COUNT → {previous_count}")

            # -------- OPENAI --------
            _logger.warning("STEP → Sending to OpenAI")
            self.send_to_openai()

            # -------- PRODUCT CREATION --------
            _logger.warning("STEP → Creating products")
            self.create_product_drafts()

            # -------- CHECK PROGRESS --------
            current_products = json.loads(self.ai_response or "[]")
            current_count = len(current_products)

            _logger.warning(f"CURRENT COUNT → {current_count}")

            # -------- SMART RETRY LOGIC --------
            if current_count == previous_count:
                _logger.warning("NO NEW PRODUCTS FOUND → STOPPING")
                self.state = "review"
            else:
                _logger.warning("NEW PRODUCTS FOUND → CONTINUE PROCESSING")
                self.state = "processing"

            _logger.warning(f"PROCESS END → Job {self.id}")

        except Exception as e:
            _logger.exception("PROCESS FAILED")
            self.state = "error"

    # ---------------- PDF ----------------

    def extract_pdf(self):

        import pdfplumber, io

        _logger.info("Extracting PDF")

        pdf_bytes = base64.b64decode(self.pdf_file)

        text = ""

        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                content = page.extract_text()
                if content:
                    text += content + "\n"

        self.extracted_text += text

    # ---------------- EXCEL ----------------

    def parse_excel(self):

        import pandas as pd
        import io

        _logger.info("Parsing Excel")

        excel_bytes = base64.b64decode(self.excel_file)

        try:
            df = pd.read_excel(io.BytesIO(excel_bytes))
        except Exception:
            df = pd.read_csv(io.BytesIO(excel_bytes))

        self.extracted_text += "\n" + df.to_string()

    # ---------------- URL ----------------

    def scrape_website(self):

        import requests
        from bs4 import BeautifulSoup

        _logger.info("Scraping URL: %s", self.data_url)

        try:
            r = requests.get(self.data_url, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")

            text = soup.get_text()

            self.extracted_text += "\n" + text[:10000]

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

        # -------- SPLIT TEXT --------
        def split_text(text, chunk_size=6000, overlap=500):
            chunks = []
            i = 0

            while i < len(text):
                chunk = text[i:i+chunk_size]
                chunks.append(chunk)
                i += chunk_size - overlap

            return chunks

        safe_text = (self.extracted_text or "")[:35000]
        chunks = split_text(safe_text)

        _logger.info(f"Processing {len(chunks)} chunks")

        all_products = []

        # -------- LOOP --------
        for chunk in chunks:

            prompt = f"""
            You are a HIGH PRECISION product extraction engine.

            TASK:
            Extract EVERY SINGLE product from the catalog text.

            STRICT RULES:
            - DO NOT skip any product
            - DO NOT merge products
            - EVEN similar products must be separate
            - If unsure → still include it
            - Extract ALL variants (size, color, version)
            - Do NOT summarize
            - If a page contains multiple products, extract ALL of them

            OUTPUT:
            Return ONLY JSON array.

            FORMAT:
            [
            {{
                "name": "",
                "description": "",
                "category": "",
                "material": "",
                "colors": []
            }}
            ]

            CRITICAL:
            - If 2 products look similar → treat them as DIFFERENT
            - If product appears twice → include once
            - MAXIMIZE product count, do NOT minimize

            TEXT:
            {chunk}
            """

            try:

                response = client.responses.create(
                    model="gpt-4.1-mini",
                    input=prompt,
                    timeout=60
                )

                result = response.output_text.strip()

                if result.startswith("```"):
                    result = result.split("```")[1]

                if result.lower().startswith("json"):
                    result = result[4:]

                result = result.strip()

                parsed = json.loads(result)
                _logger.warning(f"Parsed products count (chunk): {len(parsed) if isinstance(parsed, list) else 0}")

                if isinstance(parsed, list):
                    all_products.extend(parsed)

            except Exception as e:
                _logger.warning(f"Chunk failed: {str(e)}")
                continue

        # --------REMOVE DUPLICATES--------
        unique_products = {}

        for product in all_products:
            name = product.get("name", "").strip()
            if name and name not in unique_products:
                unique_products[name] = product
                _logger.warning(f"CREATING PRODUCT: {name}")

        final_products = list(unique_products.values())
        _logger.warning(f"FINAL PRODUCT COUNT: {len(final_products)}")

        #🔥 ADD THIS (FIRST)
        if not final_products:
            _logger.error("No products extracted from AI")
            raise Exception("No products extracted")

        #🔥 ADD THIS (SECOND)
        _logger.info(f"Final products ready: {len(final_products)}")

        #self.ai_response = json.dumps(final_products)
        existing = json.loads(self.ai_response or "[]")
        combined = existing + final_products

        # remove duplicates again
        unique = {}
        for p in combined:
            name = p.get("name", "").strip().lower()
            if name and name not in unique:
                unique[name] = p

        self.ai_response = json.dumps(list(unique.values()))
        _logger.warning(f"OpenAI RAW RESPONSE (first 300 chars): {result[:300]}")

        _logger.info(f"Total products extracted: {len(final_products)}")

    # ----------------PRODUCT CREATION----------------
        _logger.warning("ENTERED PRODUCT CREATION")
    def create_product_drafts(self):

        if not self.ai_response:
            _logger.warning("No AI response found")
            return

        product_obj = self.env['product.template']
        category_obj = self.env['product.category']

        try:
            data = json.loads(self.ai_response)
        except Exception:
            _logger.error("Invalid JSON")
            return

        # ✅ CORRECT LOCATION (INSIDE FUNCTION)
        _logger.info("Total products to create: %s", len(data))

        BATCH_SIZE = 100

        for i in range(0, len(data), BATCH_SIZE):

            batch = data[i:i+BATCH_SIZE]

            _logger.info("Processing batch %s", i//BATCH_SIZE + 1)

            for item in batch:

                name = item.get("name", "Unnamed Product")
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

                _logger.info("Product created: %s", name)
     
    #-------------async method in MODEL----------------------
    def _process_async(self):
        """Safe async fallback (no queue_job dependency)"""
        for rec in self:
            rec.process_import()

    #------Cron job to process pending vendor imports---------
    def run_pending_jobs(self):

        jobs = self.search([('state', '=', 'draft')])

        _logger.warning(f"CRON START → Found {len(jobs)} jobs")

        for job in jobs:
            try:
                _logger.warning(f"CRON → Processing job ID {job.id}")
                job.state = 'processing'
                job.process_import()

                _logger.warning(f"CRON → Job {job.id} completed successfully")

            except Exception as e:
                _logger.exception(f"CRON → Job {job.id} FAILED")
                job.state = 'error'
            """Cron job to process pending vendor imports"""

            jobs = self.search([('state', '=', 'draft')])

            _logger.info(f"CRON: Found {len(jobs)} jobs to process")

            for job in jobs:
                try:
                    _logger.info(f"CRON: Processing job {job.id}")
                    job.state = 'processing'
                    job.process_import()

                except Exception as e:
                    _logger.exception(f"CRON: Job {job.id} failed")
                    job.state = 'error'