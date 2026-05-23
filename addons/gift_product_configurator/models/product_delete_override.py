from odoo import models
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    #====== method====================
    def action_purge_imported_products(self):

        _logger.warning(
            f"[PURGE SELF IDS] {self.ids}"
        )

        templates = self

        for t in templates:

            _logger.warning(

                f"[PURGE TEMPLATE CHECK] "

                f"template={t.id} "

                f"name={t.name} "

                f"job={t.vendor_import_job_id.id}"
            )


        _logger.warning(
            f"[PURGE SELECTED TEMPLATES] {templates.ids}"
        )

        products = templates.mapped(
            'product_variant_ids'
        )

        # =====================================
        # DELETE STOCK QUANTS
        # =====================================

        quants = self.env['stock.quant'].search([

            ('product_id', 'in', products.ids)

        ])

        _logger.warning(
            f"[PURGE QUANTS] {quants.ids}"
        )

        quants.sudo().unlink()

        # =====================================
        # DELETE MOVE LINES
        # =====================================

        move_lines = self.env['stock.move.line'].search([

            ('product_id', 'in', products.ids)

        ])

        _logger.warning(
            f"[PURGE MOVE LINES] {move_lines.ids}"
        )

        move_lines.sudo().unlink()

        # =====================================
        # DELETE STOCK MOVES
        # =====================================


        moves = self.env['stock.move'].search([

            ('product_id', 'in', products.ids),

            ('state', '!=', 'done')

        ])

        _logger.warning(
            f"[PURGE MOVES] {moves.ids}"
        )

        moves.sudo().unlink()

        # =====================================
        # DELETE VARIANTS
        # =====================================

        _logger.warning(
            f"[PURGE VARIANTS] {products.ids}"
        )

        products.with_context(

            active_test=False

        ).sudo().unlink()

        # =====================================
        # DELETE TEMPLATES
        # =====================================

        _logger.warning(
            f"[PURGE TEMPLATES DELETE] {templates.ids}"
        )

        templates.with_context(

            active_test=False

        ).sudo().unlink()

        self.env.cr.commit()

        _logger.warning(
            "[PURGE COMPLETE]"
        )

        return True