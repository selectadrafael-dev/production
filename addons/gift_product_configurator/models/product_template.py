from odoo import models, fields
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

        imported = self.filtered(
            lambda p: p.vendor_import_job_id
        )

        normal = self - imported

        # =====================================
        # PURGE IMPORTED PRODUCTS
        # =====================================

        if imported:

            imported.action_purge_imported_products()

        # =====================================
        # NORMAL PRODUCTS
        # =====================================

        if normal:

            return super(
                ProductTemplate,
                normal
            ).unlink()

        return True