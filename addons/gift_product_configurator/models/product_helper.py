from odoo import models


class WebsiteProductHelper(models.AbstractModel):
    _name = 'gifting.product.helper'
    _description = 'Gifting Product Helper'

    def get_latest_products(self, category_xml_id, limit=7):

        category = self.env.ref(category_xml_id, raise_if_not_found=False)

        if not category:
            return self.env['product.template']

        return self.env['product.template'].search(
            [
                ('public_categ_ids', 'in', category.id),
                ('website_published', '=', True),   # ⭐ REQUIRED
                ('sale_ok', '=', True),             # ⭐ optional but recommended
            ],
            order='create_date desc',
            limit=limit
        )