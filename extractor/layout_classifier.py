import logging

_logger = logging.getLogger(__name__)


class LayoutClassifier:

    def classify(

        self,

        page_features

    ):

        _logger.warning(

            "[LAYOUT] "

            "Default Family A"

        )


class LayoutClassifier:

    def classify(

        self,

        page_features

    ):

        family = "A"

        confidence = 0.95

        # ----------------------------------
        # Family B Indicators
        # ----------------------------------

        if (

            page_features["large_regions"] >= 2

            and

            page_features["small_regions"] >= 4

        ):

            family = "B"

            confidence = 0.90

        _logger.warning(

            "[LAYOUT CLASSIFIER] "

            f"family={family} "

            f"confidence={confidence}"

        )

        return {

            "family": family,

            "confidence": confidence

        }

        