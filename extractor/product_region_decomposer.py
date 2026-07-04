import logging
import cv2
import numpy as np
from PIL import Image

_logger = logging.getLogger(__name__)


class ProductRegionDecomposer:

    def decompose(self, page_image, regions):

        output = []

        for region in regions:

            x = region["x"]
            y = region["y"]
            w = region["width"]
            h = region["height"]

            crop = page_image.crop((x, y, x + w, y + h))

            gray = cv2.cvtColor(
                np.array(crop),
                cv2.COLOR_RGB2GRAY
            )

            _, thresh = cv2.threshold(
                gray,
                245,
                255,
                cv2.THRESH_BINARY_INV
            )

            kernel = np.ones((5, 5), np.uint8)

            thresh = cv2.morphologyEx(
                thresh,
                cv2.MORPH_CLOSE,
                kernel
            )

            contours, _ = cv2.findContours(
                thresh,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE
            )

            product_count = 0

            products = []

            for contour in contours:

                area = cv2.contourArea(contour)

                if area < 6000:

                    continue

                rx, ry, rw, rh = cv2.boundingRect(

                    contour

                )

                #
                # Ignore tiny detections
                #

                if rw < 40 or rh < 40:

                    continue

                products.append(

                    {

                        "x": x + rx,

                        "y": y + ry,

                        "width": rw,

                        "height": rh,

                        "area": rw * rh,

                        "type": "product"

                    }

                )

            product_count = len(products)

            # ----------------------------------

            # Intelligent structure decision

            # ----------------------------------

            if region["type"] == "hero":

                structure = "hero_banner"

            elif product_count <=1:

                structure = "single_product"

            elif product_count <=4:

                structure = "product_group"

            else:

                structure = "product_grid"

            region["structure"] = structure

            region["detected_products"] = product_count

                        #
            # Real decomposition
            #

            if structure == "single_product":

                output.append(region)

            else:

                for product in products:

                    product["structure"] = "single_product"

                    product["detected_products"] = 1

                    output.append(product)

            _logger.warning(

                f"[DECOMPOSER] "

                f"{structure} "

                f"objects={product_count}"

            )

        return output


product_region_decomposer = ProductRegionDecomposer()