from odoo import (
    api,
    fields,
    models
)

from odoo.exceptions import UserError


import logging

_logger = logging.getLogger(__name__)

_logger.warning(
    "MASS UPDATE WIZARD FILE LOADED"
)


class ProductMassUpdateWizard( models.TransientModel):

    _name = "product.mass.update.wizard"

    _description = ("Product Mass Update Wizard")

    # =========================
    # PUBLISHING
    # =========================

    publish_products = fields.Boolean(
        string="Publish Products"
    )

    unpublish_products = fields.Boolean(
        string="Unpublish Products"
    )

    # =========================
    # PRICING
    # =========================

    update_price = fields.Boolean(
        string="Update Prices"
    )

    update_method = fields.Selection(
        [
            (
                "fixed",
                "Fixed Amount"
            ),
            (
                "percentage",
                "Percentage"
            )
        ],
        default="fixed"
    )

    operation = fields.Selection(
        [
            (
                "set",
                "Set Price"
            ),
            (
                "increase",
                "Increase"
            ),
            (
                "decrease",
                "Decrease"
            )
        ],
        default="set"
    )

    value = fields.Float()

    # ==========================================================
    # PRICING ACTION
    # ==========================================================

    pricing_action = fields.Selection(
        [
            ("apply", "Apply Pricing Profile"),
            ("rebuild", "Rebuild Existing Pricing"),
            ("upgrade", "Upgrade To Latest Version"),
            ("clear", "Clear Pricing"),
        ],
        string="Pricing Action",
        default="apply",
    )

    selected_product_count = fields.Integer(
        compute="_compute_selected_product_count",
    )

    pricing_tier_count = fields.Integer(
        compute="_compute_pricing_tier_count",
    )

    estimated_tier_records = fields.Integer(
        compute="_compute_estimated_tier_records",
    )

    # ==========================================================
    # WEBSITE PRICING
    # ==========================================================

    pricing_mode = fields.Selection(

        [

            ("existing", "Use Existing Profile"),

            ("create", "Create New Profile"),

            ("edit", "Edit Existing Profile"),

        ],

        string="Pricing Mode",

        default="existing",

    )

    pricing_profile_id = fields.Many2one(

        "product.pricing.profile",

        string="Pricing Profile",

        domain=[],

    )

    new_profile_name = fields.Char(

        string="New Profile Name",

    )

    pricing_line_ids = fields.One2many(

        "product.mass.update.pricing.line",

        "wizard_id",

        string="Pricing Lines",

    )

    # =========================
    # WEBSITE CATEGORY
    # =========================

    update_category = fields.Boolean(
        string="Update Website Categories"
    )

    public_category_ids = fields.Many2many(
        "product.public.category",
        string="Website Categories"
    )

    # =========================
    # INVENTORY
    # =========================

    update_inventory = fields.Boolean(
    string="Update Inventory Settings"
    )

    update_track_inventory = fields.Boolean(
        string="Update Inventory Tracking"
    )

    track_inventory_value = fields.Boolean(
        string="Track Inventory",
        default=True
    )

    warehouse_id = fields.Many2one(
        "stock.warehouse",
        string="Warehouse",
        default=lambda self:
        self.env[
            "stock.warehouse"
        ].search(
            [],
            limit=1
        )
    )

    set_quantity = fields.Boolean(
        string="Set Stock Quantity"
    )

    quantity = fields.Float(
        string="Quantity"
    )

    detailed_type = fields.Selection(
        [
            (
                "consu",
                "Goods"
            ),
            (
                "service",
                "Service"
            ),
            (
                "combo",
                "Combo"
            )
        ],
        string="Product Type",
        default="consu"
    )

    update_sale_ok = fields.Boolean(
        string="Update Can Be Sold"
    )

    sale_ok = fields.Boolean(
        string="Can Be Sold"
    )

    update_purchase_ok = fields.Boolean(
        string="Update Can Be Purchased"
    )

    purchase_ok = fields.Boolean(
        string="Can Be Purchased"
    )

    tracking = fields.Selection(
        [
            (
                "none",
                "No Tracking"
            ),
            (
                "lot",
                "By Lots"
            ),
            (
                "serial",
                "By Serial Number"
            )
        ],
        string="Tracking"
    )

    show_available_qty = fields.Boolean(
        string="Show Available Quantity"
    )

    available_threshold = fields.Integer(

        string="Only Show Below",

        default=100000,

        help="Website will display available quantity only when stock is below this value."

    )

    continue_selling = fields.Boolean(
        string="Continue Selling When Out Of Stock"
    )

    route_ids = fields.Many2many(
        "stock.route",
        string="Routes"
    )

    update_currency = fields.Boolean()

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        domain=[
            (
                'name',
                'in',
                [
                    'USD',
                    'AZN',
                    'RUB'
                ]
            )
        ]
    )

    # ==========================================================
    # COMPUTE
    # ==========================================================
    @api.depends("pricing_profile_id")
    def _compute_pricing_tier_count(self):

        for wizard in self:

            wizard.pricing_tier_count = len(
                wizard.pricing_profile_id.tier_line_ids
            )
    

    def _compute_selected_product_count(self):

        for wizard in self:

            wizard.selected_product_count = len(

                wizard.env.context.get(
                    "active_ids",
                    []
                )

            )

    # ==========================================================
    # ONCHANGE
    # ==========================================================

    @api.onchange(
        "pricing_mode"
    )
    def _onchange_pricing_mode(self):

        partner = self.env.user.partner_id

        return {

            "domain": {

                "pricing_profile_id": [

                    "|",

                    ("is_company_profile", "=", True),

                    ("owner_partner_id", "=", partner.id),

                ]

            }

        }
    
    @api.onchange(
        "pricing_profile_id"
    )
    def _onchange_pricing_profile(self):

        self.pricing_line_ids = [

            (5, 0, 0)

        ]

        if (

            not self.pricing_profile_id

        ):

            return

        lines = []

        for line in (

            self.pricing_profile_id

            .tier_line_ids

            .sorted(

                key=lambda l: l.sequence

            )

        ):

            lines.append(

                (

                    0,

                    0,

                    {

                        "sequence":

                            line.sequence,

                        "minimum_quantity":

                            line.minimum_quantity,

                        "discount_percent":

                            line.discount_percent,

                        "notes":

                            line.notes,

                    }

                )

            )

        self.pricing_line_ids = lines

    
    # ==========================================================
    # CREATE PROFILE
    # ==========================================================

    def _create_pricing_profile(self):

        self.ensure_one()

        Profile = self.env[

            "product.pricing.profile"

        ]

        profile = Profile.create({

            "name":

                self.new_profile_name,

            "owner_partner_id":

                self.env.user.partner_id.id,

            "active":

                True,

        })

        for line in self.pricing_line_ids:

            self.env[

                "product.pricing.profile.line"

            ].create({

                "pricing_profile_id":

                    profile.id,

                "sequence":

                    line.sequence,

                "minimum_quantity":

                    line.minimum_quantity,

                "discount_percent":

                    line.discount_percent,

                "notes":

                    line.notes,

            })

        return profile
    
    # ==========================================================
    # UPDATE PROFILE
    # ==========================================================

    def _update_pricing_profile(

        self,

        profile,

    ):

        profile.tier_line_ids.unlink()

        for line in self.pricing_line_ids:

            self.env[

                "product.pricing.profile.line"

            ].create({

                "pricing_profile_id":

                    profile.id,

                "sequence":

                    line.sequence,

                "minimum_quantity":

                    line.minimum_quantity,

                "discount_percent":

                    line.discount_percent,

                "notes":

                    line.notes,

            })

    # ==========================================================
    # REBUILD PROFILE PRODUCTS
    # ==========================================================

    def _rebuild_profile_products(
        self,
        profile,
     ):
        """
        Rebuild website pricing for every product
        using this pricing profile.
        """

        if not profile:
            return

        products = self.env[
            "product.template"
        ].search([

            (
                "website_pricing_profile_id",
                "=",
                profile.id,
            )

        ])

        PricingEngine = self.env[
            "product.pricing.engine"
        ]

        for product in products:

            try:

                PricingEngine.apply_profile(

                    product,

                    profile,

                )

                product.sync_website_pricing()

                _logger.info(

                    "[PROFILE REBUILD] "

                    "product=%s "

                    "profile=%s",

                    product.display_name,

                    profile.name,

                )

            except Exception:

                _logger.exception(

                    "[PROFILE REBUILD FAILED] "

                    "product=%s",

                    product.display_name,

                )

    # ==========================================================
    # REBUILD PRODUCTS
    # ==========================================================

    def rebuild_products(self):

        PricingEngine = self.env[
            "product.pricing.engine"
        ]

        for profile in self:

            products = self.env[
                "product.template"
            ].search([

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

                except Exception:

                    _logger.exception(

                        "[PROFILE REBUILD FAILED] "

                        "product=%s",

                        product.display_name,

                    )

    # =========================
    # ACTION
    # =========================
    def action_apply(self):

        active_ids = self.env.context.get(
            "active_ids",
            []
        )

        if not active_ids:

            raise UserError(
                "No products were selected."
            )
        
        if (
            self.publish_products
            and
            self.unpublish_products
        ):

            raise UserError(
                "You cannot select both "
                "Publish and Unpublish."
            )

        products = self.env[
            "product.template"
        ].browse(
            active_ids
        )

        products_count = len(
            products
        )

        published_count = 0

        unpublished_count = 0

        price_updated_count = 0

        category_updated_count = 0

        inventory_updated_count = 0

        quantity_updated_count = 0

        tier_updated_count = 0

        for product in products:

            # =====================
            # PUBLISHING
            # =====================

            if (
                self.publish_products
                and
                not product.is_published
            ):

                product.is_published = True

                published_count += 1

            if (
                self.unpublish_products
                and
                product.is_published
            ):

                product.is_published = False

                unpublished_count += 1

            # =====================
            # CATEGORY
            # =====================

            if self.update_category:

                _logger.warning(
                    "CATEGORY UPDATE: %s",
                    self.public_category_ids.ids
                )

                product.public_categ_ids = [
                    (
                        6,
                        0,
                        self.public_category_ids.ids
                    )
                ]

                category_updated_count += 1

            # =====================
            # TRACK INVENTORY
            # =====================

            inventory_vals = {}

            # --------------------------------------------------
            # Inventory Tracking
            # --------------------------------------------------

            if self.update_track_inventory:

                if self.track_inventory_value:

                    inventory_vals.update({

                        "type": "consu",

                        "is_storable": True,

                    })

                else:

                    inventory_vals.update({

                        "type": "service",

                        "is_storable": False,

                        "tracking": "none",

                    })

            # --------------------------------------------------
            # Website Availability
            # --------------------------------------------------

            if self.show_available_qty:

                inventory_vals.update({

                    "show_availability": True,

                    "available_threshold": self.available_threshold,

                })

            else:

                inventory_vals.update({

                    "show_availability": False,

                })
           
            # --------------------------------------------------
            # Apply Inventory Changes
            # --------------------------------------------------

            if inventory_vals:

                product.write(inventory_vals)

                _logger.warning(

                    "[MASS INVENTORY UPDATE] "

                    f"product={product.name} | "

                    f"type={inventory_vals.get('type')} | "

                    f"is_storable={inventory_vals.get('is_storable')} | "

                    f"show_availability={inventory_vals.get('show_availability')} | "

                    f"available_threshold={inventory_vals.get('available_threshold')}"

                )

                # =====================
                # SALES
                # =====================

                if self.update_sale_ok:

                    product.sale_ok = (
                        self.sale_ok
                    )

                # =====================
                # PURCHASE
                # =====================

                if self.update_purchase_ok:

                    product.purchase_ok = (
                        self.purchase_ok
                    )

                # =====================
                # LOT / SERIAL TRACKING
                # =====================

                if self.tracking:

                    product.tracking = (
                        self.tracking
                    )

                # =====================
                # ROUTES
                # =====================

                if self.route_ids:

                    product.route_ids = [
                        (
                            6,
                            0,
                            self.route_ids.ids
                        )
                    ]

                # =====================
                # WEBSITE STOCK DISPLAY
                # =====================

                product.show_availability = (
                    self.show_available_qty
                )

                product.allow_out_of_stock_order = (
                    self.continue_selling
                )

                # =====================
                # STOCK QUANTITY
                # =====================

                if (

                        self.set_quantity

                        and

                        product.detailed_type == "consu"

                    ):

                    warehouse = self.warehouse_id

                    if not warehouse:

                        raise UserError(
                            "Please select a warehouse."
                        )

                    location = (
                        warehouse.lot_stock_id
                    )

                    variant = (
                        product.product_variant_id
                    )

                    quant = self.env[
                        "stock.quant"
                    ]

                    current_qty = (
                        quant._get_available_quantity(
                            variant,
                            location
                        )
                    )

                    difference = (
                        self.quantity
                        -
                        current_qty
                    )

                    quant._update_available_quantity(
                        variant,
                        location,
                        difference
                    )

                    quantity_updated_count += 1

            # =================================
            # PRICE
            # =================================

            if self.update_price:

                current = (
                    product.vendor_price
                    if product.vendor_price
                    else product.list_price
                )

                if (
                    self.update_method
                    == "fixed"
                ):

                    if (
                        self.operation
                        == "set"
                    ):

                        new_price = (
                            self.value
                        )

                    elif (
                        self.operation
                        == "increase"
                    ):

                        new_price = (
                            current
                            +
                            self.value
                        )

                    else:

                        new_price = (
                            current
                            -
                            self.value
                        )

                else:

                    if (
                        self.operation
                        == "increase"
                    ):

                        new_price = (
                            current
                            *
                            (
                                1
                                +
                                (
                                    self.value
                                    /
                                    100
                                )
                            )
                        )

                    elif (
                        self.operation
                        == "decrease"
                    ):

                        new_price = (
                            current
                            *
                            (
                                1
                                -
                                (
                                    self.value
                                    /
                                    100
                                )
                            )
                        )

                    else:

                        new_price = (
                            self.value
                        )


                product.vendor_price = max(
                    0,
                    new_price
                )

                if (
                    self.update_currency
                    and
                    self.currency_id
                ):
                    product.vendor_currency_id = self.currency_id

                product._update_converted_price()

                _logger.warning(

                    f"[MASS PRICE UPDATE] "

                    f"product={product.name} "

                    f"vendor_price={product.vendor_price} "

                    f"currency={product.vendor_currency_id.name} "

                    f"list_price={product.list_price}"
                )

                price_updated_count += 1

            # =================================
            # WEBSITE PRICING ENGINE
            # =================================

            if self.pricing_action:

                profile = False

                # ------------------------------------------
                # USE EXISTING PROFILE
                # ------------------------------------------

                if (

                    self.pricing_mode
                    == "existing"

                ):

                    profile = self.pricing_profile_id

                # ------------------------------------------
                # CREATE NEW PROFILE
                # ------------------------------------------

                elif (

                    self.pricing_mode
                    == "create"

                ):

                    profile = self._create_pricing_profile()

                # ------------------------------------------
                # EDIT EXISTING PROFILE
                # ------------------------------------------

                elif (

                    self.pricing_mode
                    == "edit"

                ):

                    profile = self.pricing_profile_id

                    if profile:

                        #
                        # SECURITY
                        #

                        if (

                            not profile.is_company_profile

                            and

                            profile.owner_partner_id

                            !=

                            self.env.user.partner_id

                            and

                            not self.env.user.has_group(
                                "base.group_system"
                            )

                        ):

                            raise UserError(

                                _(

                                    "You can only edit "

                                    "your own pricing profiles."

                                )

                            )


                        self._update_pricing_profile(
                            profile
                        )

                        #
                        # Rebuild every product
                        #

                        self._rebuild_profile_products(
                            profile
                        )

                # ------------------------------------------
                # APPLY PROFILE
                # ------------------------------------------

                if profile:

                    PricingEngine = self.env[
                        "product.pricing.engine"
                    ]

                    for product in products:

                        #
                        # Assign profile
                        #

                        product.website_pricing_profile_id = (

                            profile.id

                        )

                        #
                        # Build website pricing
                        #

                        PricingEngine.apply_profile(

                            product,

                            profile,

                        )

                        #
                        # Synchronize website price
                        #

                        product.sync_website_pricing()

                        _logger.info(

                            "[PRICING PROFILE APPLIED] "

                            "product=%s "

                            "profile=%s",

                            product.display_name,

                            profile.name,

                        )

   
        return {

            "type":
            "ir.actions.client",

            "tag":
            "display_notification",

            "params": {

                "title":
                "Mass Update Complete",

                "message": (

                    f"Products Updated: "
                    f"{products_count}\n"

                    f"Published: "
                    f"{published_count}\n"

                    f"Unpublished: "
                    f"{unpublished_count}\n"

                    f"Prices Updated: "
                    f"{price_updated_count}\n"

                    f"Categories Updated: "
                    f"{category_updated_count}\n"

                    f"Inventory Updated: "
                    f"{inventory_updated_count}\n"

                    f"Stock Quantities Updated: "
                    f"{quantity_updated_count}"

                    f"Website Pricing Updated: "
                    f"{tier_updated_count}\n"
                ),

                "type":
                "success",

                "sticky":
                False,
            },

            "next": {

                "type":
                "ir.actions.act_window_close"
            }
        }
    
