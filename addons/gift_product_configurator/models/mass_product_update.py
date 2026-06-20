# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

class ProductMassUpdateWizard(models.TransientModel):
    _name = 'product.bulk.update.wizard'
    _description = 'Product Mass Update Wizard'

    # Publish field
    is_published = fields.Boolean(string='Publish Products', default=True)
    update_publish = fields.Boolean(string='Update Publish Status', default=False)

    # Price fields
    price_change_type = fields.Selection([
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage (%)')
    ], string='Price Change Type', default='fixed')
    
    price_value = fields.Float(string='Price Value Change', help="Positive values increase, negative values decrease price.")
    update_price = fields.Boolean(string='Update Price', default=False)

    def action_apply_mass_update(self):
        """Processes the mass updates and returns success notifications."""
        # Get active products from the list view context
        active_ids = self.env.context.get('active_ids', [])
        products = self.env['product.template'].browse(active_ids)

        if not products:
            raise UserError("No products were selected for mass update.")

        success_count = 0
        try:
            for product in products:
                vals = {}
                
                # Handle publication update
                if self.update_publish:
                    # 'website_published' is the standard Odoo field name
                    vals['website_published'] = self.is_published

                # Handle price calculation matrix
                if self.update_price and self.price_value != 0:
                    if self.price_change_type == 'fixed':
                        vals['list_price'] = product.list_price + self.price_value
                    elif self.price_change_type == 'percentage':
                        vals['list_price'] = product.list_price * (1 + (self.price_value / 100.0))

                if vals:
                    product.write(vals)
                    success_count += 1

            # Trigger successful web client notification banner
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': f'Successfully updated {success_count} products.',
                    'sticky': False,
                    'type': 'success', 
                    'next': {'type': 'ir.actions.act_window_close'}, # Closes modal layout
                }
            }

        except Exception as e:
            # Trigger clean fail message UI modal
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error Occurred',
                    'message': f'Mass update execution failed: {str(e)}',
                    'sticky': True,
                    'type': 'danger',
                }
            }
