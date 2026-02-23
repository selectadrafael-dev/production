from odoo import http
from odoo.http import request

class BestSellerController(http.Controller):

    @http.route(['/bestsellers'], type='http', auth='public', website=True)
    def bestsellers(self, **kwargs):

        category = request.env['product.public.category'].sudo().search([
            ('name', '=', 'Best Selling Promotional Products')
        ], limit=1)

        return request.render(
            'gift_product_configurator.bestsellers_page',
            {
                'category': category,
            }
        )