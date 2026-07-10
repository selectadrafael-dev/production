# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductMassUpdatePricingLine(
    models.TransientModel
):
    _name = (
        "product.mass.update.pricing.line"
    )

    _description = (
        "Mass Update Pricing Line"
    )

    # ==========================================================
    # RELATIONSHIP
    # ==========================================================

    wizard_id = fields.Many2one(

        "product.mass.update.wizard",

        required=True,

        ondelete="cascade",

    )

    # ==========================================================
    # TIER
    # ==========================================================

    sequence = fields.Integer(

        default=10,

    )

    minimum_quantity = fields.Integer(

        required=True,

    )

    discount_percent = fields.Float(

        digits=(16, 2),

    )

    notes = fields.Char()

    preview_price = fields.Float(
        string="Estimated Price",
        compute="_compute_preview_price",
    )