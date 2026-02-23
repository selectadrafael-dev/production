from odoo import http
from odoo.http import request


class BestSellersPage(http.Controller):

    @http.route(['/bestsellers'], type='http', auth='public', website=True)
    def bestsellers(self, **kwargs):

        # Get category by name
        category = request.env['product.public.category'].sudo().search(
            [('name', '=', 'Best Selling Promotional Products')],
            limit=1
        )

        if not category:
            products = request.env['product.template']
        else:
            products = request.env['product.template'].sudo().search([
                ('is_published', '=', True),
                ('public_categ_ids', 'in', category.id),
            ])

        return request.render(
            'gift_product_configurator.bestsellers_page_template',
            {
                'products': products,
                'category': category,
            }
        )