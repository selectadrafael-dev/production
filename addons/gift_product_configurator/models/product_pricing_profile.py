# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ProductPricingProfile(models.Model):
    _name = "product.pricing.profile"
    _description = "Product Pricing Profile"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    # ==========================================================
    # INFORMATION
    # ==========================================================

    name = fields.Char(
        string="Profile Name",
        required=True,
        tracking=True,
    )

    active = fields.Boolean(
        default=True,
    )

    description = fields.Text()

    usage = fields.Selection(
        [
            ("website", "Website"),
            ("catalogue", "Catalogue Import"),
            ("promotional", "Promotional"),
            ("clearance", "Clearance"),
        ],
        string="Usage",
        default="website",
        required=True,
    )

    is_default = fields.Boolean(
        string="Default Profile",
        tracking=True,
    )

    version = fields.Integer(
        string="Version",
        default=1,
        readonly=True,
        tracking=True,
    )

    parent_profile_id = fields.Many2one(
        "product.pricing.profile",
        string="Previous Version",
        readonly=True,
        copy=False,
    )

    # ==========================================================
    # OWNERSHIP
    # ==========================================================

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
    )

    # ==========================================================
    # PRICING TIERS
    # ==========================================================

    tier_line_ids = fields.One2many(
        "product.pricing.profile.line",
        "profile_id",
        string="Pricing Tiers",
        copy=True,
    )

    # ==========================================================
    # PRODUCTS
    # ==========================================================

    product_count = fields.Integer(
        string="Products",
        compute="_compute_product_count",
    )

    # ==========================================================
    # OWNERSHIP
    # ==========================================================

    owner_partner_id = fields.Many2one(
        "res.partner",
        string="Owner",
        index=True,
        help="Vendor that owns this pricing profile.",
    )

    is_company_profile = fields.Boolean(
        string="Company Profile",
        default=False,
        help="Shared profile available to all vendors.",
    )

    # ==========================================================
    # COMPUTE
    # ==========================================================

    @api.depends()
    def _compute_product_count(self):

        Product = self.env["product.template"]

        for profile in self:

            profile.product_count = Product.search_count([
                (
                    "website_pricing_profile_id",
                    "=",
                    profile.id,
                )
            ])
    
    # ==========================================================
    # CREATE
    # ==========================================================

    @api.model_create_multi
    def create(self, vals_list):

        current_partner = self.env.user.partner_id

        for vals in vals_list:

            #
            # Automatically assign ownership
            # for vendor users.
            #

            if (

                not vals.get("owner_partner_id")

                and

                self.env.user.has_group(
                    "gift_product_configurator.group_product_vendor"
                )

            ):

                vals["owner_partner_id"] = current_partner.id

        profiles = super().create(vals_list)

        return profiles


    # ==========================================================
    # CONSTRAINTS
    # ==========================================================

    @api.constrains(
        "is_default",
        "owner_partner_id",
    )
    def _check_single_default_profile(self):

        for profile in self:

            if not profile.is_default:

                continue

            domain = [

                ("id", "!=", profile.id),

                ("is_default", "=", True),

                ("owner_partner_id", "=",
                 profile.owner_partner_id.id),

            ]

            existing = self.search_count(domain)

            if existing:

                raise ValidationError(

                    "Only one default pricing profile is allowed "
                    "per owner."

                )
            
    # ==========================================================
    # CREATE NEW VERSION
    # ==========================================================

    def create_new_version(self):

        self.ensure_one()

        new_profile = self.copy({

            "version": self.version + 1,

            "parent_profile_id": self.id,

            "is_default": False,

        })

        return new_profile
    
    # ==========================================================
    # CAN CURRENT USER EDIT
    # ==========================================================

    can_edit = fields.Boolean(
        compute="_compute_can_edit",
    )

    @api.depends(
        "owner_partner_id"
    )
    def _compute_can_edit(self):

        for profile in self:

            if self.env.user.has_group(
                "base.group_system"
            ):

                profile.can_edit = True

                continue

            partner = self.env.user.partner_id

            profile.can_edit = (

                profile.owner_partner_id == partner

            )
    
    # ==========================================================
    # WRITE
    # ==========================================================

    def write(self, vals):

        result = super().write(vals)

        rebuild_fields = {

            "name",

        }

        if rebuild_fields.intersection(

            vals.keys()

        ):

            self.rebuild_products()

        return result
    

    # ==========================================================
    # REBUILD PRODUCTS
    # ==========================================================

    def rebuild_products(self):

        PricingEngine = self.env[
            "product.pricing.engine"
        ]

        Product = self.env[
            "product.template"
        ]

        for profile in self:

            products = Product.search([

                (
                    "website_pricing_profile_id",
                    "=",
                    profile.id,
                )

            ])

            for product in products:

                try:

                    PricingEngine.apply_profile(

                        product,

                        profile,

                    )

                    product.sync_website_pricing()

                    _logger.info(

                        "[PROFILE REBUILD] "
                        "product=%s profile=%s",

                        product.display_name,

                        profile.name,

                    )

                except Exception:

                    _logger.exception(

                        "[PROFILE REBUILD FAILED] "
                        "product=%s",

                        product.display_name,

                    )

        return True