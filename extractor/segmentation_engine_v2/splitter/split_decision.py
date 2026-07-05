"""
segmentation_engine_v2/splitter/split_decision.py

Deliverable #5
Decides which splitting strategy should be used for a component.
"""

import logging

_logger = logging.getLogger(__name__)


class SplitDecision:

    def __init__(self):
        self.watershed_area = 50000
        self.aspect_ratio_limit = 2.2

    def choose(self, component):
        """
        Return one of:
            contour
            watershed
            none
        """

        w = component.get("width", 0)
        h = component.get("height", 0)
        area = component.get("area", w * h)

        if w <= 0 or h <= 0:
            return "none"

        aspect = max(w, h) / max(1, min(w, h))

        # Very elongated or very large blobs
        # are likely merged products.
        if area >= self.watershed_area:
            strategy = "watershed"

        elif aspect >= self.aspect_ratio_limit:
            strategy = "watershed"

        else:
            strategy = "contour"

        _logger.warning(
            "[SPLIT DECISION] area=%d aspect=%.2f strategy=%s",
            area,
            aspect,
            strategy
        )

        return strategy


split_decision = SplitDecision()
