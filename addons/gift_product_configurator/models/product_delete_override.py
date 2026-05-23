from odoo import models
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):

    _inherit = 'product.template'


    def action_delete_imported_products(self):

        try:

            products = self.filtered(
                lambda p:
                    p.vendor_import_job_id
            )

            _logger.warning(
                f"[PURGE PRODUCTS] "
                f"{products.ids}"
            )

            _logger.warning(
                f"[PURGE SELF IDS] {self.ids}"
            )

            for p in self:

                _logger.warning(

                    f"[PURGE CHECK] "

                    f"product={p.id} "

                    f"name={p.name} "

                    f"job={p.vendor_import_job_id.id if p.vendor_import_job_id else None}"
                )

            if not products:

                _logger.warning(
                    "[PURGE EMPTY]"
                )

                return {
                    'type': 'ir.actions.client',
                    'tag': 'reload',
                }

            variants = products.mapped(
                'product_variant_ids'
            )

            # =====================================
            # DELETE STOCK QUANTS
            # =====================================

            quants = self.env[
                'stock.quant'
            ].sudo().search([

                (
                    'product_id',
                    'in',
                    variants.ids
                )

            ])

            _logger.warning(
                f"[PURGE QUANTS] "
                f"{quants.ids}"
            )

            quants.unlink()

            # =====================================
            # DELETE MOVE LINES
            # =====================================

            move_lines = self.env[
                'stock.move.line'
            ].sudo().search([

                (
                    'product_id',
                    'in',
                    variants.ids
                )

            ])

            move_lines.unlink()

            # =====================================
            # DELETE DRAFT MOVES
            # =====================================

            moves = self.env[
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
            )

            moves.unlink()

            # =====================================
            # ARCHIVE
            # =====================================

            products.write({
                'active': False
            })

            # =====================================
            # DELETE
            # =====================================

            products.unlink()

            _logger.warning(
                "[PURGE COMPLETE]"
            )

        except Exception as e:

            _logger.exception(
                f"[PURGE ERROR] {str(e)}"
            )

            raise

        self.env.cr.commit()

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }