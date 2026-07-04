import logging
import cv2
import numpy as np

_logger = logging.getLogger(__name__)


class UniversalContourDetector:

    def detect(

        self,

        page_image

    ):

        image = np.array(page_image)

        gray = cv2.cvtColor(

            image,

            cv2.COLOR_RGB2GRAY

        )

        #
        # ----------------------------------------
        # Primary Detection
        # (Adaptive Threshold)
        # ----------------------------------------
        #

        thresh = cv2.adaptiveThreshold(

            gray,

            255,

            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,

            cv2.THRESH_BINARY_INV,

            21,

            5

        )

        kernel = cv2.getStructuringElement(

            cv2.MORPH_RECT,

            (5, 5)

        )

        thresh = cv2.morphologyEx(

            thresh,

            cv2.MORPH_CLOSE,

            kernel,

            iterations=1

        )

        contours, _ = cv2.findContours(

            thresh,

            cv2.RETR_EXTERNAL,

            cv2.CHAIN_APPROX_SIMPLE

        )

        #
        # ----------------------------------------
        # Edge fallback
        # ----------------------------------------
        #

        if len(contours) < 5:

            _logger.warning(

                "[UNIVERSAL DETECTOR] "

                "Using Edge Fallback"

            )

            edges = cv2.Canny(

                gray,

                50,

                150

            )

            edge_contours, _ = cv2.findContours(

                edges,

                cv2.RETR_EXTERNAL,

                cv2.CHAIN_APPROX_SIMPLE

            )

            if len(edge_contours) > len(contours):

                contours = edge_contours

        #
        # ----------------------------------------
        # Build Regions
        # ----------------------------------------
        #

        regions = []

        for contour in contours:

            area = cv2.contourArea(

                contour

            )

            if area < 1500:

                continue

            x, y, w, h = cv2.boundingRect(

                contour

            )

            #
            # Ignore tiny detections
            #

            if w < 35:

                continue

            if h < 35:

                continue

            ratio = w / max(h, 1)

            #
            # Ignore long text lines
            #

            if ratio > 8:

                continue

            #
            # Ignore vertical rules
            #

            if ratio < 0.12:

                continue

            region = {

                "x": x,

                "y": y,

                "width": w,

                "height": h,

                "area": w * h,

                "type": "product",

                #
                # Required by Group B
                #

                "label": None,

                "structure": None,

                "estimated_products": 1,

                "detected_products": 1

            }

            regions.append(

                region

            )

        #
        # Largest first
        #

        regions = sorted(

            regions,

            key=lambda r: r["area"],

            reverse=True

        )

        _logger.warning(

            "[UNIVERSAL DETECTOR] "

            f"regions={len(regions)}"

        )

        return regions


universal_contour_detector = UniversalContourDetector()