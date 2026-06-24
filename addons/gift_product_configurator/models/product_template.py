from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    # =====================================
    # VENDOR FIELDS
    # =====================================

    vendor_id = fields.Many2one(
        'res.partner',
        string="Vendor"
    )

    vendor_fingerprint = fields.Char(
        index=True,
        copy=False
    )

    vendor_import_job_id = fields.Many2one(
        'vendor.import.job',
        string='Vendor Import Job',
        index=True,
        ondelete='set null'
    )

    vendor_stock_qty = fields.Integer()

    is_vendor_purged = fields.Boolean(
        default=False
    )

    vendor_currency_id = fields.Many2one(
        'res.currency',
        string="Vendor Currency",
        default=lambda self: self.env.company.currency_id.id
    )

    # =====================================
    # AUTO ASSIGN VENDOR
    # =====================================

    @api.model
    def create(self, vals):

        user = self.env.user

        if (
            user.has_group(
                'gift_product_configurator.group_product_vendor'
            )
            and not vals.get('vendor_id')
        ):

            vals['vendor_id'] = (
                user.partner_id.id
            )

        return super().create(vals)

    # =====================================
    # DELETE INTERCEPT
    # =====================================

    def unlink(self):

        for template in self:

            # ==========================
            # ONLY IMPORTED PRODUCTS
            # ==========================

            if (
                not template.vendor_import_job_id
                and not template.vendor_id
            ):
                continue

            variants = template.product_variant_ids

            product_ids = variants.ids

            # =========================
            # MOVE LINES
            # =========================

            move_lines = self.env[
                'stock.move.line'
            ].sudo().search([

                ('product_id', 'in', product_ids)

            ])

            move_lines.unlink()

            # =========================
            # STOCK MOVES
            # =========================

            moves = self.env[
                'stock.move'
            ].sudo().search([

                ('product_id', 'in', product_ids),
                ('state', '!=', 'done')

            ])

            moves.unlink()

            # =========================
            # QUANTS ORM DELETE
            # =========================

            quants = self.env[
                'stock.quant'
            ].sudo().search([

                ('product_id', 'in', product_ids)

            ])

            quants.unlink()

            # =========================
            # FORCE SQL QUANT DELETE
            # =========================

            self.env.cr.execute("""

                DELETE FROM stock_quant
                WHERE product_id IN %s

            """, [tuple(product_ids or [0])])

            self.env.cr.commit()

            # =========================
            # VALUATION
            # =========================

            valuation = self.env[
                'stock.valuation.layer'
            ].sudo().search([

                ('product_id', 'in', product_ids)

            ])

            valuation.unlink()

        return super().unlink()