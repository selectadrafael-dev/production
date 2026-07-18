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

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DEBUG_FOLDER = os.path.join(
    BASE_DIR,
    "vision_debug"
)

os.makedirs(
    DEBUG_FOLDER,
    exist_ok=True
)

_logger.warning(
    f"[VISION TEST] Debug folder: {DEBUG_FOLDER}"
)

# ==========================================================
# Stage 1
# Render Page
# ==========================================================

def _render_page(page):

    pix = page.get_pixmap(

        dpi=200

    )

    page_image = pix.tobytes("png")

    return pix, page_image

# ==========================================================
# Stage 2
# Observe Page
# ==========================================================

def _observe_page(

    pix,

    page_image

):

    return {

        "pdf": {

            "width": pix.width,

            "height": pix.height

        },

        "vision": {

            "orientation":

                "landscape"

                if pix.width > pix.height

                else "portrait"

        },

        "diagnostics": []

    }

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

        pix, page_image = _render_page(

            page
        )

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

        if image is None:
            raise RuntimeError("Failed to decode rendered page image.")

        # ==========================================================
        # Save Original Page
        # ==========================================================

        original_filename = os.path.join(

            DEBUG_FOLDER,

            f"page_{page_index+1:03d}_original.png"

        )

        saved = cv2.imwrite(
            original_filename,
            image
        )

        _logger.warning(
            f"[VISION TEST] Image saved={saved}"
        )

        _logger.warning(
            f"[VISION TEST] Saved to: {original_filename}"
        )


        page_info = _observe_page(

            pix,

            page_image

        )

        page_info["page"] = page_index + 1

        page_info["pdf"]["image_count"] = len(
            page.get_images(
                full=True
            )
        )

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