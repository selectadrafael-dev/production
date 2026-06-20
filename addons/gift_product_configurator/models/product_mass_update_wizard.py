from odoo import (
    api,
    fields,
    models
)

import logging

_logger = logging.getLogger(__name__)

_logger.warning(
    "PRODUCT MASS UPDATE WIZARD FILE LOADED"
)

from odoo.exceptions import UserError