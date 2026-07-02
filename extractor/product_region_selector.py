import logging

_logger = logging.getLogger(__name__)


class ProductRegionSelector:

    def select(

        self,

        regions

    ):

        selected = []

        for region in regions:

            if region["label"] in (

                "hero",

                "product"

            ):

                selected.append(region)

        _logger.warning(

            "[PRODUCT REGION SELECTOR] "

            f"selected={len(selected)}"

        )

        return selected


product_region_selector = ProductRegionSelector()