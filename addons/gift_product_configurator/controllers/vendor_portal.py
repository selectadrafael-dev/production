from odoo import http
from odoo.http import request


class VendorProductsController(http.Controller):

    # =====================================================
    # VENDOR PRODUCTS LIST
    # =====================================================

    @http.route(
        ['/vendor/products'],
        type='json',
        auth='user',
        website=True
    )
    def vendor_products(
        self,
        page=1,
        limit=50,
        search=""
    ):

        partner = request.env.user.partner_id

        page = int(page)
        limit = int(limit)

        offset = (page - 1) * limit

        Product = request.env[
            'product.template'
        ].sudo()

        domain = [
            ('vendor_id', '=', partner.id)
        ]

        # =========================================
        # SEARCH
        # =========================================

        if search:

            domain.append(
                ('name', 'ilike', search)
            )

        total = Product.search_count(domain)

        _logger.warning(
            f"PRODUCT DOMAIN → {domain}"
        )
    

        products = Product.search(
            domain,
            limit=limit,
            offset=offset,
            order='id desc'
        )

        _logger.warning(
            f"FOUND PRODUCTS → "
            f"{len(products)}"
        )


        result = []

        for p in products:

            result.append({

                'id': p.id,

                'name': p.name,

                'image':
                    f'/web/image/product.template/'
                    f'{p.id}/image_1920',

            })

        return {

            'products': result,

            'total': total,

            'page': page,

            'limit': limit,

            'has_next':
                (offset + limit) < total,

            'has_prev':
                page > 1,
        }


    # =====================================================
    # PRODUCT DETAILS
    # =====================================================

    @http.route(
        ['/vendor/product/details'],
        type='json',
        auth='user',
        website=True
    )
    def vendor_product_details(
        self,
        product_id
    ):

        partner = request.env.user.partner_id
        import logging

        _logger = logging.getLogger(__name__)

        _logger.warning(
            f"PORTAL USER PARTNER ID → "
            f"{partner.id}"
        )


        product = request.env[
            'product.template'
        ].sudo().search([

            ('id', '=', int(product_id)),

            ('vendor_id', '=', partner.id)

        ], limit=1)

        if not product:

            return {
                'error': 'Product not found'
            }

        # =========================================
        # WARNING DETECTION
        # =========================================

        warning = False

        if (

            not product.image_1920

            or not product.name

            or product.list_price <= 1

            or not product.website_published

        ):

            warning = (

                'Provide full details for '

                'this product to make it '

                'publishable else it '

                'remain unpublished'

            )

        return {

            'id': product.id,

            'name': product.name or '',

            'description':
                product.description_sale or '',

            'price':
                product.list_price or 0,

            'category':
                product.categ_id.name or '',

            'published':
                product.website_published,

            'create_date':
                str(product.create_date),

            'image':
                f'/web/image/product.template/'
                f'{product.id}/image_1920',

            'warning':
                warning,
        }


    # =====================================================
    # UPDATE PRODUCT
    # =====================================================

    @http.route(
        ['/vendor/product/update'],
        type='json',
        auth='user',
        website=True
    )
    def vendor_product_update(
        self,
        **post
    ):

        partner = request.env.user.partner_id

        product = request.env[
            'product.template'
        ].sudo().search([

            (
                'id',
                '=',
                int(post.get('product_id'))
            ),

            (
                'vendor_id',
                '=',
                partner.id
            )

        ], limit=1)

        if not product:

            return {
                'error': 'Unauthorized'
            }

        vals = {

            'name':
                post.get('name'),

            'description_sale':
                post.get('description'),

            'list_price':
                float(
                    post.get('price') or 0
                ),
        }

        product.write(vals)

        return {
            'success': True
        }


    # =====================================================
    # DELETE PRODUCT
    # =====================================================

    @http.route(
        ['/vendor/product/delete'],
        type='json',
        auth='user',
        website=True
    )
    def vendor_product_delete(
        self,
        product_id
    ):

        partner = request.env.user.partner_id

        product = request.env[
            'product.template'
        ].sudo().search([

            ('id', '=', int(product_id)),

            ('vendor_id', '=', partner.id)

        ], limit=1)

        if not product:

            return {
                'error': 'Unauthorized'
            }

        product.unlink()

        return {
            'success': True
        }