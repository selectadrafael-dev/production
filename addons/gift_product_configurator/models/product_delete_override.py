from odoo import models
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):

    _inherit = 'product.template'


    def unlink(self):

        for template in self:

            # ONLY imported products
            if template.vendor_import_job_id:

                try:

                    variants = template.product_variant_ids

                    _logger.warning(
                        f"[SAFE DELETE] TEMPLATE={template.id}"
                    )

                    # =========================
                    # DELETE STOCK QUANTS
                    # =========================

                    self.env['stock.quant'].sudo().search([

                        ('product_id', 'in', variants.ids)

                    ]).unlink()

                    # =========================
                    # DELETE MOVE LINES
                    # =========================

                    self.env['stock.move.line'].sudo().search([

                        ('product_id', 'in', variants.ids)

                    ]).unlink()

                    # =========================
                    # DELETE STOCK MOVES
                    # =========================

                    self.env['stock.move'].sudo().search([

                        ('product_id', 'in', variants.ids)

                    ]).unlink()

                    # =========================
                    # DELETE VARIANTS
                    # =========================

                    variants.sudo().unlink()

                except Exception as e:

                    _logger.warning(
                        f"[SAFE DELETE ERROR] {str(e)}"
                    )

        return super().unlink()