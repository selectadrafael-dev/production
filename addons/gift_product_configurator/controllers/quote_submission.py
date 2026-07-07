# -*- coding: utf-8 -*-

import json

from odoo import http
from odoo.http import request


class WebsiteQuoteSubmission(http.Controller):

    @http.route(
        "/quote/submit",
        type="http",
        auth="public",
        website=True,
        csrf=True,
        methods=["POST"],
    )
    def submit_quote(self, **post):

        try:

            # --------------------------------------------
            # Customer Information
            # --------------------------------------------

            first_name = post.get("first_name", "").strip()
            last_name = post.get("last_name", "").strip()

            customer_name = (
                f"{first_name} {last_name}"
            ).strip()

            # --------------------------------------------
            # Quote Cart
            # --------------------------------------------

            cart_json = post.get("quote_cart", "[]")

            cart = json.loads(cart_json)

            # --------------------------------------------
            # Header
            # --------------------------------------------

            quote = request.env[
                "gift.quote.request"
            ].sudo().create({

                "customer_name":
                    customer_name,

                "first_name":
                    first_name,

                "last_name":
                    last_name,

                "company_name":
                    post.get("company_name"),

                "email":
                    post.get("email"),

                "phone":
                    post.get("telephone_extension"),

                "postcode":
                    post.get("postcode"),

                "required_date":
                    post.get("order_required_by"),

                "additional_information":
                    post.get("additional_information"),

                "need_visual":
                    bool(post.get("need_visual")),

            })

            # --------------------------------------------
            # Lines
            # --------------------------------------------

            for item in cart:

                request.env[
                    "gift.quote.request.line"
                ].sudo().create({

                    "request_id":
                        quote.id,

                    "product_id":
                        item.get("id"),

                    "product_name":
                        item.get("name"),

                    "quantity":
                        item.get("quantity", 1),

                    "unit_price":
                        item.get("price", 0),

                    "discount":
                        item.get("discount", 0),

                    "tier_quantity":
                        item.get("tier_quantity"),

                    "product_image":
                        item.get("image"),

                    "configuration_json":
                        item.get("configuration", {}),

                })

            # --------------------------------------------
            # Logo Upload
            # --------------------------------------------

            logo = post.get("logo")

            if logo:

                quote.write({

                    "logo_filename":
                        logo.filename,

                    "logo":
                        logo.read(),

                })

            # --------------------------------------------
            # Workflow
            # --------------------------------------------

            quote.process_submission()

            return request.make_json_response({

                "success": True,

                "reference": quote.name,

            })

        except Exception as e:

            return request.make_json_response({

                "success": False,

                "error": str(e),

            })