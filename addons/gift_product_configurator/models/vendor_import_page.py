from odoo import models, fields


class VendorImportPage(models.Model):

    _name = 'vendor.import.page'

    _description = 'Vendor Import PDF Pages'


    job_id = fields.Many2one(
        'vendor.import.job',
        ondelete='cascade'
    )

    page_number = fields.Integer()

    extracted_json = fields.Text()
    
    page_images_json = fields.Text()
