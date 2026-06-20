from odoo import models, fields

class ProductMassUpdateWizard(models.TransientModel):
    _name = 'product.mass.update.wizard'
    _description = 'Product Mass Update Wizard'

    test_field = fields.Char()