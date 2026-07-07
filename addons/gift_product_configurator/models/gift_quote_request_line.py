# -*- coding: utf-8 -*-

from odoo import fields, models


class GiftQuoteRequestLine(models.Model):
    _name = "gift.quote.request.line"
    _description = "Website Quote Request Line"
    _order = "sequence, id"


    # ==========================================================
    # RELATION
    # ==========================================================

    request_id = fields.Many2one(
        "gift.quote.request",
        string="Quote Request",
        required=True,
        ondelete="cascade",
    )


    sequence = fields.Integer(
        default=10,
    )


    # ==========================================================
    # PRODUCT
    # ==========================================================

    product_id = fields.Many2one(
        "product.product",
        string="Product",
    )

    product_name = fields.Char()

    variant_name = fields.Char()

    colour = fields.Char()


    # ==========================================================
    # WEBSITE PRODUCT SNAPSHOT
    # ==========================================================

    sku = fields.Char(
        string="SKU",
    )

    product_url = fields.Char(
        string="Product URL",
    )

    tier_name = fields.Char(
        string="Tier Name",
    )


    # ==========================================================
    # QUANTITY
    # ==========================================================

    quantity = fields.Float(
        default=1,
    )


    # ==========================================================
    # PRICING
    # ==========================================================

    unit_price = fields.Float()

    original_price = fields.Float()

    discount = fields.Float()

    discount_amount = fields.Float()

    subtotal = fields.Float()

    currency = fields.Char()


    # ==========================================================
    # BRANDING
    # ==========================================================

    print_method = fields.Char()

    logo_colours = fields.Char()

    include_vat = fields.Boolean()

    artwork_required = fields.Boolean()

    source = fields.Char()

    fingerprint = fields.Char(
        index=True,
    )

    # ==========================================================
    # WEBSITE SNAPSHOT
    # ==========================================================

    product_image = fields.Char(
        string="Product Image URL",
    )

    tier_quantity = fields.Integer(
        string="Selected Tier",
    )

    variant_attributes = fields.Text(
        string="Variant Attributes",
    )

    vat_amount = fields.Float(
        string="VAT Amount",
    )

    total_price = fields.Float(
        string="Total Price",
    )

    configuration_json = fields.Json(
        string="Website Configuration",
    )


    # ==========================================================
    # AUDIT
    # ==========================================================






   
    