import logging

_logger = logging.getLogger(__name__)

import logging

_logger = logging.getLogger(__name__)

try:
    from .preprocess import preprocess
    _logger.warning("[IMPORT] preprocess OK")
except Exception:
    _logger.exception("[IMPORT] preprocess FAILED")
    raise

try:
    from .connected_components import connected_components
    _logger.warning("[IMPORT] connected_components OK")
except Exception:
    _logger.exception("[IMPORT] connected_components FAILED")
    raise

try:
    from .splitter import splitter
    _logger.warning("[IMPORT] splitter OK")
except Exception:
    _logger.exception("[IMPORT] splitter FAILED")
    raise

try:
    from .validator import validator
    _logger.warning("[IMPORT] validator OK")
except Exception:
    _logger.exception("[IMPORT] validator FAILED")
    raise

try:
    from .region_builder import region_builder
    _logger.warning("[IMPORT] region_builder OK")
except Exception:
    _logger.exception("[IMPORT] region_builder FAILED")
    raise


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
            Parents region selected by Family B.

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
