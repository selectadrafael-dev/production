import logging

_logger = logging.getLogger(__name__)


class ProductRegionDecomposer:

    def decompose(

        self,

        image,

        regions

    ):

        output = []

        for region in regions:

            width = region["width"]

            height = region["height"]

            ratio = width / max(height, 1)

            # --------------------------------

            # Single Product

            # --------------------------------

            if ratio < 1.6:

                region["structure"] = "single"

            # --------------------------------

            # Multiple Products

            # --------------------------------

            else:

                region["structure"] = "multiple"

            output.append(region)

        _logger.warning(

            "[REGION DECOMPOSER] "

            f"regions={len(output)}"

        )

        return output


product_region_decomposer = ProductRegionDecomposer()