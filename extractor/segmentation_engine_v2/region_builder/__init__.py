import logging

from .coordinate_mapper import coordinate_mapper
from .region_factory import region_factory
from .metadata_enricher import metadata_enricher

_logger=logging.getLogger(__name__)

class RegionBuilder:

    def build(self,parent_region,components):
        regions=[]
        for component in components:

            mapped = coordinate_mapper.map(
                parent_region,
                component
            )

            region = region_factory.create(
                mapped
            )

            region = metadata_enricher.enrich(
                region
            )

            regions.append(region)

        _logger.warning(
            "[REGION BUILDER] components=%d regions=%d",
            len(components),
            len(regions)
        )
        return regions

region_builder=RegionBuilder()
