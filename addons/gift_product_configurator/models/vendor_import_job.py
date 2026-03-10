from odoo import models, fields
import base64


class VendorImportJob(models.Model):

    _name = "vendor.import.job"
    _description = "Vendor Import Job"

    name = fields.Char(default="Vendor Data Import")

    data_url = fields.Char()

    extra_info = fields.Text()

    pdf_file = fields.Binary()

    excel_file = fields.Binary()

    logo_file = fields.Binary()

    state = fields.Selection([
        ('draft','Draft'),
        ('processing','Processing'),
        ('review','Vendor Review'),
        ('done','Completed')
    ], default='draft')


    def process_import(self):

        self.state = "processing"

        if self.pdf_file:
            self.extract_pdf()

        if self.excel_file:
            self.parse_excel()

        if self.data_url:
            self.scrape_website()

        self.create_product_drafts()

        self.state = "review"


    # -------------------------
    # PDF Extraction
    # -------------------------

    def extract_pdf(self):

        _logger = self.env['ir.logging']

        _logger.create({
            'name': 'Vendor Import',
            'type': 'server',
            'level': 'INFO',
            'message': 'PDF extraction placeholder executed',
            'path': 'vendor_import_job',
            'line': '0',
            'func': 'extract_pdf',
        })


    # -------------------------
    # Excel Parsing
    # -------------------------

    def parse_excel(self):

        _logger = self.env['ir.logging']

        _logger.create({
            'name': 'Vendor Import',
            'type': 'server',
            'level': 'INFO',
            'message': 'Excel parsing placeholder executed',
            'path': 'vendor_import_job',
            'line': '0',
            'func': 'parse_excel',
        })


    # -------------------------
    # Website Scraping
    # -------------------------

    def scrape_website(self):

        _logger = self.env['ir.logging']

        _logger.create({
            'name': 'Vendor Import',
            'type': 'server',
            'level': 'INFO',
            'message': 'Website scraping placeholder executed',
            'path': 'vendor_import_job',
            'line': '0',
            'func': 'scrape_website',
        })


    # -------------------------
    # Product Draft Creation
    # -------------------------

    def create_product_drafts(self):

        product_obj = self.env['product.template']

        product_obj.create({
            'name': 'Imported Vendor Product (Draft)',
            'sale_ok': False,
            'website_published': False,
        })