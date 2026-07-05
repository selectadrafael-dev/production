"""
segmentation_engine_v2/preprocess/adaptive_threshold.py

Deliverable #23
Adaptive threshold preprocessing.
"""

import logging
import cv2

_logger = logging.getLogger(__name__)


class AdaptiveThreshold:

    def __init__(self):
        self.block_size = 31
        self.constant = 8

    def apply(self, gray):
        """
        Convert grayscale image into a binary image using
        adaptive Gaussian thresholding.
        """

        binary = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            self.block_size,
            self.constant
        )

        _logger.warning(
            "[ADAPTIVE THRESHOLD] block=%d C=%d",
            self.block_size,
            self.constant
        )

        return binary


adaptive_threshold = AdaptiveThreshold()
