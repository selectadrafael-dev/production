from odoo import (
    fields,
    models
)

import logging

_logger = logging.getLogger(__name__)

_logger.warning(
    "PRODUCT MASS UPDATE WIZARD FILE LOADED"
)


class ProductMassUpdateWizard(
    models.TransientModel
):

    _name = "product.mass.update.wizard"

    test_field = fields.Char()