"""
segmentation_engine_v2/preprocess/grayscale.py

Deliverable #22
Extract ROI and convert it to grayscale.
"""

import logging
import cv2
import numpy as np

_logger = logging.getLogger(__name__)


class GrayscaleProcessor:

    def extract_roi(self, image, region):
        """
        Crop the parent region from the page image.
        """
        x = int(region.get("x", 0))
        y = int(region.get("y", 0))
        w = int(region.get("width", 0))
        h = int(region.get("height", 0))

        roi = image.crop((x, y, x + w, y + h))

        _logger.warning(
            "[GRAYSCALE] ROI %dx%d extracted",
            roi.width,
            roi.height
        )

        return roi

    def to_grayscale(self, roi):
        """
        Convert PIL ROI to OpenCV grayscale image.
        """
        rgb = np.array(roi)
        gray = cv2.cvtColor(
            rgb,
            cv2.COLOR_RGB2GRAY
        )

        _logger.warning(
            "[GRAYSCALE] converted"
        )

        return gray


grayscale_processor = GrayscaleProcessor()
