from odoo import models, fields

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