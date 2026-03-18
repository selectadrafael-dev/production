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
        ('draft','Draft'),
        ('processing','Processing'),
        ('ai_processing','AI Processing'),
        ('review','Vendor Review'),
        ('done','Completed'),
        ('error','Error')
    ], default='draft')


    # ---------------- MAIN FLOW ----------------

    def process_import(self):

        self.state = "processing"

        try:

            if self.pdf_file:
                self.extract_pdf()

            if self.excel_file:
                self.parse_excel()

            if self.data_url:
                self.scrape_website()

            if self.extracted_text:
                self.send_to_openai()

            self.create_product_drafts()

            self.state = "review"

        except Exception as e:
            _logger.exception("Processing failed")
            self.state = "error"


    # ---------------- PDF EXTRACTION ----------------

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

        self.extracted_text = text[:15000]

        _logger.info("PDF extraction done")


    # ---------------- EXCEL PARSING ----------------

    def parse_excel(self):

        import pandas as pd
        import io

        _logger.info("Parsing Excel")

        excel_bytes = base64.b64decode(self.excel_file)

        df = pd.read_excel(io.BytesIO(excel_bytes))

        self.extracted_text += df.to_string()

        _logger.info("Excel parsing done")


    # ---------------- URL SCRAPING ----------------

    def scrape_website(self):

        import requests
        from bs4 import BeautifulSoup

        _logger.info("Scraping URL: %s", self.data_url)

        try:
            r = requests.get(self.data_url, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")

            text = soup.get_text()

            self.extracted_text += text[:10000]

        except Exception as e:
            _logger.warning("URL scraping failed")


    # ---------------- OPENAI ----------------

    def send_to_openai(self):

        from openai import OpenAI

        self.state = "ai_processing"

        api_key = self.env['ir.config_parameter'].sudo().get_param('openai.api.key')

        if not api_key:
            raise Exception("OpenAI API key not configured")

        client = OpenAI(api_key=api_key)

        prompt = f"""
        You are an AI data extraction engine.

        TASK:
        Extract ONLY product information from the provided catalog or scraped website text.

        STRICT RULES:
        - Ignore navigation menus, headers, footers, and non-product text
        - Focus only on actual products
        - Translate ALL content to English
        - Return ONLY valid JSON (no explanation, no text outside JSON)

        OUTPUT FORMAT:
        Return a JSON array of products.

        Each product must contain:

        - name (string)
        - description (string)
        - category (string)
        - material (string, if available)
        - colors (array of strings, if available)

        IMPORTANT:
        - If a field is missing, return an empty string or empty array
        - Do NOT invent data
        - Do NOT include duplicate products

        TEXT:
        {self.extracted_text}
        """

        try:

            _logger.info("Calling OpenAI API")

            response = client.responses.create(
                model="gpt-4.1-mini",
                input=prompt
            )

            result = response.output[0].content[0].text

            self.ai_response = result

            json.loads(result)

            _logger.info("OpenAI processing successful")

        except Exception as e:

            _logger.error("OpenAI error: %s", str(e))

            if "quota" in str(e).lower():
                raise Exception("Billing issue detected")

            raise


    # ---------------- PRODUCT CREATION ----------------

    def create_product_drafts(self):

        product_obj = self.env['product.template']

        product_obj.create({
            'name': 'Imported Vendor Product (Draft)',
            'sale_ok': False,
            'website_published': False,
        })