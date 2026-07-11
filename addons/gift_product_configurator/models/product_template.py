from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    # =====================================
    # VENDOR FIELDS
    # =====================================

    vendor_id = fields.Many2one(
        'res.partner',
        string="Vendor"
    )

    vendor_fingerprint = fields.Char(
        index=True,
        copy=False
    )

    vendor_import_job_id = fields.Many2one(
        'vendor.import.job',
        string='Vendor Import Job',
        index=True,
        ondelete='set null'
    )

    vendor_stock_qty = fields.Integer()

    is_vendor_purged = fields.Boolean(
        default=False
    )

    vendor_price = fields.Float(
        string="Vendor Price"
    )

    vendor_currency_id = fields.Many2one(
        "res.currency",
        string="Vendor Currency"
    )

    # ==========================================================
    # WEBSITE PRICING
    # ==========================================================

    website_pricing_profile_id = fields.Many2one(
        "product.pricing.profile",
        string="Website Pricing Profile",
        tracking=True,
        copy=False,
    )

    pricing_tier_ids = fields.One2many(
        "product.pricing.tier",
        "product_tmpl_id",
        string="Website Pricing Tiers",
        copy=False,
    )

    pricing_tier_count = fields.Integer(
        string="Pricing Tiers",
        compute="_compute_pricing_tier_count",
    )

    pricing_profile_version = fields.Integer(
        readonly=True,
    )

    # ==========================================================
    # COMPUTE
    # ==========================================================

    @api.depends("pricing_tier_ids")
    def _compute_pricing_tier_count(self):

        for product in self:

            product.pricing_tier_count = len(

                product.pricing_tier_ids

            )

    # =====================================
    # AUTO ASSIGN VENDOR
    # =====================================

    @api.model
    def create(self, vals):

        user = self.env.user

        if (
            user.has_group(
                'gift_product_configurator.group_product_vendor'
            )
            and not vals.get('vendor_id')
        ):

            vals['vendor_id'] = (
                user.partner_id.id
            )

        return super().create(vals)

    # =====================================
    # DELETE INTERCEPT
    # =====================================

    def unlink(self):

        for template in self:

            # ==========================
            # ONLY IMPORTED PRODUCTS
            # ==========================

            if (
                not template.vendor_import_job_id
                and not template.vendor_id
            ):
                continue

            variants = template.product_variant_ids

            product_ids = variants.ids

            # =========================
            # MOVE LINES
            # =========================

            move_lines = self.env[
                'stock.move.line'
            ].sudo().search([

                ('product_id', 'in', product_ids)

            ])

            move_lines.unlink()

            # =========================
            # STOCK MOVES
            # =========================

            moves = self.env[
                'stock.move'
            ].sudo().search([

                ('product_id', 'in', product_ids),
                ('state', '!=', 'done')

            ])

            moves.unlink()

            # =========================
            # QUANTS ORM DELETE
            # =========================

            quants = self.env[
                'stock.quant'
            ].sudo().search([

                ('product_id', 'in', product_ids)

            ])

            quants.unlink()

            # =========================
            # FORCE SQL QUANT DELETE
            # =========================

            self.env.cr.execute("""

                DELETE FROM stock_quant
                WHERE product_id IN %s

            """, [tuple(product_ids or [0])])

            self.env.cr.commit()

            # =========================
            # VALUATION
            # =========================

            valuation = self.env[
                'stock.valuation.layer'
            ].sudo().search([

                ('product_id', 'in', product_ids)

            ])

            valuation.unlink()

        return super().unlink()
    
    #==========currency update logic 1===========
    @api.model
    def _convert_vendor_price(
        self,
        vendor_price,
        vendor_currency
    ):

        company = self.env.company

        company_currency = company.currency_id

        if (
            not vendor_currency
            or
            vendor_currency == company_currency
        ):
            return vendor_price

        converted_price = vendor_currency._convert(

            vendor_price,

            company_currency,

            company,

            fields.Date.today()
        )

        return converted_price
    
    #==========currency update logic 2===========
    def _update_converted_price(self):

        for product in self:

            if (
                not product.vendor_currency_id
                or
                not product.vendor_price
            ):
                continue

            converted_price = self._convert_vendor_price(

                product.vendor_price,

                product.vendor_currency_id
            )

            product.list_price = converted_price

            _logger.warning(

                f"[PRICE CONVERTED] "

                f"{product.name} "

                f"{product.vendor_price} "

                f"{product.vendor_currency_id.name} "

                f"-> "

                f"{converted_price} "

                f"{self.env.company.currency_id.name}"
            )

    # ==========================================================
    # APPLY WEBSITE PRICING PROFILE
    # ==========================================================

    def apply_website_pricing_profile(self):

        engine = self.env[
            "product.pricing.engine"
        ]

        for product in self:

            if not product.website_pricing_profile_id:
                continue

            engine.apply_profile(

                product,

                product.website_pricing_profile_id,

            )

        return True
    

    # ==========================================================
    # APPLY DEFAULT WEBSITE PROFILE
    # ==========================================================

    def apply_default_website_profile(
        self,
        owner=None,
    ):

        engine = self.env[
            "product.pricing.engine"
        ]

        for product in self:

            engine.apply_default_profile(

                product,

                owner,

            )

        return True


    # ==========================================================
    # REBUILD WEBSITE PRICING
    # ==========================================================

    def rebuild_website_pricing(self):
        """
        Rebuild website pricing tiers using the assigned
        pricing profile.

        This method is intentionally explicit so imports
        and bulk updates only rebuild pricing once.
        """

        for product in self:

            if product.website_pricing_profile_id:

                product.apply_website_pricing_profile()

        return True
    

    # ==========================================================
    # SET WEBSITE PRICING PROFILE
    # ==========================================================

    def set_website_pricing_profile(
        self,
        profile,
    ):

        self.ensure_one()

        self.website_pricing_profile_id = profile

        if profile:

            self.pricing_profile_version = profile.version

        return True
    
    # ==========================================================
    # CLEAR WEBSITE PRICING
    # ==========================================================

    def clear_website_pricing(self):

        for product in self:

            product.pricing_tier_ids.unlink()

        return True
    

    # ==========================================================
    # SYNC WEBSITE PRICING
    # ==========================================================

    def sync_website_pricing(self):
        """
        Synchronize website pricing using the Pricing Engine.

        If a pricing profile is already assigned to the product,
        it is used.

        Otherwise the engine automatically resolves the Vendor
        Default or Company Default profile.
        """

        Engine = self.env[
            "product.pricing.engine"
        ]

        for product in self:

            if product.website_pricing_profile_id:

                Engine.apply_profile(

                    product,

                    product.website_pricing_profile_id,

                )

            else:

                Engine.apply_default_profile(

                    product,

                )

        return True
    
    # ==========================================================
    # FINALIZE PRODUCT
    # ==========================================================

    def finalize_product(self):
        """
        Final processing after the product has been
        completely built.
        """

        for product in self:

            #
            # Refresh website selling price
            #

            if (
                product.vendor_price
                and
                product.vendor_currency_id
            ):

                product._update_converted_price()

            #
            # Generate website pricing only once
            #

            if not product.pricing_tier_ids:

                product.sync_website_pricing()

        return True
    
    # ==========================================================
    # WRITE
    # ==========================================================

    def write(self, vals):
        """
        Keep website pricing synchronized when
        important pricing fields change.
        """

        if self.env.context.get(
            "skip_pricing_sync"
        ):
            return super().write(vals)

        result = super().write(vals)

        pricing_fields = {

            "vendor_price",

            "vendor_currency_id",

            "website_pricing_profile_id",

        }

        if pricing_fields.intersection(vals.keys()):

            for product in self:

                try:

                    product.with_context(
                        skip_pricing_sync=True
                    ).sync_website_pricing()

                except Exception:

                    _logger.exception(

                        "[SYNC WEBSITE PRICING FAILED] "

                        "product=%s",

                        product.display_name,

                    )

        return result

    # ==========================================================
    # UPGRADE PRICING PROFILE
    # ==========================================================

    def upgrade_pricing_profile(self):

        for product in self:

            profile = product.website_pricing_profile_id

            if not profile:

                continue

            latest = self.env[
                "product.pricing.profile"
            ].search(

                [

                    ("name", "=", profile.name),

                    ("active", "=", True),

                ],

                order="version desc",

                limit=1,

            )

            if latest:

                product.set_website_pricing_profile(

                    latest

                )

                product.sync_website_pricing()

        return True
    
    # ==========================================================
    # WEBSITE PRICING JSON
    # ==========================================================

    def get_website_pricing_json(self):

        self.ensure_one()

        return [

            tier.get_website_json()

            for tier

            in self.pricing_tier_ids.sorted(

                key=lambda t:

                t.minimum_quantity

            )

        ]
    

    # ==========================================================
    # WEBSITE PRICING
    # ==========================================================

    def get_website_pricing(self):

        self.ensure_one()

        product = self.sudo()

        currency = (
            product.currency_id
            or self.env.company.currency_id
        )

        symbol = currency.symbol or ""

        result = []

        for tier in product.pricing_tier_ids.sorted(
            key=lambda t: t.minimum_quantity
        ):

            result.append({

                "sequence":
                    tier.sequence,

                "quantity":
                    tier.minimum_quantity,

                "discount":
                    tier.discount_percent,

                "price":
                    tier.unit_price,

                "formatted_price":
                    f"{symbol}{tier.unit_price:.2f}",

            })

        return result