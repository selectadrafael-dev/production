import logging

_logger = logging.getLogger(__name__)


class LayoutClassifier:

    def classify(self, features):

        family = "B"
        confidence = 0.90

        # -----------------------------
        # Family A (Grid Layout)
        # -----------------------------
        if (

            features["large_regions"] <= 2

            and

            features["small_regions"] >= 8

        ):

            family = "A"
            confidence = 0.98

        _logger.warning(

            f"[LAYOUT CLASSIFIER] "

            f"family={family} "

            f"confidence={confidence}"

        )

        return {

            "family": family,

            "confidence": confidence

        }