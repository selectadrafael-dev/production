from odoo import models, fields

raise Exception(
    "PRODUCT MASS UPDATE WIZARD FILE IS BEING IMPORTED"
)

class ProductMassUpdateWizard(models.TransientModel):
    _name = "product.mass.update.wizard"

    test_field = fields.Char()