import logging

_logger = logging.getLogger(__name__)


class ProductCandidateBuilder:

    def build(

        self,

        family,

        page,

        products

    ):

        candidates = []

        for index, product in enumerate(products):

            candidate = {

                "id": f"P{page}_{index+1}",

                "family": family,

                "page": page,

                "bbox": {

                    "x": product["x"],

                    "y": product["y"],

                    "width": product["width"],

                    "height": product["height"]

                },

                "classification": product.get(

                    "label"

                ),

                "layout": product.get(

                    "structure"

                ),
               
                # "crop": {

                #     "image": product.get(

                #         "image"

                #     ),

                

                #     "width": product.get(

                #         "crop_width"

                #     ),

                #     "height": product.get(

                #         "crop_height"

                #     ),

                #     "size": product.get(

                #         "image_size"

                #     )

                # },

                "crop": {

                    #
                    # PIL image for QA
                    #

                    "image": product.get(

                        "crop_image"

                    ),

                    #
                    # Base64 for AI
                    #

                    "encoded": product.get(

                        "image"

                    ),

                    "width": product.get(

                        "crop_width"

                    ),

                    "height": product.get(

                        "crop_height"

                    ),

                    "size": product.get(

                        "image_size"

                    )

                },

                "metadata": {

                    "name": None,

                    "sku": None,

                    "price": None,

                    "stock": None,

                    "colour": None,

                    "capacity": None,

                    "material": None,

                    "description": None

                },

                "confidence":0.0

            }

            candidates.append(candidate)

                _logger.warning(

            "[CANDIDATE] "

            f"{candidate['id']} "

            f"crop_image="

            f"{candidate['crop']['image'] is not None}"

        )

        _logger.warning(

            f"[CANDIDATE BUILDER] "

            f"built={len(candidates)}"

        )

        return candidates


product_candidate_builder = ProductCandidateBuilder()