import logging

from .preprocess import preprocess
from .connected_components import connected_components
from .splitter import splitter
from .validator import validator
from .region_builder import region_builder

_logger = logging.getLogger(__name__)


class SegmentationEngine:

    def segment(
        self,
        image,
        region
    ):
        """
        Parameters
        ----------
        image : PIL.Image
            Full catalogue page.

        region : dict
            Parent region selected by Family B.

        Returns
        -------
        list[dict]
        """

        _logger.warning("[SEGMENTATION ENGINE] START")

        binary = preprocess.process(
            image,
            region
        )

        components = connected_components.extract(
            binary
        )

        components = splitter.execute(
            binary,
            components
        )

        components = validator.validate(
            image,
            components
        )

        regions = region_builder.build(
            region,
            components
        )

        _logger.warning(
            "[SEGMENTATION ENGINE] regions=%d",
            len(regions)
        )
        
        _logger.warning(

        "[SEGMENTATION ENGINE] "

            f"Returning {len(regions)} regions"

        )        

        return regions


segmentation_engine = SegmentationEngine()
