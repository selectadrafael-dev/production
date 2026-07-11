# -*- coding: utf-8 -*-

from odoo import api, fields, models
import logging


class ProductPricingEngine(models.AbstractModel):
    _name = "product.pricing.engine"
    _description = "Product Pricing Engine"

        # ==========================================================
    # APPLY PROFILE
    # ==========================================================

    def apply_profile(
        self,
        product,
        profile,
    ):

        """
        Apply a pricing profile to a product.

        Existing pricing tiers are removed.

        New pricing tiers are copied from the profile.

        Unit prices are calculated using the
        product's current selling price.
        """

        if not product or not profile:
            return False

        ProductTier = self.env[
            "product.pricing.tier"
        ]

        #
        # Remove previous tiers
        #

        product.clear_website_pricing()

        #
        # Current base selling price
        #

        base_price = self._get_base_price(product)

        currency = (
            product.currency_id
            or self.env.company.currency_id
        )

        #
        # Copy profile lines
        #

        for line in profile.tier_line_ids.sorted(
            key=lambda l: l.minimum_quantity
        ):

            discount_amount = (

                base_price *

                (

                    line.discount_percent / 100.0

                )

            )

            unit_price = (

                base_price -

                discount_amount

            )

            ProductTier.create({

                "product_tmpl_id":

                    product.id,

                "pricing_profile_id":

                    profile.id,

                "sequence":

                    line.sequence,

                "minimum_quantity":

                    line.minimum_quantity,

                "discount_percent":

                    line.discount_percent,

                "currency_id":

                    currency.id,

                "base_price":

                    base_price,

                "discount_amount":

                    discount_amount,

                "unit_price":

                    unit_price,

                "source":

                    "profile",

                "notes":

                    line.notes,
                
                "pricing_profile_name":
                    profile.name,

                "pricing_profile_version":
                    profile.version,

            })

        return True
    

    # ==========================================================
    # APPLY DEFAULT PROFILE
    # ==========================================================

    def apply_default_profile(
        self,
        product,
        owner=None,
    ):
        """
        Apply the default pricing profile for an owner.

        Owner may be:

            • res.partner
            • Vendor record (any model with partner_id)
            • None

        Search order:

            1. Owner's default profile
            2. Company shared default profile
        """

        if not product:
            return False

        partner = False

        # ------------------------------------------------------
        # Resolve owner
        # ------------------------------------------------------

        if owner:

            if owner._name == "res.partner":

                partner = owner

            elif hasattr(owner, "partner_id"):

                partner = owner.partner_id

        # ------------------------------------------------------
        # Find default profile
        # ------------------------------------------------------

        Profile = self.env[
            "product.pricing.profile"
        ]

        profile = False

        #
        # Vendor default
        #

        if partner:

            profile = Profile.search(

                [

                    ("owner_partner_id", "=", partner.id),

                    ("is_default", "=", True),

                    ("active", "=", True),

                ],

                limit=1,

            )

        #
        # Company default
        #

        if not profile:

            profile = Profile.search(

                [

                    ("owner_partner_id", "=", False),

                    ("is_default", "=", True),

                    ("active", "=", True),

                ],

                limit=1,

            )

        #
        # Nothing configured
        #


        if not profile:

            self._build_default_pricing(

                product,

            )

            return True

        #
        # Apply profile
        #

        return self.apply_profile(

            product,

            profile,

        )

    # ==========================================================
    # BUILD DEFAULT PRICING
    # ==========================================================

    def _build_default_pricing(
        self,
        product,
    ):
        """
        Build default website pricing when
        no pricing profile exists.

        Every quantity tier uses the
        product's current selling price.
        """

        Tier = self.env[
            "product.pricing.tier"
        ]

        #
        # Remove existing tiers
        #

        product.clear_website_pricing()

        base_price = self._get_base_price(
            product
        )

        _logger.warning(
            "[DEFAULT PRICING] Product=%s Base Price=%s",
            product.display_name,
            base_price,
        )

        currency = (
            product.currency_id
            or self.env.company.currency_id
        )

        #
        # Default quantities
        #

        default_quantities = [

            1000,
            2000,
            3000,
            4000,

        ]

        sequence = 10

        for qty in default_quantities:

            _logger.warning(
                "[DEFAULT PRICING] Creating tier Qty=%s Price=%s",
                qty,
                base_price,
            )

            Tier.create({

                "product_tmpl_id":
                    product.id,

                "sequence":
                    sequence,

                "minimum_quantity":
                    qty,

                "discount_percent":
                    0,

                "base_price":
                    base_price,

                "discount_amount":
                    0,

                "unit_price":
                    base_price,

                "currency_id":
                    currency.id,

                "source":
                    "default",

                "notes":
                    "Automatic default pricing",

            })

            sequence += 10

        _logger.warning(
            "[DEFAULT PRICING] Creating tier Qty=%s Price=%s",
            qty,
            base_price,
        )
        
        return True

    # ==========================================================
    # CONVERT PRICE
    # ==========================================================

    def convert_price(
        self,
        amount,
        from_currency,
        to_currency=None,
        exchange_rate=None,
    ):
        """
        Convert one amount into the target currency.

        If exchange_rate is supplied it takes precedence.

        Otherwise Odoo currency conversion is used.
        """

        if amount is None:
            return 0.0

        if not to_currency:
            to_currency = self.env.company.currency_id

        #
        # Manual exchange rate
        #

        if exchange_rate:

            return round(
                amount * exchange_rate,
                2,
            )

        #
        # Same currency
        #

        if from_currency == to_currency:

            return round(
                amount,
                2,
            )

        #
        # Odoo conversion
        #

        company = self.env.company

        return from_currency._convert(

            amount,

            to_currency,

            company,

            fields.Date.today(),

        )

    # ==========================================================
    # GET CURRENT EXCHANGE RATE
    # ==========================================================

    def get_exchange_rate(

        self,

        from_currency,

        to_currency=None,

    ):

        if not to_currency:

            to_currency = self.env.company.currency_id

        if from_currency == to_currency:

            return 1

        company = self.env.company

        return from_currency._get_conversion_rate(

            from_currency,

            to_currency,

            company,

            fields.Date.today(),

        )
    
    # ==========================================================
    # GET BASE PRICE
    # ==========================================================

    def _get_base_price(
        self,
        product,
    ):
        """
        Returns the website base selling price used
        for all pricing calculations.

        Future enhancements:
            - Vendor currency conversion
            - Markup rules
            - Regional pricing
            - Promotional overrides
        """

        product.ensure_one()

        return product.list_price