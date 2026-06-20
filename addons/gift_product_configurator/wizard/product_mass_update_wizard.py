from odoo import (
    api,
    fields,
    models
)

from odoo.exceptions import UserError

class ProductMassUpdateWizard(
    models.TransientModel
):
    _name = (
        "product.mass.update.wizard"
    )

    publish_products = fields.Boolean(
        string="Publish Products"
    )

    unpublish_products = fields.Boolean(
        string="Unpublish Products"
    )

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

    def action_apply(self):

        active_ids = self.env.context.get(
            "active_ids",
            []
        )

        if not active_ids:


            raise UserError(
                'No products were selected.'
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
        

        for product in products:

            if self.publish_products:

                product.is_published = True

                published_count += 1


            if self.unpublish_products:

                product.is_published = False

                unpublished_count += 1


            if self.update_price:

                current = (
                    product.list_price
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

                product.list_price = max(
                    0,
                    new_price
                )

                price_updated_count += 1


        return {
            'type': 'ir.actions.client',

            'tag': 'display_notification',

            'params': {

                'title':
                'Mass Update Complete',

                'message': (

                    f'Products Updated: '
                    f'{products_count}\n'

                    f'Published: '
                    f'{published_count}\n'

                    f'Unpublished: '
                    f'{unpublished_count}\n'

                    f'Prices Updated: '
                    f'{price_updated_count}'
                ),

                'type':
                'success',

                'sticky':
                True,
            },

            'next': {
                'type':
                'ir.actions.act_window_close'
            }
        }