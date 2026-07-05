"""
connected_components.py

Deliverable #3
Segmentation Engine V2 component.
"""

import logging
import cv2
import numpy as np

_logger = logging.getLogger(__name__)


class ConnectedComponents:

    def extract(self, binary_image, min_area=600):

        count, labels, stats, _ = cv2.connectedComponentsWithStats(
            binary_image,
            connectivity=8
        )

        components = []

        for idx in range(1, count):

            x = int(stats[idx, cv2.CC_STAT_LEFT])
            y = int(stats[idx, cv2.CC_STAT_TOP])
            w = int(stats[idx, cv2.CC_STAT_WIDTH])
            h = int(stats[idx, cv2.CC_STAT_HEIGHT])
            area = int(stats[idx, cv2.CC_STAT_AREA])

            if area < min_area:
                continue

            mask = (labels == idx).astype(np.uint8) * 255

            components.append({
                "x": x,
                "y": y,
                "width": w,
                "height": h,
                "area": area,
                "mask": mask
            })

        _logger.warning(
            "[CONNECTED COMPONENTS] kept=%d total=%d",
            len(components),
            count - 1
        )

        return components


connected_components = ConnectedComponents()
