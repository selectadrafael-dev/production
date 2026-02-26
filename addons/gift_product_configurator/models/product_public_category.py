from odoo import models, fields


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    hero_title = fields.Char("Hero Title")
    hero_subtitle = fields.Char("Hero Subtitle")
    hero_description = fields.Text("Hero Description")
    hero_bg_color = fields.Char(
        "Hero Background Color",
        default="#6E8FC6"
    )