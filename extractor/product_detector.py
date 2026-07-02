import logging

_logger = logging.getLogger(__name__)


class ProductDetector:

    def process(self, page):

        accepted = 0

        for asset in page.assets:

            vision = asset.metadata.get("vision", {})

            if vision.get("label") == "product":

                accepted += 1

        _logger.warning(

            "[PRODUCT DETECTOR] "

            f"accepted={accepted} "

            f"total={len(page.assets)}"

        )

        return page


product_detector = ProductDetector()