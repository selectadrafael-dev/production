import logging
from product_estimator import product_estimator

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

            structure = "unknown"

            # ----------------------------------
            # Hero Banner
            # ----------------------------------

            if area > 250000:

                label = "hero"

                structure = "hero_banner"

            # ----------------------------------
            # Text Region
            # ----------------------------------

            elif ratio > 2.5:

                label = "text"

                structure = "text_block"

            # ----------------------------------
            # Product Region
            # ----------------------------------

            elif area > 40000:

                label = "product"

                #
                # Temporary structure.
                # Will be refined after estimating products.
                #

                structure = "single_product"

            # ----------------------------------
            # Detail Region
            # ----------------------------------

            else:

                label = "detail"

                structure = "detail"

            # ----------------------------------
            # Estimate Products
            # ----------------------------------

            estimated_products = product_estimator.estimate(

                image,

                region

            )

 
            _logger.warning(

                "[PRODUCT ESTIMATOR] "

                f"label={label} "

                f"structure={structure} "

                f"estimated_products={estimated_products} "

                f"area={area} "

                f"size={width}x{height}"

            )

            #
            # Refine structure using estimated products
            #

            if label == "product":

                if estimated_products >= 8:

                    structure = "product_grid"

                elif estimated_products >= 2:

                    structure = "colour_variants"

                else:

                    structure = "single_product"

            # ----------------------------------
            # Store Classification
            # ----------------------------------

            region["label"] = label

            region["structure"] = structure

            region["estimated_products"] = estimated_products

            classified.append(

                region

            )

        _logger.warning(

            "[REGION CLASSIFIER] "

            f"regions={len(classified)}"

        )

        return classified

    # ==========================================
    # Estimate number of products in a region
    # ==========================================

    def _estimate_products(

        self,

        image,

        region

    ):

        #
        # Temporary implementation.
        # This will be replaced with
        # OpenCV object estimation.
        #

        return 1


region_classifier = RegionClassifier()