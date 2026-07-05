"""
segmentation_engine_v2/region_builder/region_factory.py

Deliverable #19
Creates standardized region dictionaries for downstream processing.
"""

import logging
import copy

_logger = logging.getLogger(__name__)


class RegionFactory:

    def create(self, component):

        region = copy.deepcopy(component)

        region.setdefault("type", "product")
        region.setdefault("label", "product")
        region.setdefault("structure", "single_product")
        region.setdefault("confidence", 0.0)
        region.setdefault("children", [])
        region.setdefault("metadata", {})
        region.setdefault("source", "segmentation_engine_v2")

        region["bbox"] = {
            "x": region["x"],
            "y": region["y"],
            "width": region["width"],
            "height": region["height"],
        }

        _logger.warning(
            "[REGION FACTORY] (%d,%d,%d,%d)",
            region["x"],
            region["y"],
            region["width"],
            region["height"]
        )

        return region


region_factory = RegionFactory()
