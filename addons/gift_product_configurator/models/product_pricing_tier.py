# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProductPricingTier(models.Model):
    _name = "product.pricing.tier"
    _description = "Product Pricing Tier"
    _order = "sequence, minimum_quantity"

    # ==========================================================
    # PRODUCT
    # ==========================================================

    product_tmpl_id = fields.Many2one(
        "product.template",
        string="Product",
        required=True,
        ondelete="cascade",
        index=True,
    )

    # ==========================================================
    # SOURCE PROFILE
    # ==========================================================

    pricing_profile_id = fields.Many2one(
        "product.pricing.profile",
        string="Pricing Profile",
        readonly=True,
    )

    pricing_profile_name = fields.Char(
        readonly=True,
    )

    pricing_profile_version = fields.Integer(
        readonly=True,
    )

    generated_on = fields.Datetime(
        default=fields.Datetime.now,
        readonly=True,
    )

    generated_by = fields.Many2one(
        "res.users",
        default=lambda self: self.env.user,
        readonly=True,
    )

    # ==========================================================
    # ORDER
    # ==========================================================

    sequence = fields.Integer(
        default=10,
    )

    # ==========================================================
    # QUANTITY
    # ==========================================================

    minimum_quantity = fields.Integer(
        string="Minimum Quantity",
        required=True,
    )


    # ==========================================================
    # PRICING
    # ==========================================================

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )

    base_price = fields.Monetary(
        string="Base Price",
        currency_field="currency_id",
    )

    discount_percent = fields.Float(
        string="Discount (%)",
        required=True,
    )

    unit_price = fields.Monetary(
        string="Unit Price",
        currency_field="currency_id",
    )

    discount_amount = fields.Monetary(
        string="Discount Amount",
        currency_field="currency_id",
    )

    subtotal = fields.Monetary(
        string="Subtotal",
        currency_field="currency_id",
        compute="_compute_subtotal",
        store=True,
    )

    # ==========================================================
    # INFORMATION
    # ==========================================================

    notes = fields.Char()

    active = fields.Boolean(
        default=True,
    )

    pricing_profile_version = fields.Integer(
        readonly=True,
    )

    # ==========================================================
    # AUDIT
    # ==========================================================

    source = fields.Selection(
    [
            ("default", "Default"),
            ("profile", "Pricing Profile"),
            ("manual", "Manual"),
            ("import", "Importer"),
            ("mass_update", "Mass Update"),
        ],
        default="default",
        required=True,
    )

    # ==========================================================
    # SQL
    # ==========================================================

    _sql_constraints = [

        (

            "product_quantity_unique",

            "unique(product_tmpl_id, minimum_quantity)",

            "This quantity already exists for this product.",

        ),

    ]

    # ==========================================================
    # VALIDATION
    # ==========================================================

    @api.constrains(
        "minimum_quantity",
        "discount_percent",
    )
    def _check_values(self):

        for tier in self:

            if tier.minimum_quantity <= 0:

                raise ValidationError(

                    "Minimum quantity must be greater than zero."

                )

            if tier.discount_percent < 0:

                raise ValidationError(

                    "Discount cannot be negative."

                )

            if tier.discount_percent > 100:

                raise ValidationError(

                    "Discount cannot exceed 100%."

                )
            
    # ==========================================================
    # COMPUTE
    # ==========================================================

    @api.depends(
        "minimum_quantity",
        "unit_price",
    )
    def _compute_subtotal(self):

        for tier in self:

            tier.subtotal = (

                tier.minimum_quantity *

                tier.unit_price

            )

    # ==========================================================
    # PRICE CALCULATION
    # ==========================================================

    def calculate_price(self):

        for tier in self:

            tier.discount_amount = (

                tier.base_price *

                (

                    tier.discount_percent / 100.0

                )

            )

            tier.unit_price = (

                tier.base_price -

                tier.discount_amount

            )

    # ==========================================================
    # DISPLAY NAME
    # ==========================================================

    def name_get(self):

        result = []

        for tier in self:

            result.append(

                (

                    tier.id,

                    "%s+ → %s%%" % (

                        tier.minimum_quantity,

                        tier.discount_percent,

                    ),

                )

            )

        return result
    

    # ==========================================================
    # WEBSITE JSON
    # ==========================================================

    def get_website_json(self):

        self.ensure_one()

        return {

            "id": self.id,

            "qty": self.minimum_quantity,

            "discount": self.discount_percent,

            "price": self.unit_price,

            "currency": (

                self.currency_id.name

                if self.currency_id

                else ""

            ),

            "tier": "%s+" % (

                self.minimum_quantity

            ),

        }