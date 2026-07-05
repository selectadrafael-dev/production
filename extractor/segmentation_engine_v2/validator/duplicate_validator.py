"""
segmentation_engine_v2/validator/duplicate_validator.py

Deliverable #14
Remove duplicate / highly-overlapping validated regions.
"""

import logging

_logger = logging.getLogger(__name__)


class DuplicateValidator:

    def __init__(self):
        self.iou_threshold = 0.85

    def validate(self, region, accepted):

        for existing in accepted:
            if self._iou(region, existing) >= self.iou_threshold:
                _logger.warning(
                    "[DUPLICATE] rejected overlap"
                )
                return False

        region["validated_duplicate"] = True
        return True

    def _iou(self, a, b):

        ax1, ay1 = a["x"], a["y"]
        ax2, ay2 = ax1 + a["width"], ay1 + a["height"]

        bx1, by1 = b["x"], b["y"]
        bx2, by2 = bx1 + b["width"], by1 + b["height"]

        ix1 = max(ax1, bx1)
        iy1 = max(ay1, by1)
        ix2 = min(ax2, bx2)
        iy2 = min(ay2, by2)

        if ix2 <= ix1 or iy2 <= iy1:
            return 0.0

        inter = (ix2-ix1)*(iy2-iy1)
        area_a = a["width"]*a["height"]
        area_b = b["width"]*b["height"]
        union = area_a + area_b - inter

        return inter / union if union else 0.0


duplicate_validator = DuplicateValidator()
