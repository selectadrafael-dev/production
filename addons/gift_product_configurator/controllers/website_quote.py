# ==========================================================
# IMPORTS
# ==========================================================

from odoo import http
from odoo.http import request

import base64
import json
import logging


_logger = logging.getLogger(__name__)


# ==========================================================
# WEBSITE QUOTE CONTROLLER
# ==========================================================

class WebsiteQuoteController(http.Controller):
    """
    Website quotation controller.

    Responsibilities
    ----------------
    1. Receive website quotation requests.
    2. Validate incoming payload.
    3. Create / find customer.
    4. Create Gift Quote Request.
    5. Create Quote Lines.
    6. Attach artwork/logo.
    7. Trigger CRM workflow.
    8. Return JSON response.

    IMPORTANT

    The controller should NEVER perform business calculations.

    Pricing, discounts, quantities, branding selections,
    etc. arrive from the website as a transaction snapshot.

    The controller simply validates and persists that data.
    """

    # ==========================================================
    # JSON RESPONSE
    # ==========================================================

    def _json_response(
        self,
        success,
        message,
        **kwargs,
    ):
        """
        Standard JSON response for Odoo JSON routes.
        """

        response = {

            "success": bool(success),

            "message": message,

        }

        response.update(kwargs)

        return response

    # ==========================================================
    # FIND / CREATE CUSTOMER
    # ==========================================================

    def _find_or_create_partner(
        self,
        payload,
    ):
        """
        Find an existing customer by email.

        If none exists, create a new customer.

        Returns
        -------
        res.partner record
        """

        Partner = request.env[
            "res.partner"
        ].sudo()

        email = (
            payload.get("email")
            or ""
        ).strip().lower()

        partner = Partner.search(

            [
                ("email", "=", email)
            ],

            limit=1,

        )

        if partner:

            #
            # Keep customer details updated
            #

            values = {}

            full_name = " ".join(

                filter(

                    None,

                    [

                        payload.get("first_name"),

                        payload.get("last_name"),

                    ],

                )

            ).strip()

            if full_name and partner.name != full_name:
                values["name"] = full_name

            if payload.get("phone") and partner.phone != payload.get("phone"):
                values["phone"] = payload.get("phone")

            if payload.get("postcode") and partner.zip != payload.get("postcode"):
                values["zip"] = payload.get("postcode")

            if payload.get("company_name"):

                company = payload.get("company_name").strip()

                if company:

                    values["company_name"] = company

            if values:
                partner.write(values)

            return partner

        #
        # Create new customer
        #

        full_name = " ".join(

            filter(

                None,

                [

                    payload.get("first_name"),

                    payload.get("last_name"),

                ],

            )

        ).strip()

        partner = Partner.create({

            "name":
                full_name or email,

            "company_type":
                "person",

            "email":
                email,

            "phone":
                payload.get("phone"),

            "zip":
                payload.get("postcode"),

            "company_name":
                payload.get("company_name"),

        })

        _logger.info(

            "Created new website customer: %s",

            partner.display_name,

        )

        return partner
    
    # ==========================================================
    # PREPARE QUOTE VALUES
    # ==========================================================

    def _prepare_quote_values(
        self,
        payload,
        partner,
    ):
        """
        Prepare values for gift.quote.request.create().

        This method is the ONLY place responsible for
        mapping the incoming website payload to the
        Gift Quote Request model.
        """

        def as_bool(value):
            return str(value).lower() in (
                "true",
                "1",
                "yes",
                "on",
            )

        return {

            # ----------------------------------------------
            # Customer
            # ----------------------------------------------

            "partner_id":
                partner.id,

            "company_name":
                payload.get("company_name"),

            "first_name":
                payload.get("first_name"),

            "last_name":
                payload.get("last_name"),

            "email":
                payload.get("email"),

            "phone":
                payload.get("phone"),

            "postcode":
                payload.get("postcode"),

            # ----------------------------------------------
            # Quote
            # ----------------------------------------------

            "required_date":
                payload.get("required_date") or False,

            "additional_information":
                payload.get(
                    "additional_information"
                ),

            "need_visual":
                as_bool(
                    payload.get(
                        "need_visual"
                    )
                ),

            "include_vat":
                as_bool(
                    payload.get(
                        "include_vat"
                    )
                ),

            "state":
                "submitted",

        }

    # ==========================================================
    # PREPARE QUOTE LINE VALUES
    # ==========================================================

    def _prepare_line_values(
        self,
        product,
        quote,
    ):
        """
        Convert one website product snapshot into
        one gift.quote.request.line record.

        This is the ONLY place that understands
        the website product JSON schema.
        """

        Product = request.env[
            "product.product"
        ].sudo()

        product_id = product.get("product_id")

        product_record = False

        # --------------------------------------------------
        # Pricing Snapshot
        # --------------------------------------------------

        pricing = (

            product.get(

                "pricing_snapshot"

            )

            or {}

        )

        if product_id:

            product_record = Product.browse(
                int(product_id)
            )

            if not product_record.exists():
                product_record = False

        return {

            # ----------------------------------------------
            # Parent
            # ----------------------------------------------

            "request_id":
                quote.id,

            # ----------------------------------------------
            # Product
            # ----------------------------------------------

            "product_id":
                product_record.id if product_record else False,

            "product_name":
                product.get("product_name"),

            "sku":
                product.get("sku"),

            "product_url":
                product.get("product_url"),

            "variant_name":
                product.get("variant_name"),

            "colour":
                product.get("colour"),

            # ----------------------------------------------
            # Branding
            # ----------------------------------------------

            "print_method":
                product.get("print_method"),

            "logo_colours":
                product.get("logo_colours"),

            "artwork_required":
                bool(
                    product.get(
                        "artwork_required"
                    )
                ),

            # ----------------------------------------------
            # Pricing
            # ----------------------------------------------

            "tier_name":

                pricing.get(

                    "tier"

                )

                or

                product.get(

                    "tier_name"

                ),


            "tier_quantity":

                pricing.get(

                    "qty"

                )

                or

                product.get(

                    "tier_quantity"

                ),
            
            "pricing_tier_id":
                product.get(

                    "pricing_tier_id"

                ),

            "quantity":
                product.get("quantity") or 1,

           "currency":

                pricing.get(

                    "currency"

                )

                or

                product.get(

                    "currency"

                ),

           "unit_price":

                    pricing.get(

                        "price"

                    )

                    or

                    product.get(

                        "unit_price"

                    )

                    or

                    0,

            "original_price":
                product.get("original_price") or 0,

           "discount":

                pricing.get(

                    "discount"

                )

                or

                product.get(

                    "discount"

                )

                or

                0,
            
          "pricing_snapshot": pricing,

            "discount_amount":
                product.get("discount_amount") or 0,

            "subtotal":
                product.get("subtotal") or 0,

            "include_vat":
                bool(
                    product.get(
                        "include_vat"
                    )
                ),

            # ----------------------------------------------
            # Audit
            # ----------------------------------------------

            "source":
                product.get("source"),

            "fingerprint":
                product.get("fingerprint"),

        }
    
    # ==========================================================
    # ATTACH LOGO / ARTWORK
    # ==========================================================

    def _attach_logo(
        self,
        quote,
        logo_file,
    ):
        """
        Attach uploaded artwork/logo to the quote.

        Returns
        -------
        ir.attachment record or False
        """

        if not logo_file:
            return False

        attachment = request.env[
            "ir.attachment"
        ].sudo().create({

            "name":
                logo_file.filename,

            "datas":
                base64.b64encode(
                    logo_file.read()
                ),

            "res_model":
                "gift.quote.request",

            "res_id":
                quote.id,

            "mimetype":
                getattr(
                    logo_file,
                    "content_type",
                    False,
                ),

        })

        _logger.info(

            "Artwork attached to quote %s",

            quote.name,

        )

        return attachment
    

    # ==========================================================
    # SUBMIT WEBSITE QUOTE
    # ==========================================================

    @http.route(
        "/website/quote/submit",
        type="json",
        auth="public",
        methods=["POST"],
        csrf=True,
        website=True,
    )
    def submit_quote(self, **kwargs):

        try:

            payload = request.get_json_data() or {}

            #
            # Basic validation
            #

            required = [

                "first_name",
                "last_name",
                "email",

            ]

            for field in required:

                if not payload.get(field):

                    return self._json_response(

                        False,

                        "%s is required." % (
                            field.replace("_", " ").title()
                        )

                    )

            products = payload.get("products") or []

            if not products:

                return self._json_response(

                    False,

                    "Your quote contains no products.",

                )

            #
            # Customer
            #

            partner = self._find_or_create_partner(
                payload
            )

            #
            # Quote
            #

            quote = request.env[
                "gift.quote.request"
            ].sudo().create(

                self._prepare_quote_values(

                    payload,

                    partner,

                )

            )

            #
            # Quote Lines
            #

            QuoteLine = request.env[
                "gift.quote.request.line"
            ].sudo()

            for product in products:

                QuoteLine.create(

                    self._prepare_line_values(

                        product,

                        quote,

                    )

                )

            #
            # Artwork
            #

            if kwargs.get("logo"):

                self._attach_logo(

                    quote,

                    kwargs["logo"],

                )

            #
            # CRM
            #

            quote._create_crm_lead()

            _logger.info(

                "Website quote %s successfully created.",

                quote.name,

            )

            return self._json_response(

                True,

                "Quote submitted successfully.",

                quote_id=quote.id,

                reference=quote.name,

                crm_id=quote.lead_id.id if quote.lead_id else False,

            )

        # except Exception:

        #     _logger.exception(

        #         "Website quote submission failed."

        #     )

        #     return self._json_response(

        #         False,

        #         "Unexpected server error."

        #     )

        except Exception as e:

            _logger.exception(
                "Website quote submission failed."
            )

            return self._json_response(

                False,

                str(e),

            )