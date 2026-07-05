"""
segmentation_engine_v2/splitter/merge.py

Deliverable #8
Merge duplicate or heavily overlapping split regions.
"""

import logging

_logger = logging.getLogger(__name__)


class MergeRegions:

    def execute(self, regions, iou_threshold=0.85):

        if len(regions) <= 1:
            return regions

        output = []

        for region in regions:

            duplicate = False

            for kept in output:
                if self._iou(region, kept) >= iou_threshold:
                    duplicate = True
                    break

            if not duplicate:
                output.append(region)

        _logger.warning(
            "[MERGE] input=%d output=%d",
            len(regions),
            len(output)
        )

        return output

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

        inter = (ix2 - ix1) * (iy2 - iy1)
        area_a = a["width"] * a["height"]
        area_b = b["width"] * b["height"]
        union = area_a + area_b - inter

        return inter / union if union else 0.0


merge_regions = MergeRegions()
