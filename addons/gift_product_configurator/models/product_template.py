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

    vendor_price = fields.Float(
        string="Vendor Price"
    )

    vendor_currency_id = fields.Many2one(
        "res.currency",
        string="Vendor Currency"
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
    
    #==========currency update logic 1===========
    @api.model
    def _convert_vendor_price(
        self,
        vendor_price,
        vendor_currency
    ):

        company = self.env.company

        company_currency = company.currency_id

        if (
            not vendor_currency
            or
            vendor_currency == company_currency
        ):
            return vendor_price

        converted_price = vendor_currency._convert(

            vendor_price,

            company_currency,

            company,

            fields.Date.today()
        )

        return converted_price
    
    #==========currency update logic 2===========
    def _update_converted_price(self):

        for product in self:

            if (
                not product.vendor_currency_id
                or
                not product.vendor_price
            ):
                continue

            converted_price = self._convert_vendor_price(

                product.vendor_price,

                product.vendor_currency_id
            )

            product.list_price = converted_price

            _logger.warning(

                f"[PRICE CONVERTED] "

                f"{product.name} "

                f"{product.vendor_price} "

                f"{product.vendor_currency_id.name} "

                f"-> "

                f"{converted_price} "

                f"{self.env.company.currency_id.name}"
            )