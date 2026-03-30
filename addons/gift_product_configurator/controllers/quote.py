from odoo import models, fields

class QuoteOrder(models.Model):
    _name = 'quote.order'
    _description = 'Quote Order'

    name = fields.Char(default='New')
    partner_id = fields.Many2one('res.partner')
    line_ids = fields.One2many('quote.order.line', 'order_id')

    wants_visual = fields.Boolean(default=False)
    artwork = fields.Binary()
    artwork_filename = fields.Char()


class QuoteOrderLine(models.Model):
    _name = 'quote.order.line'
    _description = 'Quote Line'

    order_id = fields.Many2one('quote.order')
    product_id = fields.Many2one('product.product')

    quantity = fields.Integer(default=1)
    price_unit = fields.Float()

    name = fields.Char()
