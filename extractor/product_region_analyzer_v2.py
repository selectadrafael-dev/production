import logging

from segmentation_engine_v2 import segmentation_engine

_logger = logging.getLogger(__name__)


class ProductRegionAnalyzerV2:
    """
    Drop-in replacement for ProductRegionAnalyzer.

    Input:
        image  : PIL.Image
        region : dict

    Output:
        list[dict]
    """

    def analyze(self, image, region):

        try:

            _logger.warning(

                "[PRODUCT ANALYZER V2] "

                "Calling Segmentation Engine"

            )

            children = region.get(

                "children",

                []
            )

            if not children:

                _logger.warning(

                    "[PRODUCT ANALYZER V2] "

                    "No cached children"

                )

                return [region]
           
            _logger.warning(

                "[PRODUCT ANALYZER V2] "

                f"Segmentation returned {len(children)} regions"

            )
        except Exception as exc:
            _logger.exception(
                "[PRODUCT ANALYZER V2] segmentation failed: %s",
                exc
            )
            return [region]

        if not children:
            _logger.warning(
                "[PRODUCT ANALYZER V2] no child regions"
            )
            return [region]

        validated = []

        for child in children:

            if self._is_valid(child):
                validated.append(child)

        if not validated:
            return [region]

        _logger.warning(
            "[PRODUCT ANALYZER V2] parent=1 children=%d",
            len(validated)
        )

        return validated

    def _is_valid(self, region):

        width = region.get("width", 0)
        height = region.get("height", 0)

        if width < 20:
            return False

        if height < 20:
            return False

        if width * height < 800:
            return False

        region.setdefault("type", "product")
        region.setdefault("source", "segmentation_v2")

        return True


product_region_analyzer_v2 = ProductRegionAnalyzerV2()
