from odoo import http
from odoo.http import request


class QuoteController(http.Controller):

    def _get_quote(self):

        quote_id = request.session.get('quote_id')

        if quote_id:
            quote = request.env['quote.order'].sudo().browse(quote_id)
            if quote.exists():
                return quote

        quote = request.env['quote.order'].sudo().create({})
        request.session['quote_id'] = quote.id

        return quote


    @http.route('/quote/add', type='json', auth='public', website=True)
    def add_to_quote(self, product_id, qty=1):

        quote = self._get_quote()

        product = request.env['product.product'].sudo().browse(product_id)

        if not product.exists():
            return {'success': False}

        request.env['quote.order.line'].sudo().create({
            'order_id': quote.id,
            'product_id': product.id,
            'quantity': qty,
            'price_unit': product.lst_price,
            'name': product.name,
        })

        return {'success': True}


    @http.route('/quote/remove', type='json', auth='public', website=True)
    def remove_line(self, line_id):

        line = request.env['quote.order.line'].sudo().browse(line_id)

        if line.exists():
            line.unlink()

        return {'success': True}


    @http.route('/quote/toggle_visual', type='json', auth='public', website=True)
    def toggle_visual(self, value):

        quote = self._get_quote()

        quote.sudo().write({'wants_visual': bool(value)})

        return {'success': True}


    @http.route(
        '/quote/upload_artwork',
        type='http',
        auth='public',
        methods=['POST'],
        website=True
    )
    def upload_artwork(self, artwork=None):

        if not artwork:
            return request.redirect('/')

        quote = self._get_quote()

        quote.sudo().write({
            'artwork': artwork.read(),
            'artwork_filename': artwork.filename,
        })

        return request.redirect('/')
    
    @http.route('/quote/count', type='json', auth='public', website=True)
    def quote_count(self):
        quote = self._get_quote()
        return {'count': len(quote.line_ids)}