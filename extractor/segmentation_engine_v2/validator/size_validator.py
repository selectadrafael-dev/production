"""
segmentation_engine_v2/validator/size_validator.py

Deliverable #11
Reject regions that are too small to represent a valid product.
"""

import logging

_logger = logging.getLogger(__name__)


class SizeValidator:

    def __init__(self):
        self.min_width = 20
        self.min_height = 20
        self.min_area = 800

    def validate(self, region):

        w = region.get("width", 0)
        h = region.get("height", 0)
        area = w * h

        if w < self.min_width:
            _logger.warning("[SIZE] reject width=%d", w)
            return False

        if h < self.min_height:
            _logger.warning("[SIZE] reject height=%d", h)
            return False

        if area < self.min_area:
            _logger.warning("[SIZE] reject area=%d", area)
            return False

        region["validated_size"] = True
        return True


size_validator = SizeValidator()
