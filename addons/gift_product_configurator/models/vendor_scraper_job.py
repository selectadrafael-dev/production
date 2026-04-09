from odoo import models, fields, api
import json
import logging

_logger = logging.getLogger(__name__)

# ✅ Extend existing model
class ResPartner(models.Model):
    _inherit = 'res.partner'

    #Vendor user role
    is_vendor_user = fields.Boolean(
        string="Vendor User",
        default=False
    )


class VendorScraperJob(models.Model):
    _name = 'vendor.scraper.job'
    _description = 'Vendor Scraper Job'

    partner_id = fields.Many2one("res.partner", string="Vendor")  # ✅ LINK instead


    name = fields.Char()
    url = fields.Char(required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('processing', 'Processing'),
        ('done', 'Done'),
        ('failed', 'Failed'),
    ], default='draft')

    extracted_data = fields.Text()

    # ================= MAIN ENTRY =================
    def action_process(self):

        self.state = "processing"

        try:
            from ..services.scraper_service import scrape_url

            _logger.warning(f"SCRAPING URL → {self.url}")

            products = scrape_url(self.url)

            if not products:
                raise Exception("No products found")

            pages = [{
                "page": 1,
                "text": "\n".join([p["name"] for p in products]),
                "images": [
                    p["image_base64"]
                    for p in products if p.get("image_base64")
                ]
            }]

            self.extracted_data = json.dumps(pages)

            # 🔥 REUSE YOUR EXISTING ENGINE
            job = self.env['vendor.import.job'].create({
                'extracted_text': self.extracted_data
            })

            job.send_to_openai()
            job.create_product_drafts()

            self.state = "done"

        except Exception as e:
            _logger.error(f"SCRAPER FAILED → {str(e)}")
            self.state = "failed"