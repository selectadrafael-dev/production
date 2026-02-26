from odoo import http
from odoo.http import request


class ConfiguratorAPI(http.Controller):

    def _get_quote(self):
        """
        Get or create session quote
        """

        quote_id = request.session.get('quote_id')

        if quote_id:
            quote = request.env['quote.order'].sudo().browse(quote_id)
            if quote.exists():
                return quote

        quote = request.env['quote.order'].sudo().create({})
        request.session['quote_id'] = quote.id

        return quote


    @http.route(
        '/quote/add_configured',
        type='json',
        auth='public',
        website=True
    )
    def add_configured(self, product_id, qty, options=None):

        options = options or {}

        quote = self._get_quote()

        product = request.env['product.product'].sudo().browse(product_id)

        # 🔥 Pricing engine
        pricing = request.env['pricing.service']
        price = pricing.calculate_price(product, qty, options)

        # 🔥 Create quote line
        line = request.env['quote.order.line'].sudo().create({
            'order_id': quote.id,
            'product_id': product.id,
            'quantity': qty,
            'price_unit': price,
            'name': product.name,
        })

        # 🔥 Save configuration
        request.env['quote.config'].sudo().create({
            'order_line_id': line.id,
            'print_method': options.get('print_method'),
            'production_time': options.get('production_time'),
            'wants_visual': options.get('visual'),
        })

        return {"success": True}