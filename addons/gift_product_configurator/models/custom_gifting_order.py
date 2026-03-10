# -*- coding: utf-8 -*-

from odoo import models, fields


class CustomGiftingOrder(models.Model):
    _name = "custom.gifting.order"
    _description = "Custom Gifting Order"

    # Customer Information
    company_name = fields.Char()
    first_name = fields.Char(required=True)
    last_name = fields.Char(required=True)

    email = fields.Char(required=True)
    phone = fields.Char()

    postcode = fields.Char()

    quantity = fields.Integer()

    additional_information = fields.Text()

    order_required_by = fields.Date()

    partner_id = fields.Many2one("res.partner")

    # Quote Type
    purpose = fields.Char(default="large_qty_quote")

    state = fields.Selection([
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("quoted", "Quoted"),
        ("won", "Won"),
        ("lost", "Lost")
    ], default="submitted")

    # Uploaded Logo
    logo = fields.Binary("Uploaded Logo")
    logo_filename = fields.Char()

    # Order Lines
    line_ids = fields.One2many(
        "custom.gifting.order.line",
        "order_id",
        string="Quote Products"
    )


class CustomGiftingOrderLine(models.Model):
    _name = "custom.gifting.order.line"
    _description = "Custom Gifting Order Line"

    order_id = fields.Many2one(
        "custom.gifting.order",
        required=True,
        ondelete="cascade"
    )

    product_name = fields.Char()

    product_image = fields.Char()

    product_price = fields.Float()

    quantity = fields.Integer(default=1)