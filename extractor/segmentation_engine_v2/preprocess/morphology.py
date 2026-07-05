"""
segmentation_engine_v2/preprocess/morphology.py

Deliverable #24
Morphological refinement of the binary image.
"""

import logging
import cv2
import numpy as np

_logger = logging.getLogger(__name__)


class MorphologyProcessor:

    def __init__(self):
        self.kernel_size = (3, 3)
        self.open_iterations = 1
        self.close_iterations = 1

    def apply(self, binary):
        """
        Remove small noise and reconnect fragmented products.
        """

        kernel = np.ones(self.kernel_size, np.uint8)

        cleaned = cv2.morphologyEx(
            binary,
            cv2.MORPH_OPEN,
            kernel,
            iterations=self.open_iterations
        )

        cleaned = cv2.morphologyEx(
            cleaned,
            cv2.MORPH_CLOSE,
            kernel,
            iterations=self.close_iterations
        )

        _logger.warning(
            "[MORPHOLOGY] kernel=%s open=%d close=%d",
            self.kernel_size,
            self.open_iterations,
            self.close_iterations
        )

        return cleaned


morphology_processor = MorphologyProcessor()
