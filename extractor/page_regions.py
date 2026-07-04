import cv2
import numpy as np


class PageRegionAnalyzer:

    def analyze(

        self,

        image

    ):

        page = np.array(image)

        gray = cv2.cvtColor(

            page,

            cv2.COLOR_RGB2GRAY

        )

        #
        # Better threshold
        #

        binary = cv2.adaptiveThreshold(

            gray,

            255,

            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,

            cv2.THRESH_BINARY_INV,

            25,

            8

        )

        #
        # Remove tiny noise
        #

        kernel = np.ones(

            (3, 3),

            np.uint8

        )

        binary = cv2.morphologyEx(

            binary,

            cv2.MORPH_OPEN,

            kernel

        )

        #
        # Merge nearby components
        #

        kernel = np.ones(

            (15, 15),

            np.uint8

        )

        binary = cv2.dilate(

            binary,

            kernel,

            iterations=1

        )

        contours, _ = cv2.findContours(

            binary,

            cv2.RETR_EXTERNAL,

            cv2.CHAIN_APPROX_SIMPLE

        )

        regions = []

        for contour in contours:

            x, y, w, h = cv2.boundingRect(

                contour

            )

            #
            # Ignore tiny regions
            #

            if w < 60 or h < 60:

                continue

            area = w * h

            region_type = "detail"

            if area > 220000:

                region_type = "hero"

            elif area > 25000:

                region_type = "product"

            regions.append({

                "x": x,

                "y": y,

                "width": w,

                "height": h,

                "area": area,

                "type": region_type

            })

        return regions


page_region_analyzer = PageRegionAnalyzer()