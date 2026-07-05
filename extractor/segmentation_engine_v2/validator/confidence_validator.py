"""
segmentation_engine_v2/validator/confidence_validator.py

Deliverable #15
Assign a confidence score to validated regions.
"""

import logging

_logger = logging.getLogger(__name__)


class ConfidenceValidator:

    def __init__(self):
        self.minimum_score = 60.0

    def validate(self, region):

        score = 100.0

        if not region.get("validated_size"):
            score -= 25

        if not region.get("validated_aspect"):
            score -= 20

        if not region.get("validated_white_object"):
            score -= 30

        score = max(score, 0.0)

        region["confidence"] = round(score, 1)

        if score < self.minimum_score:
            _logger.warning(
                "[CONFIDENCE] reject score=%.1f",
                score
            )
            return False

        _logger.warning(
            "[CONFIDENCE] accept score=%.1f",
            score
        )
        return True


confidence_validator = ConfidenceValidator()
