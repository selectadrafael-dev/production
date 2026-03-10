from odoo import http
from odoo.http import request
import json
import base64


class LargeQuantityController(http.Controller):

    @http.route('/larger-quantity/submit', type='http', auth='public', website=True, csrf=False)
    def submit_large_quantity(self, **post):

        data = json.loads(request.httprequest.data.decode("utf-8"))

        email = data.get("email")

        partner = request.env["res.partner"].sudo().search(
            [("email", "=", email)], limit=1
        )

        if not partner:
            partner = request.env["res.partner"].sudo().create({
                "name": "%s %s" % (data.get("first_name"), data.get("last_name")),
                "email": email,
                "phone": data.get("phone"),
                "company_name": data.get("company_name"),
            })

        request.env["custom.gifting.order"].sudo().create({

            "partner_id": partner.id,

            "company_name": data.get("company_name"),
            "first_name": data.get("first_name"),
            "last_name": data.get("last_name"),
            "email": email,

            "phone": data.get("phone"),
            "postcode": data.get("postcode"),

            "product_id": data.get("product_id"),
            "product_name": data.get("product_name"),
            "product_image": data.get("product_image"),
            "product_price": data.get("product_price"),

            "quantity": data.get("quantity"),

            "additional_information": data.get("additional_information"),
            "order_required_by": data.get("order_required_by"),

            "purpose": "large_qty_quote",
            "state": "submitted",

        })

        return request.make_response(
            json.dumps({"status": "success"}),
            headers=[('Content-Type', 'application/json')]
        )