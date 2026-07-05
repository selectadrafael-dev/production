"""
segmentation_engine_v2/validator/white_object_validator.py

Deliverable #13
"""

import logging
import cv2
import numpy as np

_logger = logging.getLogger(__name__)

class WhiteObjectValidator:

    def __init__(self):
        self.min_edge_pixels = 120
        self.min_foreground_ratio = 0.015

    def validate(self, page_image, region):
        x = int(region["x"])
        y = int(region["y"])
        w = int(region["width"])
        h = int(region["height"])

        crop = np.array(page_image.crop((x, y, x + w, y + h)))
        gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)

        edges = cv2.Canny(gray, 40, 120)
        edge_pixels = int(np.count_nonzero(edges))

        _, fg = cv2.threshold(gray,245,255,cv2.THRESH_BINARY_INV)
        foreground_ratio = np.count_nonzero(fg) / float(max(1, fg.size))

        region["edge_pixels"] = edge_pixels
        region["foreground_ratio"] = round(foreground_ratio,4)

        if edge_pixels >= self.min_edge_pixels:
            region["validated_white_object"] = True
            return True

        if foreground_ratio >= self.min_foreground_ratio:
            region["validated_white_object"] = True
            return True

        _logger.warning(
            "[WHITE VALIDATOR] reject edges=%d fg=%.4f",
            edge_pixels,
            foreground_ratio
        )
        return False

white_object_validator = WhiteObjectValidator()
