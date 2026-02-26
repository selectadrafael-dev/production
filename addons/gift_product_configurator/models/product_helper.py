from odoo import models


class GiftingProductHelper(models.AbstractModel):
    _name = "gifting.product.helper"
    _description = "Gifting Product Helper"

    def get_latest_products(self, xml_id, limit):

        category = self.env.ref(xml_id, raise_if_not_found=False)
        if not category:
            return self.env['product.template']

        products = self.env['product.template'].search(
            [
                ('public_categ_ids', 'in', category.id),
                ('website_published', '=', True),
            ],
            order='id desc',
            limit=limit
        )

        return products