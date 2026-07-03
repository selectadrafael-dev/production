import logging

_logger = logging.getLogger(__name__)


class GridDetector:

    def detect(self, regions):

        medium = 0
        large = 0

        for region in regions:

            area = region["area"]

            if area > 250000:

                large += 1

            elif area > 35000:

                medium += 1

        is_grid = (

            medium >= 8

            and

            large <= 2

        )

        _logger.warning(

            f"[GRID DETECTOR] "

            f"medium={medium} "

            f"large={large} "

            f"is_grid={is_grid}"

        )

        return {

            "is_grid": is_grid,

            "medium": medium,

            "large": large

        }


grid_detector = GridDetector()