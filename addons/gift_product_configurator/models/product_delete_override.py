from odoo import models
import logging

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):

    _inherit = 'product.product'


    def unlink(self):

        try:

            imported_products = self.filtered(
                lambda p:
                    p.product_tmpl_id.vendor_import_job_id
            )

            if imported_products:

                _logger.warning(
                    f"[SAFE DELETE] PRODUCTS={imported_products.ids}"
                )

                # ====================================
                # DELETE STOCK QUANTS
                # ====================================

                self.env['stock.quant'].sudo().search([

                    ('product_id', 'in', imported_products.ids)

                ]).unlink()

                # ====================================
                # DELETE MOVE LINES
                # ====================================

                self.env['stock.move.line'].sudo().search([

                    ('product_id', 'in', imported_products.ids)

                ]).unlink()

                # ====================================
                # DELETE STOCK MOVES
                # ====================================

                self.env['stock.move'].sudo().search([

                    ('product_id', 'in', imported_products.ids)

                ]).unlink()

                _logger.warning(
                    "[SAFE DELETE] STOCK CLEANED"
                )

        except Exception as e:

            _logger.warning(
                f"[SAFE DELETE ERROR] {str(e)}"
            )

        return super().unlink()