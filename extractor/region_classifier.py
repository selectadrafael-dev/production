import logging
#from product_estimator import product_estimator
from segmentation_engine_v2 import segmentation_engine

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

            # ---------------------------------------
            # Detail Region
            # ---------------------------------------

            else:

                label = "detail"

                structure = "detail"

            # --------------------------------------
            # Estimate Products
            # ---------------------------------------
            children = []

            estimated_products = 1

            if label == "product":
                region["label"] = label

                region["structure"] = structure

                children = segmentation_engine.segment(

                    image,

                    region
                )

                estimated_products = len(children)

                if estimated_products == 0:

                    estimated_products = 1

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

            region["children"] = children

            classified.append(

                region

            )


            _logger.warning(

                "[REGION CLASSIFIER] "

                f"Segmentation returned "

                f"{estimated_products} children"

            )

        _logger.warning(

            "[REGION CLASSIFIER] "

            f"regions={len(classified)}"

        )

        return classified


region_classifier = RegionClassifier()