"""
segmentation_engine_v2/validator/aspect_validator.py

Deliverable #12
Reject implausible product aspect ratios while allowing
reasonable portrait, landscape and square products.
"""

import logging

_logger = logging.getLogger(__name__)


class AspectValidator:

    def __init__(self):
        self.max_aspect_ratio = 6.0
        self.min_aspect_ratio = 0.16

    def validate(self, region):

        w = max(1, region.get("width", 0))
        h = max(1, region.get("height", 0))

        aspect = w / h

        if aspect > self.max_aspect_ratio:
            _logger.warning(
                "[ASPECT] reject %.2f (too wide)",
                aspect
            )
            return False

        if aspect < self.min_aspect_ratio:
            _logger.warning(
                "[ASPECT] reject %.2f (too tall)",
                aspect
            )
            return False

        region["aspect_ratio"] = round(aspect, 3)
        region["validated_aspect"] = True
        return True


aspect_validator = AspectValidator()
