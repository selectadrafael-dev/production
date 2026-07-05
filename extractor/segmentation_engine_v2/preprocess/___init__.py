import logging

from .grayscale import grayscale_processor
from .adaptive_threshold import adaptive_threshold
from .morphology import morphology_processor
from .cleanup import cleanup_processor

_logger = logging.getLogger(__name__)


class Preprocess:

    def process(self, image, region):
        """
        Returns a binary ROI ready for connected components.
        """

        _logger.warning(

            "[PREPROCESS] START"

        )

        roi = grayscale_processor.extract_roi(
            image,
            region
        )

        gray = grayscale_processor.to_grayscale(
            roi
        )

        binary = adaptive_threshold.apply(
            gray
        )

        binary = morphology_processor.apply(
            binary
        )

        binary = cleanup_processor.apply(
            binary
        )

        _logger.warning(
            "[PREPROCESS] complete"
        )

        return binary


preprocess = Preprocess()
