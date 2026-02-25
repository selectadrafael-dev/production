from odoo import http
from odoo.http import request


class PromoController(http.Controller):

    @http.route('/promo/<int:cat_id>', type='http', auth='public', website=True)
    def promo_category(self, cat_id):

        category = request.env['product.public.category'].browse(cat_id)

        products = request.env['product.template'].search([
            ('public_categ_ids', 'in', category.id),
            ('website_published', '=', True),
        ])

        attributes = request.env['product.attribute'].search([])

        return request.render(
            'theme_gifting.promo_category_page',
            {
                'category': category,
                'products': products,
                'attributes': attributes,
            }
        )