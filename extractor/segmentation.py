import base64
import io
import logging

import cv2
import numpy as np

from PIL import Image

_logger = logging.getLogger(__name__)


def segment_catalog_page(pil_image):

    try:

        image = np.array(pil_image)

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_RGB2GRAY
        )

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

        _logger.warning(

            f"[CONTOUR COUNT] "

            f"{len(contours)}"

        )

        results = []

        for contour in contours:

            area = cv2.contourArea(contour)

            if area < 8000:
                continue

            x, y, w, h = cv2.boundingRect(contour)

            _logger.warning(

                f"[CONTOUR FOUND] "

                f"x={x} "

                f"y={y} "

                f"w={w} "

                f"h={h} "

                f"area={w*h}"

            )
           
            area = cv2.contourArea(
                contour
            )

            if area < 4500:

                _logger.warning(

                    f"[EXTRACTOR REJECT AREA] "

                    f"area={area}"
                )

                continue

            if w < 120 or h < 120:
                continue

            ratio = w / float(h)

            if ratio > 4.5 or ratio < 0.22:
                continue

            crop = image[
                y:y+h,
                x:x+w
            ]

            crop_pil = numpy_to_pil(

                crop
            )

            results.append(

                encode_image(

                    crop_pil
                )
            )

        return results[:12]

    except Exception:

        _logger.exception(

            "[SEGMENTATION ERROR]"

        )

        return []
    