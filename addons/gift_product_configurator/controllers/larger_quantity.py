from odoo import http
from odoo.http import request
from odoo.fields import Date
import json


class LargeQuantityController(http.Controller):

    @http.route('/larger-quantity/submit', type='http', auth='public', website=True, csrf=False)
    def submit_large_quantity(self, **kw):

        try:

            # ----------------------------------
            # READ JSON DATA FROM REQUEST
            # ----------------------------------

            raw_data = request.httprequest.data.decode("utf-8")
            data = json.loads(raw_data) if raw_data else {}

            email = data.get("email")

            # ----------------------------------
            # VALIDATE REQUIRED FIELDS
            # ----------------------------------

            if not email:
                return request.make_response(
                    json.dumps({"status": "error", "message": "Email is required"}),
                    headers=[('Content-Type', 'application/json')]
                )

            # ----------------------------------
            # CHECK OR CREATE CONTACT
            # ----------------------------------

            partner = request.env["res.partner"].sudo().search(
                [("email", "=", email)], limit=1
            )

            if not partner:
                partner = request.env["res.partner"].sudo().create({
                    "name": "%s %s" % (
                        data.get("first_name", ""),
                        data.get("last_name", "")
                    ),
                    "email": email,
                    "phone": data.get("phone"),
                })

            # ----------------------------------
            # HANDLE DATE SAFELY
            # ----------------------------------

            order_required_by = data.get("order_required_by")

            if order_required_by:
                try:
                    order_required_by = Date.to_date(order_required_by)
                except Exception:
                    order_required_by = False

            # ----------------------------------
            # SAFE TYPE CONVERSION
            # ----------------------------------

            product_id = data.get("product_id")
            quantity = data.get("quantity")
            product_price = data.get("product_price")

            product_id = int(product_id) if product_id else False
            quantity = int(quantity) if quantity else 0
            product_price = float(product_price) if product_price else 0.0

            # ----------------------------------
            # CREATE GIFTING ORDER
            # ----------------------------------

            request.env["custom.gifting.order"].sudo().create({

                "partner_id": partner.id,

                "company_name": data.get("company_name"),

                "first_name": data.get("first_name"),
                "last_name": data.get("last_name"),
                "email": email,

                "phone": data.get("phone"),
                "postcode": data.get("postcode"),

                "product_id": product_id,
                "product_name": data.get("product_name"),
                "product_image": data.get("product_image"),
                "product_price": product_price,

                "quantity": quantity,

                "additional_information": data.get("additional_information"),

                "order_required_by": order_required_by,

                "purpose": "large_qty_quote",
                "state": "submitted",
            })

            # ----------------------------------
            # SUCCESS RESPONSE
            # ----------------------------------

            return request.make_response(
                json.dumps({
                    "status": "success",
                    "message": "Quote request submitted successfully"
                }),
                headers=[('Content-Type', 'application/json')]
            )

        except Exception as e:

            # ----------------------------------
            # ERROR RESPONSE
            # ----------------------------------

            return request.make_response(
                json.dumps({
                    "status": "error",
                    "message": str(e)
                }),
                headers=[('Content-Type', 'application/json')]
            )