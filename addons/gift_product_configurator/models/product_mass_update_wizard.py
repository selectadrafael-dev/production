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
            # INVENTORY
            # =====================

            if self.update_inventory:

                inventory_updated_count += 1

                # =====================
                # PRODUCT TYPE
                # =====================

                if self.update_track_inventory:

                    product.type = (
                        self.detailed_type
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

                if self.set_quantity:

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