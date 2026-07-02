import logging

_logger = logging.getLogger(__name__)


class RegionClassifier:

    def classify(

        self,

        image,

        regions

    ):

        classified = []

        for region in regions:

            area = region["area"]

            width = region["width"]

            height = region["height"]

            ratio = width / max(height, 1)

            label = "unknown"

            # -----------------------------
            # Very Large Region
            # -----------------------------

            if area > 250000:

                label = "hero"

            # -----------------------------
            # Wide Region
            # -----------------------------

            elif ratio > 2.5:

                label = "text"

            # -----------------------------
            # Medium Region
            # -----------------------------

            elif area > 40000:

                label = "product"

            # -----------------------------
            # Small Region
            # -----------------------------

            else:

                label = "detail"

            region["label"] = label

            classified.append(region)

        _logger.warning(

            f"[REGION CLASSIFIER] "

            f"regions={len(classified)}"

        )

        return classified


region_classifier = RegionClassifier()