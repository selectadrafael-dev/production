from odoo import http
from odoo.http import request
import base64


class LargeQuantityController(http.Controller):

    @http.route('/larger-quantity/submit', type='json', auth='public', website=True, csrf=False)
    def submit_large_quantity(self, **post):

        email = post.get("email")

        # --------------------------------
        # CHECK OR CREATE CONTACT
        # --------------------------------

        partner = request.env["res.partner"].sudo().search(
            [("email", "=", email)], limit=1
        )

        if not partner:
            partner = request.env["res.partner"].sudo().create({
                "name": "%s %s" % (post.get("first_name"), post.get("last_name")),
                "email": email,
                "phone": post.get("phone"),
                "company_name": post.get("company_name"),
            })

        # --------------------------------
        # HANDLE LOGO UPLOAD
        # --------------------------------

        logo_binary = False
        logo_filename = False

        logo = request.httprequest.files.get("logo")

        if logo:
            logo_binary = base64.b64encode(logo.read())
            logo_filename = logo.filename

        # --------------------------------
        # CREATE GIFTING ORDER RECORD
        # --------------------------------

        request.env["custom.gifting.order"].sudo().create({

            "partner_id": partner.id,

            "company_name": post.get("company_name"),
            "first_name": post.get("first_name"),
            "last_name": post.get("last_name"),
            "email": email,
            "phone": post.get("phone"),
            "telephone_extension": post.get("telephone_extension"),
            "postcode": post.get("postcode"),

            "product_id": post.get("product_id"),
            "product_name": post.get("product_name"),
            "product_image": post.get("product_image"),
            "product_price": post.get("product_price"),

            "quantity": post.get("quantity"),

            "print_colour": post.get("print_colour"),
            "product_colour": post.get("product_colour"),

            "additional_information": post.get("additional_information"),
            "order_required_by": post.get("order_required_by"),

            "logo_file": logo_binary,
            "logo_filename": logo_filename,

            "purpose": "large_qty_quote",
            "state": "submitted",

        })

        return {
            "status": "success",
            "message": "Quote request submitted successfully"
        }