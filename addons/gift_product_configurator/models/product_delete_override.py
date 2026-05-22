from odoo import models
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):

    _inherit = 'product.template'


    def action_purge_imported_products(self):

        try:

            imported_products = self.filtered(
                lambda p:
                    p.vendor_import_job_id
            )

            _logger.warning(

                f"[PURGE PRODUCTS] "

                f"{len(imported_products)}"
            )

            variants = imported_products.mapped(
                'product_variant_ids'
            )

            # =====================================
            # DELETE STOCK QUANTS
            # =====================================

            self.env[
                'stock.quant'
            ].sudo().search([

                (
                    'product_id',
                    'in',
                    variants.ids
                )

            ]).unlink()

            # =====================================
            # DELETE MOVE LINES
            # =====================================

            self.env[
                'stock.move.line'
            ].sudo().search([

                (
                    'product_id',
                    'in',
                    variants.ids
                )

            ]).unlink()

            # =====================================
            # DELETE DRAFT MOVES
            # =====================================

            self.env[
                'stock.move'
            ].sudo().search([

                (
                    'product_id',
                    'in',
                    variants.ids
                )

            ]).filtered(

                lambda m:
                    m.state != 'done'
            ).unlink()

            # =====================================
            # ARCHIVE FIRST
            # =====================================

            imported_products.write({

                'active': False
            })

            # =====================================
            # DELETE PRODUCTS
            # =====================================

            _logger.warning(
                "[PURGE COMPLETE]"
            )

            
            imported_products.unlink()
            self.env.cr.commit()

            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }

        except Exception as e:

            _logger.exception(

                f"[PURGE ERROR] "

                f"{str(e)}"
            )

            raise