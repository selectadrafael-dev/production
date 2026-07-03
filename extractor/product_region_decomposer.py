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

            area = region["area"]

            ratio = width / max(height, 1)

            structure = "single_product"

            # ---------------------------------
            # Very Large Region
            # ---------------------------------

            if area > 350000:

                structure = "hero_banner"

            # ---------------------------------
            # Wide Grid
            # ---------------------------------

            elif ratio > 1.8:

                structure = "product_grid"

            # ---------------------------------
            # Tall Lifestyle
            # ---------------------------------

            elif ratio < 0.60:

                structure = "lifestyle"

            region["structure"] = structure

            output.append(region)

            _logger.warning(

                f"[DECOMPOSER] "

                f"{structure} "

                f"{width}x{height}"

            )

        return output


product_region_decomposer = ProductRegionDecomposer()