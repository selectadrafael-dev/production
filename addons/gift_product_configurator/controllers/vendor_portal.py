from odoo import http
from odoo.http import request


class VendorProductsController(http.Controller):

    @http.route(
        ['/vendor/products'],
        type='json',
        auth='user',
        website=True
    )
    def vendor_products(self, page=1, limit=50):

        partner = request.env.user.partner_id

        offset = (page - 1) * limit

        Product = request.env['product.template'].sudo()

        domain = [
            ('vendor_id', '=', partner.id)
        ]

        total = Product.search_count(domain)

        products = Product.search(
            domain,
            limit=limit,
            offset=offset,
            order='id desc'
        )

        result = []

        for p in products:

            result.append({
                'id': p.id,
                'name': p.name,
                'image': f'/web/image/product.template/{p.id}/image_1920',
            })

        return {
            'products': result,
            'total': total,
            'page': page,
            'limit': limit,
            'has_next': (offset + limit) < total,
            'has_prev': page > 1,
        }