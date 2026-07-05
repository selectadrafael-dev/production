"""
segmentation_engine_v2/preprocess/cleanup.py

Deliverable #25
Final cleanup stage before connected component extraction.
"""

import logging
import cv2
import numpy as np

_logger = logging.getLogger(__name__)


class CleanupProcessor:

    def __init__(self):
        self.min_component_area = 80

    def apply(self, binary):
        """
        Remove very small connected components that are
        unlikely to represent products.
        """

        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
            binary,
            connectivity=8
        )

        cleaned = np.zeros_like(binary)

        for label in range(1, num_labels):

            area = stats[label, cv2.CC_STAT_AREA]

            if area < self.min_component_area:
                continue

            cleaned[labels == label] = 255

        _logger.warning(
            "[CLEANUP] kept=%d removed=%d",
            int(np.max(labels)),
            max(0, num_labels - 1)
        )

        return cleaned


cleanup_processor = CleanupProcessor()
