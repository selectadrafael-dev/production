from odoo import models
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    # =====================================
    # FINAL PURGE ENGINE
    # =====================================

    def action_purge_imported_products(self):

        templates = self.filtered(
            lambda t: t.vendor_import_job_id
        )

        if not templates:
            return True

        _logger.warning(
            f"[PURGE TEMPLATES] {templates.ids}"
        )

        products = templates.mapped(
            'product_variant_ids'
        )

        # =====================================
        # INVENTORY LINES
        # =====================================

        inventory_lines = self.env[
            'stock.inventory.line'
        ].search([

            ('product_id', 'in', products.ids)

        ])

        _logger.warning(
            f"[PURGE INVENTORY LINES] "
            f"{inventory_lines.ids}"
        )

        inventory_lines.sudo().unlink()

        # =====================================
        # INVENTORY ADJUSTMENTS
        # =====================================

        inventories = self.env[
            'stock.inventory'
        ].search([

            ('line_ids.product_id', 'in', products.ids)

        ])

        _logger.warning(
            f"[PURGE INVENTORIES] "
            f"{inventories.ids}"
        )

        inventories.sudo().unlink()

        # =====================================
        # STOCK MOVE LINES
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
        # STOCK MOVES
        # =====================================

        moves = self.env[
            'stock.move'
        ].search([

            ('product_id', 'in', products.ids)

        ])

        _logger.warning(
            f"[PURGE MOVES] "
            f"{moves.ids}"
        )

        # CANCEL DONE MOVES
        for move in moves.filtered(
            lambda m: m.state == 'done'
        ):

            try:

                move._action_cancel()

            except Exception as e:

                _logger.warning(

                    f"[MOVE CANCEL FAILED] "
                    f"{move.id} => {str(e)}"
                )

        moves.sudo().unlink()

        # =====================================
        # VALUATION LAYERS
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
        # STOCK QUANTS
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
        # REORDER RULES
        # =====================================

        reorder_rules = self.env[
            'stock.warehouse.orderpoint'
        ].search([

            ('product_id', 'in', products.ids)

        ])

        _logger.warning(
            f"[PURGE REORDER RULES] "
            f"{reorder_rules.ids}"
        )

        reorder_rules.sudo().unlink()

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
            f"[PURGE TEMPLATES FINAL] "
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