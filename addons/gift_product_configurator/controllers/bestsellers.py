from odoo import http
from odoo.http import request


class BestSellersPage(http.Controller):

    @http.route(['/bestsellers'], type='http', auth='public', website=True)
    def bestsellers(self, **kwargs):

        website = request.website

        # Find category
        category = request.env['product.public.category'].sudo().search(
            [('name', '=', 'Best Selling Promotional Products')],
            limit=1
        )

        # Base domain: published on website
        domain = [
            ('is_published', '=', True),
            ('website_id', 'in', [False, website.id]),
        ]

        # Filter by category if found
        if category:
            domain.append(('public_categ_ids', 'in', category.id))

        products = request.env['product.template'].sudo().search(domain)

        return request.render(
            'gift_product_configurator.bestsellers_page_template',
            {
                'products': products,
                'category': category,
            }
        )