import logging

_logger = logging.getLogger(__name__)


class LayoutClassifier:

   def classify(

        self,

        features,

        fingerprint

    ):

        family = "B"

        confidence = 0.90

        if (

            fingerprint["region_density"] >= 10

            and

            fingerprint["large_ratio"] <= 2

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