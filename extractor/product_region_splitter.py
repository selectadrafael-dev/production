import logging
import cv2
import numpy as np

_logger = logging.getLogger(__name__)


class ProductRegionSplitter:

    def split(

        self,

        page_image,

        regions

    ):

        products = []

        for region in regions:

            if region["label"] != "hero":

                products.append(region)

                continue

            x = region["x"]
            y = region["y"]
            w = region["width"]
            h = region["height"]

            crop = page_image[

                y:y+h,

                x:x+w

            ]

            gray = cv2.cvtColor(

                crop,

                cv2.COLOR_BGR2GRAY

            )

            _, thresh = cv2.threshold(

                gray,

                245,

                255,

                cv2.THRESH_BINARY_INV

            )

            kernel = np.ones(

                (5,5),

                np.uint8

            )

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

            found = 0

            for contour in contours:

                rx, ry, rw, rh = cv2.boundingRect(

                    contour

                )

                area = rw * rh

                if area < 12000:

                    continue

                products.append({

                    "label": "product",

                    "type": "product",

                    "x": x + rx,

                    "y": y + ry,

                    "width": rw,

                    "height": rh,

                    "area": area,

                    "source": "splitter"

                })

                found += 1

            _logger.warning(

                f"[REGION SPLITTER] "

                f"hero={w}x{h} "

                f"products={found}"

            )

        return products


product_region_splitter = ProductRegionSplitter()