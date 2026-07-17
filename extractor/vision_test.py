import fitz
import cv2
import numpy as np
import logging
import os

from flask import jsonify

_logger = logging.getLogger(__name__)

# ============================================================
# Vision Debug Folder
# ============================================================

DEBUG_FOLDER = "vision_debug"

os.makedirs(

    DEBUG_FOLDER,

    exist_ok=True

)


def process_catalog(file):

    """
    Vision Engine Laboratory

    Version 1

    Purpose:
        - Read PDF
        - Inspect every page
        - Return diagnostics

    No extraction.

    No segmentation.

    No AI.

    """

    pdf_bytes = file.read()

    document = fitz.open(

        stream=pdf_bytes,

        filetype="pdf"

    )

    pages = []

    for page_index in range(len(document)):

        page = document.load_page(

            page_index

        )

        pix = page.get_pixmap(

            dpi=200

        )

        # =====================================================
        # Render Page Image
        # =====================================================

        page_image = pix.tobytes("png")

        # =====================================================
        # Decode page image
        # =====================================================

        image = np.frombuffer(

            page_image,

            np.uint8

        )

        image = cv2.imdecode(

            image,

            cv2.IMREAD_COLOR

        )

        # ============================================================
        # Save Original Page
        # ============================================================

        original_filename = os.path.join(

            DEBUG_FOLDER,

            f"page_{page_index+1:03d}_original.png"

        )

        cv2.imwrite(

            original_filename,

            image
        )

        # =====================================================
        # Visual Saliency
        # =====================================================

        saliency = cv2.saliency.StaticSaliencyFineGrained_create()

        success, saliency_map = saliency.computeSaliency(image)

        if success:

            saliency_map = (

                saliency_map * 255

            ).astype("uint8")

            average_saliency = float(

                np.mean(

                    saliency_map

                )

            )

        else:

            average_saliency = 0.0

        page_info = {

            "page": page_index + 1,

            "pdf": {

                "width": pix.width,

                "height": pix.height,

                "image_count": len(

                    page.get_images(

                        full=True

                    )

                )

            },

            "vision": {

                "page_image_bytes": len(page_image),

                "orientation":

                    "landscape"

                    if pix.width > pix.height

                    else "portrait",

                "average_saliency": round(

                    average_saliency,

                    2

                )

            },

            "diagnostics":[

                {

                    "original_page":

                        original_filename

                }

            ]
        }

        pages.append(

            page_info
        )

        _logger.warning(

            f"[VISION TEST] {page_info}"

        )

    document.close()

    return jsonify({

        "success": True,

        "pages": pages

    })