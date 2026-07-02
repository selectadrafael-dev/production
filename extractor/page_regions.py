import cv2
import numpy as np


class PageRegionAnalyzer:

    def analyze(self, image):

        page = np.array(image)

        gray = cv2.cvtColor(
            page,
            cv2.COLOR_RGB2GRAY
        )

        binary = cv2.threshold(

            gray,

            245,

            255,

            cv2.THRESH_BINARY_INV

        )[1]

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

            if w < 80 or h < 80:

                continue

            area = w * h

            region_type = "unknown"

            if area > 180000:

                region_type = "hero"

            elif area > 30000:

                region_type = "product"

            else:

                region_type = "detail"

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