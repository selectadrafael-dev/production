from odoo import models


class ProductTemplate(models.Model):

    _inherit = 'product.template'


    def unlink(self):

        for template in self:

            # =====================================
            # ONLY IMPORTED PRODUCTS
            # =====================================

            if not template.vendor_import_job_id:
                continue

            variants = template.product_variant_ids

            # =====================================
            # DELETE STOCK MOVE LINES
            # =====================================

            move_lines = self.env[
                'stock.move.line'
            ].search([

                ('product_id', 'in', variants.ids)
            ])

            move_lines.unlink()

            # =====================================
            # DELETE STOCK MOVES
            # =====================================

            moves = self.env[
                'stock.move'
            ].search([

                ('product_id', 'in', variants.ids)
            ])

            moves.unlink()

            # =====================================
            # DELETE STOCK QUANTS
            # =====================================

            quants = self.env[
                'stock.quant'
            ].search([

                ('product_id', 'in', variants.ids)
            ])

            quants.unlink()

            # =====================================
            # DELETE VALUATION
            # =====================================

            valuation = self.env[
                'stock.valuation.layer'
            ].search([

                ('product_id', 'in', variants.ids)
            ])

            valuation.unlink()

        return super().unlink()