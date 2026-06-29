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

        results = []

        for contour in contours:

            area = cv2.contourArea(contour)

            if area < 8000:
                continue

            x, y, w, h = cv2.boundingRect(contour)
           
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

            crop_pil = Image.fromarray(crop)

            buffer = io.BytesIO()

            crop_pil.save(
                buffer,
                format="JPEG",
                quality=75
            )

            encoded = base64.b64encode(

                buffer.getvalue()

            ).decode("utf-8")

            page_area = max(

                image.shape[0] * image.shape[1],

                1
            )

            crop_area = w * h

            coverage = crop_area / page_area

            score = round(

                coverage * 100,

                2
            )

            clean_index = len(results)

            results.append({
                "clean_index": clean_index,

                "image": encoded,

                "x": x,

                "y": y,

                "width": w,

                "height": h,

                "score": score,

                "crop_area": crop_area,

                "large_area": coverage > 0.18,

                "large_image": coverage > 0.30,

                "portrait": h > w,

                "is_lifestyle": False,

                "lifestyle_score": 0,

                "hero_score": score,

                "gallery_score": score,

                "needs_extractor_crop": True
            })


        results.sort(

            key=lambda x: x["score"],

            reverse=True
        )

        return results

    except Exception:

        return []
    

def recover_region(region):

    try:

        page_image = region.get(

            "page_image"
        )

        if not page_image:

            return []

        x = int(region["x"])
        y = int(region["y"])
        w = int(region["width"])
        h = int(region["height"])

        image_bytes = base64.b64decode(

            page_image
        )

        image = Image.open(

            io.BytesIO(image_bytes)

        ).convert("RGB")

        crop = image.crop(

            (

                x,

                y,

                x + w,

                y + h

            )
        )

        return segment_catalog_page(

            crop
        )

    except Exception:

        _logger.exception(

            "[RECOVER REGION ERROR]"
        )

        return []
    