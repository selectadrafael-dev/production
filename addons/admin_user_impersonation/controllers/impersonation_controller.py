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
    def impersonate_start(
        self,
        user_id,
        **kwargs
    ):

        current_user = request.env.user

        # Only System Admins
        if not current_user.has_group(
            'base.group_system'
        ):
            return request.not_found()

        # Prevent nested impersonation
        if request.session.get(
            'impersonation_data'
        ):
            return redirect('/web')

        target_user = (
            request.env['res.users']
            .sudo()
            .browse(user_id)
        )

        if not target_user.exists():
            return request.not_found()

        # Prevent self-switch
        if target_user.id == current_user.id:
            return redirect('/web')

        # Prevent admin -> admin switch
        if target_user.has_group(
            'base.group_system'
        ):
            return request.not_found()

        # Store original admin
        request.session[
            'impersonation_data'
        ] = {
            'admin_id': current_user.id,
            'admin_name': current_user.name,
            'target_user_id': target_user.id,
            'target_user_name': target_user.name,
        }

        # Become vendor/user
        request.session.uid = target_user.id
        request.session.modified = True

        return redirect('/web')

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

        # Real vendor typed URL manually
        if not impersonation_data:
            return redirect('/web')

        admin_id = impersonation_data.get(
            'admin_id'
        )

        if not admin_id:
            request.session.pop(
                'impersonation_data',
                None
            )
            return redirect('/web')

        request.session.uid = admin_id

        request.session.pop(
            'impersonation_data',
            None
        )

        request.session.modified = True

        return redirect('/web')