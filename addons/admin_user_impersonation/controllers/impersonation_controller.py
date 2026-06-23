from odoo import http
from odoo.http import request
from werkzeug.utils import redirect


class ImpersonationController(http.Controller):

    @http.route(
        '/impersonate/start/<int:user_id>',
        type='http',
        auth='user',
        website=True
    )
    def impersonate_start(self, user_id, **kwargs):

        current_user = request.env.user

        # Allow only administrators
        if not current_user.has_group('base.group_system'):
            return request.not_found()

        target_user = request.env['res.users'].sudo().browse(user_id)

        if not target_user.exists():
            return request.not_found()

        # Prevent impersonating super admin
        if target_user.has_group('base.group_system'):
            return request.not_found()

        # Save original admin
        request.session['impersonator_id'] = current_user.id

        # Activate impersonation
        request.session.uid = target_user.id

        # Redirect
        return redirect('/my')

    # @http.route(
    #     '/impersonate/stop',
    #     type='http',
    #     auth='user',
    #     website=True
    # )
    # def impersonate_stop(self, **kwargs):

    #     impersonator_id = request.session.get('impersonator_id')

    #     if impersonator_id:

    #         request.session.uid = impersonator_id

    #         request.session.pop('impersonator_id')

    #     return redirect('/web')

    @http.route(
        '/impersonate/stop',
        type='http',
        auth='user',
        website=True
    )
    def impersonate_stop(
        self,
        **kwargs
    ):

        impersonation_data = (
            request.session.get(
                'impersonation_data'
            )
        )

        if impersonation_data:

            request.session.uid = (
                impersonation_data[
                    'admin_id'
                ]
            )

            request.session.pop(
                'impersonation_data',
                None
            )

        return redirect('/web')