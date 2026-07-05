"""
segmentation_engine_v2/splitter/contour_splitter.py

Deliverable #6
Fast contour-based splitter used before watershed.
"""

import logging
import cv2

_logger = logging.getLogger(__name__)


class ContourSplitter:

    def split(self, binary_image, component):
        """
        Split a connected component using contour analysis.
        Returns a list of child component dictionaries.
        """

        x = component["x"]
        y = component["y"]
        w = component["width"]
        h = component["height"]

        roi = binary_image[y:y+h, x:x+w]

        contours, _ = cv2.findContours(
            roi,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        children = []

        for contour in contours:

            rx, ry, rw, rh = cv2.boundingRect(contour)

            area = rw * rh

            if area < 600:
                continue

            children.append({
                "x": x + rx,
                "y": y + ry,
                "width": rw,
                "height": rh,
                "area": area,
                "source": "contour_splitter"
            })

        if not children:
            children.append(component)

        _logger.warning(
            "[CONTOUR SPLITTER] parent=1 children=%d",
            len(children)
        )

        return children


contour_splitter = ContourSplitter()
