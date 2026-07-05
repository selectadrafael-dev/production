"""
segmentation_engine_v2/splitter/watershed_splitter.py

Deliverable #7
Marker-based watershed splitter for large merged components.
"""

import logging
import cv2
import numpy as np

_logger = logging.getLogger(__name__)


class WatershedSplitter:

    def split(self, binary_image, component):

        x = component["x"]
        y = component["y"]
        w = component["width"]
        h = component["height"]

        roi = binary_image[y:y+h, x:x+w]

        if roi.size == 0:
            return [component]

        work = roi.copy()

        kernel = np.ones((3, 3), np.uint8)

        opening = cv2.morphologyEx(
            work,
            cv2.MORPH_OPEN,
            kernel,
            iterations=1
        )

        sure_bg = cv2.dilate(opening, kernel, iterations=2)

        dist = cv2.distanceTransform(
            opening,
            cv2.DIST_L2,
            5
        )

        _, sure_fg = cv2.threshold(
            dist,
            0.45 * dist.max(),
            255,
            0
        )

        sure_fg = np.uint8(sure_fg)

        count, markers = cv2.connectedComponents(sure_fg)

        if count <= 2:
            return [component]

        children = []

        stats = cv2.connectedComponentsWithStats(
            sure_fg,
            8
        )[2]

        for idx in range(1, len(stats)):
            sx, sy, sw, sh, area = stats[idx]

            if area < 600:
                continue

            children.append({
                "x": x + int(sx),
                "y": y + int(sy),
                "width": int(sw),
                "height": int(sh),
                "area": int(area),
                "source": "watershed_splitter"
            })

        if not children:
            children.append(component)

        _logger.warning(
            "[WATERSHED] parent=1 children=%d",
            len(children)
        )

        return children


watershed_splitter = WatershedSplitter()
