import logging

from .split_decision import split_decision
from .contour_splitter import contour_splitter
from .merge import merge_regions
from .scoring import split_scoring

_logger = logging.getLogger(__name__)


class SplitterEngine:

    def execute(
        self,
        binary_image,
        components
    ):
        """
        Execute the appropriate splitting strategy.

        Parameters
        ----------
        binary_image : numpy.ndarray
            Binary ROI image.

        components : list[dict]
            Connected components extracted from the ROI.

        Returns
        -------
        list[dict]
        """

        output = []

        for component in components:

            strategy = split_decision.choose(component)

            if strategy == "contour":

                result = contour_splitter.split(
                    binary_image,
                    component
                )

            elif strategy == "watershed":

                from .watershed_splitter import watershed_splitter

                result = watershed_splitter.split(
                    binary_image,
                    component
                )

            else:
                result = [component]

            output.extend(result)

        output = merge_regions.execute(output)

        output = split_scoring.score(output)

        _logger.warning(
            "[SPLITTER] input=%d output=%d",
            len(components),
            len(output)
        )

        return output


splitter = SplitterEngine()
