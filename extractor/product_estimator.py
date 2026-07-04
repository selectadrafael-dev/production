import cv2
import numpy as np
import logging

_logger = logging.getLogger(__name__)

class ProductEstimator:

    def estimate(

        self,

        image,

        region

    ):

        x = region["x"]
        y = region["y"]
        w = region["width"]
        h = region["height"]

        _logger.warning(

            "[PRODUCT ESTIMATOR START] "

            f"bbox=({x},{y},{w},{h})"

        )

        roi = image.crop(

            (

                x,

                y,

                x + w,

                y + h

            )

        )

        img = np.array(roi)

        gray = cv2.cvtColor(

            img,

            cv2.COLOR_RGB2GRAY

        )

        edges = cv2.Canny(

            gray,

            60,

            180

        )

        contours, _ = cv2.findContours(

            edges,

            cv2.RETR_EXTERNAL,

            cv2.CHAIN_APPROX_SIMPLE

        )

        _logger.warning(

            "[PRODUCT ESTIMATOR] "

            f"total_contours={len(contours)}"

        )

        products = 0

        for contour in contours:

            area = cv2.contourArea(

                contour

            )

            x2, y2, w2, h2 = cv2.boundingRect(

                contour

            )

            _logger.warning(

                "[PRODUCT ESTIMATOR] "

                f"area={int(area)} "

                f"bbox=({x2},{y2},{w2},{h2})"

            )


            if area > 4000:

                products += 1

                _logger.warning(

                    "[PRODUCT ESTIMATOR] "

                    f"ACCEPT contour "

                    f"#{products}"

                )

            else:

                _logger.warning(

                    "[PRODUCT ESTIMATOR] "

                    "REJECT contour"

                )


        estimated = max(

            1,

            products

        )

        _logger.warning(

            "[PRODUCT ESTIMATOR RESULT] "

            f"estimated_products={estimated}"

        )

        return estimated


product_estimator = ProductEstimator()