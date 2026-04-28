import logging

from odoo import http
from odoo.http import request


_logger = logging.getLogger(__name__)



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

            _logger.warning(

                f"PRODUCT {p.id} | "

                f"TEMPLATE IMAGE → "

                f"{bool(p.image_1920)} | "

                f"VARIANT IMAGE → "

                f"{bool(p.product_variant_id.image_1920)}"
            )


            result.append({

                'id': p.id,

                'name': p.name,
                'image': (
                    f'/vendor/product/image/{p.id}'
                ),
 
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
    # def vendor_product_details(
    #     self,
    #     product_id
    # ):


    def vendor_product_details(

        self,

        product_id=None,

        **kwargs
    ):
        
        try:

            product_id = int(product_id)

        except Exception:

            return {
                'error': 'Invalid product ID'
            }
    

        partner = request.env.user.partner_id
        import logging

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

        _logger.warning(
            f"FOUND PRODUCT → {product}"
        )


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

            # 'image': (

            #     f'/web/image?model=product.template'
            #     f'&id={p.id}'
            #     f'&field=image_128'
            # ),

        
            'image': (
                f'/vendor/product/image/{product.id}'
            ),

            'warning':
                warning,
        }

 
    # =======================================================
    # UPDATE PRODUCT
    # =======================================================

    @http.route(
        ['/vendor/product/update'],
        type='json',
        auth='user',
        website=True
    )
    def vendor_product_update(

        self,

        product_id=None,

        name=None,

        description=None,

        price=None,

        **kwargs
    ):

        partner = request.env.user.partner_id


        try:

            product_id = int(product_id)

        except Exception:

            return {
                'error': 'Invalid product ID'
            }


        product = request.env[
            'product.template'
        ].sudo().search([

            ('id', '=', product_id),

            ('vendor_id', '=', partner.id)

        ], limit=1)


        if not product:

            return {
                'error': 'Unauthorized'
            }


        vals = {

            'name': name or '',

            'description_sale':
                description or '',

            'list_price':
                float(price or 0),
        }

        if kwargs.get('image'):

            vals['image_1920'] = kwargs.get('image')

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

        product_id=None,

        **kwargs
    ):

        partner = request.env.user.partner_id


        try:

            product_id = int(product_id)

        except Exception:

            return {
                'error': 'Invalid product ID'
            }


        product = request.env[
            'product.template'
        ].sudo().search([

            ('id', '=', product_id),

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


    @http.route(

        '/vendor/product/image/<int:product_id>',

        type='http',

        auth='user',

        website=True
    )
    def vendor_product_image(

        self,

        product_id,

        **kwargs
    ):


        partner = request.env.user.partner_id


        product = request.env[
            'product.template'
        ].sudo().search([

            ('id', '=', product_id),

            ('vendor_id', '=', partner.id)

        ], limit=1)
        

        if not product.exists():

            return request.not_found()


        image = (

            product.image_128

            or

            product.product_variant_id.image_128
        )


        if not image:

            return request.redirect(
                '/web/static/img/placeholder.png'
            )


        import base64


        try:

            image_data = base64.b64decode(image)

        except Exception:

            image_data = image


        return request.make_response(

            image_data,

            headers=[

                ('Content-Type', 'image/png'),

                ('Cache-Control', 'public, max-age=3600'),
            ]
        )
