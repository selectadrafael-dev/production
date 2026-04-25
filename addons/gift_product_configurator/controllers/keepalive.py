from odoo import http
from odoo.http import request

import logging

_logger = logging.getLogger(__name__)


class KeepAliveController(http.Controller):

    @http.route(
        ['/keepalive'],
        type='http',
        auth='public',
        website=False,
        csrf=False
    )
    def keepalive(self, **kwargs):

        _logger.warning(
            "KEEPALIVE PING RECEIVED"
        )

        return "OK"