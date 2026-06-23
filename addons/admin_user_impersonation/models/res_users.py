from odoo import models

class ResUsers(models.Model):
    _inherit = 'res.users'

    def action_impersonate_user(self):

        self.ensure_one()

        #=======admin impersontion
        return {
            'type': 'ir.actions.act_url',
            'url': f'/impersonate/start/{self.id}',
            'target': 'self',
        }

        