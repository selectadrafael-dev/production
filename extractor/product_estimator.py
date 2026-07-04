import cv2
import numpy as np


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

        products = 0

        for contour in contours:

            area = cv2.contourArea(

                contour

            )

            if area > 4000:

                products += 1

        return max(

            1,

            products

        )


product_estimator = ProductEstimator()