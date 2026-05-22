from odoo import models
import logging

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):

    _inherit = 'product.product'


    def unlink(self):

        imported_products = self.filtered(
            lambda p:
                p.product_tmpl_id.vendor_import_job_id
        )

        if imported_products:

            try:

                _logger.warning(
                    f"[SAFE DELETE START] "
                    f"{imported_products.ids}"
                )

                # ====================================
                # RESET QUANT INVENTORY FIRST
                # ====================================

                quants = self.env[
                    'stock.quant'
                ].sudo().search([

                    (
                        'product_id',
                        'in',
                        imported_products.ids
                    )

                ])

                for quant in quants:

                    try:

                        quant.sudo().write({

                            'inventory_quantity': 0
                        })

                        quant.sudo().action_apply_inventory()

                    except Exception as e:

                        _logger.warning(
                            f"[QUANT RESET ERROR] "
                            f"{str(e)}"
                        )

                # ====================================
                # DELETE QUANTS
                # ====================================

                quants.unlink()

                # ====================================
                # DELETE MOVE LINES
                # ====================================

                self.env[
                    'stock.move.line'
                ].sudo().search([

                    (
                        'product_id',
                        'in',
                        imported_products.ids
                    )

                ]).unlink()

                # ====================================
                # DELETE MOVES
                # ====================================

                self.env[
                    'stock.move'
                ].sudo().search([

                    (
                        'product_id',
                        'in',
                        imported_products.ids
                    )

                ]).filtered(

                    lambda m:
                        m.state != 'done'

                ).unlink()

                _logger.warning(
                    "[SAFE DELETE COMPLETE]"
                )

            except Exception as e:

                _logger.warning(
                    f"[SAFE DELETE ERROR] "
                    f"{str(e)}"
                )

        return super().unlink()