from odoo import http
from odoo.http import request


class BestSellersController(http.Controller):

    @http.route('/bestsellers', type='http', auth='public', website=True)
    def bestsellers_page(self, **kwargs):

        category = request.env['product.public.category'].sudo().search([
            ('name', '=', 'Best Selling Promotional Products')
        ], limit=1)

        products = request.env['product.template'].sudo().search([
            ('public_categ_ids', 'in', category.ids),
            ('website_published', '=', True),
        ])

        return request.render(
            'gift_product_configurator.bestsellers_template',
            {
                'products': products,
                'category': category
            }
        )