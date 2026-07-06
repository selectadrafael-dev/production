from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    website_quote_vat = fields.Float(

        string="Website Quote VAT %",

        config_parameter=
        "gift_product_configurator.website_quote_vat",

        default=20.0,

    )