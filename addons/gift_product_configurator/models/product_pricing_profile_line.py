# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProductPricingProfileLine(models.Model):
    _name = "product.pricing.profile.line"
    _description = "Product Pricing Profile Line"
    _order = "sequence, minimum_quantity"

    # ==========================================================
    # PROFILE
    # ==========================================================

    profile_id = fields.Many2one(
        "product.pricing.profile",
        string="Pricing Profile",
        required=True,
        ondelete="cascade",
        index=True,
    )

    sequence = fields.Integer(
        default=10,
    )

    # ==========================================================
    # PRICING
    # ==========================================================

    minimum_quantity = fields.Integer(
        string="Minimum Quantity",
        required=True,
        tracking=True,
    )

    discount_percent = fields.Float(
        string="Discount (%)",
        required=True,
        tracking=True,
    )

    # ==========================================================
    # INFORMATION
    # ==========================================================

    notes = fields.Char(
        string="Notes",
    )

    active = fields.Boolean(
        default=True,
    )

    # ==========================================================
    # SQL CONSTRAINTS
    # ==========================================================

    _sql_constraints = [

        (
            "profile_quantity_unique",

            "unique(profile_id, minimum_quantity)",

            "The same minimum quantity cannot appear twice in the same pricing profile.",

        ),

    ]

    # ==========================================================
    # VALIDATION
    # ==========================================================

    @api.constrains(
        "minimum_quantity",
        "discount_percent",
    )
    def _check_pricing_values(self):

        for line in self:

            if line.minimum_quantity <= 0:

                raise ValidationError(

                    "Minimum quantity must be greater than zero."

                )

            if line.discount_percent < 0:

                raise ValidationError(

                    "Discount percentage cannot be negative."

                )

            if line.discount_percent > 100:

                raise ValidationError(

                    "Discount percentage cannot exceed 100%."

                )

    # ==========================================================
    # DISPLAY NAME
    # ==========================================================

    def name_get(self):

        result = []

        for line in self:

            name = "%s+  →  %s%%" % (

                line.minimum_quantity,

                line.discount_percent,

            )

            result.append(

                (

                    line.id,

                    name,

                )

            )

        return result

    # ==========================================================
    # COPY
    # ==========================================================

    def copy(self, default=None):

        default = dict(default or {})

        default.setdefault(
            "sequence",
            self.sequence,
        )

        return super().copy(default)

    # ==========================================================
    # DEFAULT ORDERING
    # ==========================================================

    @api.model_create_multi
    def create(self, vals_list):

        records = super().create(vals_list)

        for record in records:

            siblings = record.profile_id.tier_line_ids.sorted(
                key=lambda r: (
                    r.minimum_quantity,
                    r.sequence,
                )
            )

            seq = 10

            for line in siblings:

                line.sequence = seq

                seq += 10

        return records
    
    # ==========================================================
    # WRITE
    # ==========================================================

    def write(self, vals):

        result = super().write(vals)

        self.mapped(

            "pricing_profile_id"

        ).rebuild_products()

        return result