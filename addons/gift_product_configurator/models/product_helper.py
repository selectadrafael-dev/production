from odoo import models


class GiftingProductHelper(models.AbstractModel):
    _name = "gifting.product.helper"
    _description = "Gifting Product Helper"

    def get_latest_products(self, xml_id, limit):

        # ✅ FORCE WEBSITE LANGUAGE CONTEXT (CRITICAL)
        lang = self.env.context.get('lang')

        Product = self.env['product.template'].with_context(lang=lang)

        # =========================================
        # CATEGORY FETCH
        # =========================================
        category = self.env.ref(xml_id, raise_if_not_found=False)

        if not category:
            return Product.browse([])

        # =========================================
        # PRODUCTS SEARCH
        # =========================================
        products = Product.search(
            [
                ('public_categ_ids', 'in', category.id),
                ('website_published', '=', True),
            ],
            order='id desc',
            limit=limit
        )

        return products