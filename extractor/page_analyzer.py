import cv2
import numpy as np
from PIL import Image


class PageAnalyzer:

    def analyze(self, image):

        page = np.array(image)

        gray = cv2.cvtColor(
            page,
            cv2.COLOR_RGB2GRAY
        )

        height, width = gray.shape

        # ---------------------------------

        # Binary image

        # ---------------------------------

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

        large_regions = 0

        small_regions = 0

        total_regions = len(contours)

        for contour in contours:

            x, y, w, h = cv2.boundingRect(
                contour
            )

            area = w * h

            if area > 60000:

                large_regions += 1

            elif area > 3000:

                small_regions += 1

        return {

            "page_width": width,

            "page_height": height,

            "total_regions": total_regions,

            "large_regions": large_regions,

            "small_regions": small_regions

        }
    


page_analyzer = PageAnalyzer()