from odoo import models, fields

class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    # =========================
    # HERO CONTENT
    # =========================
    hero_title = fields.Char("Hero Title", translate=True)
    hero_subtitle = fields.Char("Hero Subtitle", translate=True)
    hero_description = fields.Text("Hero Description", translate=True)
    show_favourites = fields.Boolean("Show Favourites Section")
    show_home_promo = fields.Boolean(
    "Show On Home Promotional Section")
    show_popular_carousel = fields.Boolean(
        "Show In Popular Categories Carousel"
    )

    # =========================
    # HERO DESIGN
    # =========================
    hero_bg_color = fields.Char(
        "Hero Background Color",
        default="#6E8FC6"
    )

    hero_layout = fields.Selection([
        ('split', 'Split (Sidebar Overlap)'),
        ('center', 'Center (Keyrings Style)'),
        ('compact', 'Compact'),
        ('editorial', 'Editorial (Drinkware Style)'),
        ('sidebar_hero', 'Sidebar Hero (New Arrivals Style)'),
    ], default='split')

    # =========================
    # OPTIONAL (ADVANCED)
    # =========================
    hero_image = fields.Binary("Hero Image")
    hero_cta_text = fields.Char("CTA Text", translate=True)
    hero_cta_link = fields.Char("CTA Link")