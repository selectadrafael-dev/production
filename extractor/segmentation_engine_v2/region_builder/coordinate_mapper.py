"""
segmentation_engine_v2/region_builder/coordinate_mapper.py

Deliverable #18
Maps child component coordinates from ROI space back to page space.
"""

import logging
import copy

_logger = logging.getLogger(__name__)


class CoordinateMapper:

    def map(self, parent_region, component):
        """
        Convert ROI-relative coordinates into page coordinates.
        """

        region = copy.deepcopy(component)

        parent_x = int(parent_region.get("x", 0))
        parent_y = int(parent_region.get("y", 0))

        region["x"] = parent_x + int(component.get("x", 0))
        region["y"] = parent_y + int(component.get("y", 0))

        region["parent_x"] = parent_x
        region["parent_y"] = parent_y
        region["mapped"] = True

        _logger.warning(
            "[COORDINATE MAPPER] (%d,%d)->(%d,%d)",
            component.get("x", 0),
            component.get("y", 0),
            region["x"],
            region["y"]
        )

        return region


coordinate_mapper = CoordinateMapper()
