from odoo import models
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def action_purge_imported_products(self):

        templates = self.filtered(
            lambda t: t.vendor_import_job_id
        )

        _logger.warning(
            f"[PURGE PRODUCTS] {templates.ids}"
        )

        products = templates.mapped(
            'product_variant_ids'
        )

        # =====================================
        # STOCK MOVES
        # =====================================

        moves = self.env['stock.move'].search([
            ('product_id', 'in', products.ids)
        ])

        _logger.warning(
            f"[PURGE MOVES FOUND] {moves.ids}"
        )

        # =====================================
        # RESET DONE MOVES
        # =====================================

        done_moves = moves.filtered(
            lambda m: m.state == 'done'
        )

        for move in done_moves:

            try:

                move._action_cancel()

            except Exception as e:

                _logger.warning(
                    f"[MOVE CANCEL FAILED] "
                    f"{move.id} => {str(e)}"
                )

        # =====================================
        # DELETE MOVE LINES
        # =====================================

        move_lines = self.env[
            'stock.move.line'
        ].search([

            ('product_id', 'in', products.ids)

        ])

        _logger.warning(
            f"[PURGE MOVE LINES] "
            f"{move_lines.ids}"
        )

        move_lines.sudo().unlink()

        # =====================================
        # DELETE MOVES
        # =====================================

        moves.sudo().unlink()

        # =====================================
        # DELETE VALUATION
        # =====================================

        valuation_layers = self.env[
            'stock.valuation.layer'
        ].search([

            ('product_id', 'in', products.ids)

        ])

        _logger.warning(
            f"[PURGE VALUATION] "
            f"{valuation_layers.ids}"
        )

        valuation_layers.sudo().unlink()

        # =====================================
        # DELETE QUANTS
        # =====================================

        quants = self.env[
            'stock.quant'
        ].search([

            ('product_id', 'in', products.ids)

        ])

        _logger.warning(
            f"[PURGE QUANTS] "
            f"{quants.ids}"
        )

        quants.sudo().unlink()

        # =====================================
        # DELETE VARIANTS
        # =====================================

        _logger.warning(
            f"[PURGE VARIANTS] "
            f"{products.ids}"
        )

        products.with_context(
            active_test=False
        ).sudo().unlink()

        # =====================================
        # DELETE TEMPLATES
        # =====================================

        _logger.warning(
            f"[PURGE TEMPLATES] "
            f"{templates.ids}"
        )

        templates.with_context(
            active_test=False
        ).sudo().unlink()

        self.env.cr.commit()

        _logger.warning(
            "[PURGE COMPLETE]"
        )

        return True