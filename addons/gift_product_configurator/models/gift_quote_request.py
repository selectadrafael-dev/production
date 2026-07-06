# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class GiftQuoteRequest(models.Model):
    _name = "gift.quote.request"
    _description = "Website Quote Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    # ==========================================================
    # BASIC INFORMATION
    # ==========================================================

    name = fields.Char(
        string="Reference",
        required=True,
        copy=False,
        readonly=True,
        default="New",
        tracking=True,
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("crm_created", "CRM Created"),
            ("quotation_created", "Quotation Created"),
            ("won", "Won"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        tracking=True,
    )

    # ==========================================================
    # CUSTOMER
    # ==========================================================

    partner_id = fields.Many2one(
        "res.partner",
        string="Customer",
        tracking=True,
    )

    company_name = fields.Char()

    first_name = fields.Char(required=True)

    last_name = fields.Char(required=True)

    email = fields.Char(required=True)

    phone = fields.Char()

    postcode = fields.Char()

    # ==========================================================
    # PRODUCT
    # ==========================================================

    product_id = fields.Many2one(
        "product.product",
        string="Product",
    )

    product_name = fields.Char()

    variant_name = fields.Char()

    colour = fields.Char()

    quantity = fields.Float()

    unit_price = fields.Float()

    subtotal = fields.Float()

    currency = fields.Char()

    # ==========================================================
    # BRANDING
    # ==========================================================

    print_method = fields.Char()

    logo_colours = fields.Char()

    include_vat = fields.Boolean()

    need_visual = fields.Boolean()

    required_date = fields.Date()

    additional_information = fields.Text()

    # ==========================================================
    # FILES
    # ==========================================================

    logo_attachment_id = fields.Many2one(
        "ir.attachment",
        string="Logo",
    )

    # ==========================================================
    # GENERATED RECORDS
    # ==========================================================

    lead_id = fields.Many2one(
        "crm.lead",
        string="CRM Lead",
        readonly=True,
    )

    sale_order_id = fields.Many2one(
        "sale.order",
        string="Quotation",
        readonly=True,
    )

    # ==========================================================
    # WEBSITE
    # ==========================================================

    website_id = fields.Many2one(
        "website",
        default=lambda self: self.env.website,
    )

    website_language = fields.Char()

    submitted_on = fields.Datetime(
        default=fields.Datetime.now,
    )

    # ==========================================================
    # DISPLAY
    # ==========================================================

    customer_name = fields.Char(
        compute="_compute_customer_name",
        store=True,
    )

    line_ids = fields.One2many(
        "gift.quote.request.line",
        "request_id",
        string="Quote Lines",
    )

    @api.depends("first_name", "last_name")
    def _compute_customer_name(self):

        for rec in self:

            rec.customer_name = (
                (rec.first_name or "")
                + " "
                + (rec.last_name or "")
            ).strip()

    # ==========================================================
    # CREATE
    # ==========================================================

    @api.model
    def create(self, vals):

        if vals.get("name", "New") == "New":

            vals["name"] = self.env["ir.sequence"].next_by_code(
                "gift.quote.request"
            ) or "New"

        return super().create(vals)
    
    # ==========================================================
    # PARTNER
    # ==========================================================

    def _get_or_create_partner(self):

        self.ensure_one()

        partner = self.env["res.partner"].search([
            ("email", "=", self.email)
        ], limit=1)

        if partner:
            return partner

        return self.env["res.partner"].create({

            "name": self.customer_name,

            "company_type": "person",

            "email": self.email,

            "phone": self.phone,

            "zip": self.postcode,

            "company_name": self.company_name,

        })
    
    # ==========================================================
    # VALIDATION
    # ==========================================================

    def _validate_submission(self):

        self.ensure_one()

        if not self.email:

            raise ValidationError(_("Email is required."))

        if not self.first_name:

            raise ValidationError(_("First name is required."))

        if not self.last_name:

            raise ValidationError(_("Last name is required."))

        if not self.line_ids:

            raise ValidationError(_("Quote contains no products."))
        
  
    # ==========================================================
    # MAIN WORKFLOW
    # ==========================================================

    def process_submission(self):

        self.ensure_one()

        self._validate_submission()

        try:

            partner = self._get_or_create_partner()

            self.partner_id = partner.id

            self.state = "submitted"

            self._create_crm_lead()

            self._create_sale_order()

            self._attach_logo()

            self._send_confirmation_email()

            self.state = "quotation_created"

            return True

        except Exception:

            raise
    

    # ==========================================================
    # CRM
    # ==========================================================

    def _create_crm_lead(self):

        self.ensure_one()

        product_summary = []

        for line in self.line_ids:

            product_summary.append(

                "%s × %s (%s)"

                % (

                    int(line.quantity),

                    line.product_name or line.product_id.display_name,

                    line.print_method or "Standard",

                )

            )

  
        description = "\n".join([
            "Website Quote Reference",
            self.name or "",
            "",
            "Products",
            "\n".join(product_summary),
            "",
            "Print Method",
            self.line_ids[:1].print_method if self.line_ids else "",
            "",
            "Logo Colours",
            self.line_ids[:1].logo_colours if self.line_ids else "",
            "",
            "Need Free Visual",
            "Yes" if self.need_visual else "No",
            "",
            "Required Date",
            str(self.required_date or ""),
            "",
            "Customer Notes",
            self.additional_information or "",
        ])

        # ==========================================================
        # Resolve Sales Team
        # ==========================================================

        team = self.env["crm.team"].search(
            [("name", "=", "Sales")],
            limit=1,
        )

        lead = self.env["crm.lead"].create({

            "name":

            "Website Quote | %s | %s"

            % (

                self.name,

                self.customer_name,

            ),

            "type": "opportunity",

            "partner_id": self.partner_id.id,

            "contact_name": self.customer_name,

            "email_from": self.email,

            "phone": self.phone,

            "description": description,

            "team_id": team.id if team else False,

        })

        self.lead_id = lead.id

        self.state = "crm_created"

        return lead


    def _create_sale_order(self):
        raise NotImplementedError()


    def _attach_logo(self):
        pass


    def _send_confirmation_email(self):
        pass


    # ==========================================================
    # GENERATE SALE ORDER
    # ==========================================================

    def action_generate_sale_order(self):

        self.ensure_one()

        if self.sale_order_id:
            return {
                "type": "ir.actions.act_window",
                "res_model": "sale.order",
                "view_mode": "form",
                "res_id": self.sale_order_id.id,
            }

        partner = self.partner_id

        if not partner:
            partner = self._get_or_create_partner()
            self.partner_id = partner.id

        sale_order = self.env["sale.order"].create({

            "partner_id": partner.id,

            "origin": self.name,

            "client_order_ref": self.name,

        })

        name = line.product_name or line.product_id.display_name

        config = []

        if line.print_method:
            config.append(f"Print Method: {line.print_method}")

        if line.logo_colours:
            config.append(f"Logo Colours: {line.logo_colours}")

        if line.tier_quantity:
            config.append(f"Quantity Tier: {line.tier_quantity}")

        if line.include_vat:
            config.append("VAT Included")

        if config:
            name += "\n\n" + "\n".join(config)


        for line in self.line_ids:

            self.env["sale.order.line"].create({

                "order_id": sale_order.id,

                "product_id": line.product_id.id,

                "name": name,

                "product_uom_qty": line.quantity,

                # Website snapshot price
                "price_unit": line.unit_price,

            })

        self.sale_order_id = sale_order.id

        self.state = "quotation_created"

        return {

            "type": "ir.actions.act_window",

            "res_model": "sale.order",

            "view_mode": "form",

            "res_id": sale_order.id,

        }