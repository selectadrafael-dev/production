from odoo import http
from odoo.http import request
from odoo.fields import Date
import json
import base64


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

            quantity = data.get("quantity")
            quantity = int(quantity) if quantity else 0

            # ----------------------------------
            # HANDLE LOGO FILE (IF PROVIDED)
            # ----------------------------------

            logo_file = request.httprequest.files.get("logo")

            logo_data = False
            logo_filename = False

            if logo_file:
                logo_data = base64.b64encode(logo_file.read())
                logo_filename = logo_file.filename

            # ----------------------------------
            # CREATE MAIN ORDER
            # ----------------------------------

            order = request.env["custom.gifting.order"].sudo().create({

                "partner_id": partner.id,

                "company_name": data.get("company_name"),

                "first_name": data.get("first_name"),
                "last_name": data.get("last_name"),
                "email": email,

                "phone": data.get("phone"),
                "postcode": data.get("postcode"),

                "quantity": quantity,

                "additional_information": data.get("additional_information"),

                "order_required_by": order_required_by,

                "purpose": "large_qty_quote",
                "state": "submitted",

                "logo": logo_data,
                "logo_filename": logo_filename,
            })

            # ----------------------------------
            # STORE PRODUCTS FROM SIDEBAR
            # ----------------------------------

            products = data.get("products", [])

            for p in products:

                product_name = p.get("name")
                product_image = p.get("image")
                product_price = float(p.get("price", 0))
                product_qty = int(p.get("qty", 1))

                request.env["custom.gifting.order.line"].sudo().create({

                    "order_id": order.id,

                    "product_name": product_name,

                    "product_image": product_image,

                    "product_price": product_price,

                    "quantity": product_qty,

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