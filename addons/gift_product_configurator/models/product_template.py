from odoo import models
from odoo.exceptions import UserError

class ProductTemplate(models.Model):

    _inherit = 'product.template'


    def unlink(self):

        imported = self.filtered(
            lambda p: p.vendor_import_job_id
        )

        normal = self - imported

        # =====================================
        # PURGE IMPORTED PRODUCTS SAFELY
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