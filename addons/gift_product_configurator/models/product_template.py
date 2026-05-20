from odoo import models


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    def unlink(self):

        imported_products = self.filtered(
            lambda p: p.vendor_import_job_id
        )

        normal_products = self - imported_products

        # =====================================
        # CLEAN IMPORTED PRODUCT INVENTORY
        # =====================================

        for product in imported_products:

            variants = product.product_variant_ids

            self.env['stock.quant'].search([

                (
                    'product_id',
                    'in',
                    variants.ids
                )

            ]).unlink()

            self.env['stock.move.line'].search([

                (
                    'product_id',
                    'in',
                    variants.ids
                )

            ]).unlink()

            self.env['stock.move'].search([

                (
                    'product_id',
                    'in',
                    variants.ids
                )

            ]).unlink()

        # =====================================
        # DELETE IMPORTED PRODUCTS
        # =====================================

        result = super(

            ProductTemplate,
            imported_products

        ).unlink()

        # =====================================
        # NORMAL PRODUCTS
        # =====================================

        if normal_products:

            result = super(

                ProductTemplate,
                normal_products

            ).unlink()

        return result