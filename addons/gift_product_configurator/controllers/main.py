from odoo import http
from odoo.http import request

class LargerQuantityController(http.Controller):

    @http.route('/larger-quantity', type='http', auth='public', website=True)
    def larger_quantity(self, **kwargs):
        return request.render(
            'gift_product_configurator.larger_quantity_page',
            {}
        )