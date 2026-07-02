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

            crop = refine_crop(

                crop
            )

            validation = validate_recovered_crop(

                crop=crop,

                contour=contour,

                image_width=image.shape[1],

                image_height=image.shape[0]
            )


            if not validation["accepted"]:

                continue
           
            area = cv2.contourArea(
                contour
            )

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

            # =====================================
            # RECOVERY VALIDATION REPORT
            # =====================================

            validation["score"] = score

            validation["coverage"] = round(

                coverage,

                3
            )

            results.append({
                "clean_index": clean_index,

                "image": encoded,

                "rve_version": 1,

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

                 "coverage": coverage,

                "validation": validation,

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
    
#===========================================================
# Recovery Validation Engine
#===========================================================

def validate_recovered_crop(

    crop,

    contour,

    image_width,

    image_height
):

    try:

        x, y, w, h = cv2.boundingRect(

            contour
        )

        reasons = []

        # =====================================
        # PRODUCT OCCUPANCY
        # =====================================

        bounding_area = max(

            w * h,

            1
        )

        contour_area = cv2.contourArea(

            contour
        )

        occupancy = contour_area / bounding_area

        if occupancy < 0.30:

            reasons.append(

                "low_occupancy"
            )

        # =======================================
        # BORDER TOUCH
        # =======================================

        border = 5

        if (

            x <= border

            or

            y <= border

            or

            (x + w) >= (image_width - border)

            or

            (y + h) >= (image_height - border)

        ):

            reasons.append(

                "border_touch"
            )

        # =====================================
        # SIZE
        # =====================================

        area = w * h

        if area < 4500:

            reasons.append(

                "small_area"
            )

        # =====================================
        # ASPECT
        # =====================================

        ratio = w / float(

            max(

                h,

                1
            )
        )

        if (

            ratio > 4.5

            or

            ratio < 0.22

        ):

            reasons.append(

                "bad_ratio"
            )

        accepted = (

            len(reasons) == 0
        )

        _logger.warning(

            f"[RVE] "

            
            f"x={x} "

            f"y={y} "

            f"w={w} "

            f"h={h} "

            f"area={area} "

            f"ratio={ratio:.2f} "

            f"occupancy={occupancy:.2f} "

            f"accepted={accepted} "

            f"reasons={reasons}"
        )

        return {

            "accepted": accepted,

            "reasons": reasons,

            "occupancy": round(

                occupancy,

                3
            ),

        }

    except Exception:

        _logger.exception(

            "[RVE ERROR]"
        )

        return {

            "accepted": False,

            "reasons": [

                "validator_error"
            ]
        }
    
#===========================================================
# Refine Recovery Crop
#===========================================================

def refine_crop(crop):

    try:

        if crop is None:

            return crop

        image = crop.copy()

        gray = cv2.cvtColor(

            image,

            cv2.COLOR_RGB2GRAY
        )

        _, thresh = cv2.threshold(

            gray,

            245,

            255,

            cv2.THRESH_BINARY_INV
        )

        points = cv2.findNonZero(

            thresh
        )

        if points is None:

            return crop

        x, y, w, h = cv2.boundingRect(

            points
        )

        margin = 6

        x = max(

            0,

            x - margin
        )

        y = max(

            0,

            y - margin
        )

        w = min(

            image.shape[1] - x,

            w + margin * 2
        )

        h = min(

            image.shape[0] - y,

            h + margin * 2
        )

        refined = image[

            y:y+h,

            x:x+w

        ]

        _logger.warning(

            f"[REFINE CROP] "

            f"before={crop.shape[1]}x{crop.shape[0]} "

            f"after={refined.shape[1]}x{refined.shape[0]} "

            f"saved={crop.shape[0]-refined.shape[0]}px"
        )

        # =====================================
        # REMOVE BOTTOM CAPTION STRIP
        # =====================================

        height = refined.shape[0]

        caption = int(

            height * 0.12
        )

        if caption > 20:

            refined = refined[

                :height-caption,

                :
            ]

        return refined

    except Exception:

        _logger.exception(

            "[REFINE CROP ERROR]"
        )

        return crop