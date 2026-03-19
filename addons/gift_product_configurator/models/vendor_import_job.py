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

            self.extracted_text = self.extracted_text or ""

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

        self.extracted_text += text[:15000]


    # ---------------- EXCEL ----------------

    def parse_excel(self):

        import pandas as pd
        import io

        _logger.info("Parsing Excel")

        excel_bytes = base64.b64decode(self.excel_file)

        df = pd.read_excel(io.BytesIO(excel_bytes))

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

        prompt = f"""
        Extract ONLY product data and return valid JSON array.

        TEXT:
        {self.extracted_text}
        """

        try:

            _logger.info("Calling OpenAI API")

            response = client.responses.create(
                model="gpt-4.1-mini",
                input=prompt
            )

            result = response.output[0].content[0].text.strip()

            # CLEAN RESPONSE
            if result.startswith("```"):
                result = result.split("```")[1]

            if result.lower().startswith("json"):
                result = result[4:]

            result = result.strip()

            _logger.info("AI CLEANED RESPONSE: %s", result[:500])

            # SAFE JSON PARSE
            try:
                parsed = json.loads(result)
                self.ai_response = result
                _logger.info("OpenAI JSON parsed successfully")
            except Exception:
                _logger.error("Invalid JSON from OpenAI: %s", result[:500])
                raise Exception("AI response is not valid JSON")

        except Exception as e:

            _logger.error("OpenAI error: %s", str(e))

            if "quota" in str(e).lower():
                raise Exception("Billing issue detected")

            raise


    # ---------------- PRODUCT CREATION ----------------

    def create_product_drafts(self):

        if not self.ai_response:
            _logger.warning("No AI response found, skipping product creation")
            return

        product_obj = self.env['product.template']
        category_obj = self.env['product.category']

        try:
            data = json.loads(self.ai_response)
        except Exception:
            _logger.error("Invalid JSON, cannot create products")
            return

        for item in data:

            name = item.get("name", "Unnamed Product")
            description = item.get("description", "")
            category_name = item.get("category", "Uncategorized")

            category = category_obj.search([('name', '=', category_name)], limit=1)

            if not category:
                category = category_obj.create({'name': category_name})

            product = product_obj.create({
                'name': name,
                'description_sale': description,
                'categ_id': category.id,
                'sale_ok': True,
                'website_published': False,
            })

            _logger.info("Product created: %s", name)