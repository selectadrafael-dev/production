"""
segmentation_engine_v2/region_builder/metadata_enricher.py

Deliverable #20
Populate standard metadata placeholders on regions.
"""

import copy
import logging

_logger = logging.getLogger(__name__)


class MetadataEnricher:

    def enrich(self, region):

        enriched = copy.deepcopy(region)

        enriched.setdefault("metadata", {})

        meta = enriched["metadata"]

        meta.setdefault("name", None)
        meta.setdefault("sku", None)
        meta.setdefault("price", None)
        meta.setdefault("colour", None)
        meta.setdefault("material", None)
        meta.setdefault("capacity", None)
        meta.setdefault("description", None)

        enriched["metadata_ready"] = True

        _logger.warning(
            "[METADATA ENRICHER] ready=%s",
            enriched["metadata_ready"]
        )

        return enriched


metadata_enricher = MetadataEnricher()
