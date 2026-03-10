from odoo import models, fields

class CustomGiftingOrder(models.Model):
    _name = "custom.gifting.order"
    _description = "Custom Gifting Order"

    partner_id = fields.Many2one("res.partner")

    # customer info
    company_name = fields.Char()
    first_name = fields.Char(required=True)
    last_name = fields.Char(required=True)
    email = fields.Char(required=True)
    phone = fields.Char()
    telephone_extension = fields.Char()
    postcode = fields.Char()

    # product info
    product_id = fields.Many2one("product.product")
    product_name = fields.Char()
    product_image = fields.Char()  # url of product image
    product_price = fields.Float()
    quantity = fields.Integer()

    # customization
    print_colour = fields.Char()
    product_colour = fields.Char()

    # uploaded logo
    logo_file = fields.Binary("Customer Logo")
    logo_filename = fields.Char()

    # order info
    additional_information = fields.Text()
    order_required_by = fields.Date()

    purpose = fields.Selection(
        [
            ("large_qty_quote", "Large Quantity Quote"),
        ],
        default="large_qty_quote"
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted")
        ],
        default="draft"
    )