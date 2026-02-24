from odoo import models, fields, api


# =========================================================
# QUOTE ORDER
# =========================================================

class QuoteOrder(models.Model):
    _name = 'quote.order'
    _description = 'Website Quote'
    _order = 'id desc'

    # --- Identity ---
    name = fields.Char(
        string="Quote Reference",
        default="New",
        copy=False
    )

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('converted', 'Converted'),
            ('cancel', 'Cancelled'),
        ],
        default='draft'
    )

    # --- Customer ---
    partner_id = fields.Many2one(
        'res.partner',
        string="Customer"
    )

    email = fields.Char()
    phone = fields.Char()

    # --- Lines ---
    line_ids = fields.One2many(
        'quote.order.line',
        'order_id',
        string="Quote Lines",
        copy=True
    )

    # --- Totals ---
    amount_total = fields.Float(
        compute='_compute_total',
        store=True
    )

    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )

    # --- Artwork / Visual ---
    wants_visual = fields.Boolean(
        string="Free Visual Requested",
        default=False
    )

    artwork = fields.Binary(string="Artwork File")
    artwork_filename = fields.Char()

    # --- Submission Info ---
    submitted_date = fields.Datetime()
    notes = fields.Text()

    # =====================================================
    # COMPUTE TOTAL
    # =====================================================

    @api.depends('line_ids.price_subtotal')
    def _compute_total(self):
        for order in self:
            order.amount_total = sum(
                line.price_subtotal for line in order.line_ids
            )

    # =====================================================
    # SEQUENCE ON CREATE
    # =====================================================

    @api.model
    def create(self, vals):

        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'quote.order'
            ) or 'Q-NEW'

        return super().create(vals)

    # =====================================================
    # ACTIONS
    # =====================================================

    def action_submit(self):
        self.write({
            'state': 'submitted',
            'submitted_date': fields.Datetime.now()
        })

    def action_cancel(self):
        self.write({'state': 'cancel'})


# =========================================================
# QUOTE ORDER LINE
# =========================================================

class QuoteOrderLine(models.Model):
    _name = 'quote.order.line'
    _description = 'Quote Line'
    _order = 'id'

    order_id = fields.Many2one(
        'quote.order',
        required=True,
        ondelete='cascade'
    )

    product_id = fields.Many2one(
        'product.product',
        required=True
    )

    name = fields.Char()

    quantity = fields.Integer(
        default=1,
        required=True
    )

    price_unit = fields.Float(default=0.0)

    price_subtotal = fields.Float(
        compute='_compute_subtotal',
        store=True
    )

    image = fields.Binary(
        related='product_id.image_128',
        readonly=True
    )

    # 🔥 Link configurations
    config_ids = fields.One2many(
        'quote.config',
        'order_line_id',
        string="Configurations"
    )

    # =====================================================
    # SUBTOTAL
    # =====================================================

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.price_subtotal = (
                line.quantity * line.price_unit
            )


# =========================================================
# PRODUCT CONFIGURATION
# =========================================================

class QuoteConfig(models.Model):
    _name = "quote.config"
    _description = "Product Configuration"

    order_line_id = fields.Many2one(
        'quote.order.line',
        required=True,
        ondelete='cascade'
    )

    print_method = fields.Char()
    colours = fields.Char()
    production_time = fields.Char()
    size = fields.Char()

    artwork_file = fields.Binary()
    artwork_filename = fields.Char()

    wants_visual = fields.Boolean(default=False)


# =========================================================
# PRICING SERVICE
# =========================================================

class PricingService(models.AbstractModel):
    _name = 'pricing.service'
    _description = 'Pricing Engine'

    def calculate_price(self, product, qty, options=None):

        options = options or {}

        base = product.list_price or 0.0

        # Print method
        if options.get("print_method") == "digital":
            base += 0.30

        # Express production
        if options.get("production_time") == "express":
            base *= 1.2

        # Bulk discount
        if qty >= 500:
            base *= 0.8

        return base