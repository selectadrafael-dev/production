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

# ============================================================
# Vision Pipeline
# ============================================================

class VisionPipeline:

    def __init__(self):

        self.page = None

        self.pipeline = {

            "render": {},

            "observation": {},

            "regions": {

                "count": 0,

                "items": []

            },

            "classification": {

                "items": []

            },

            "products": {

                "count": 0,

                "items": []

            },

            "validation": {},

            "logs": []

        }

    def log(self, message):

        self.pipeline["logs"].append(message)

        _logger.warning(
            f"[VISION TEST] {message}"
        )

    def to_dict(self):

        return {

            "page": self.page,

            "pipeline": self.pipeline

        }


# ==========================================================
# Stage 4
# Draw Region Overlay
# ==========================================================

def _draw_region_overlay(image, regions):

    overlay = image.copy()

    for idx, region in enumerate(regions, start=1):

        x1, y1, x2, y2 = region["bbox"]

        cv2.rectangle(
            overlay,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            3
        )

        cv2.putText(
            overlay,
            f"R{idx}",
            (x1, max(y1 - 10, 30)),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
            cv2.LINE_AA
        )

    return overlay

def _render_page(page):

    pix = page.get_pixmap(

        dpi=200

    )

    page_image = pix.tobytes("png")

    return pix, page_image

# ==========================================================
# Stage 3
# Discover Visual Regions
# ==========================================================

def _discover_regions(image):

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    _, thresh = cv2.threshold(
        gray,
        245,
        255,
        cv2.THRESH_BINARY_INV
    )

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        thresh,
        connectivity=8
    )

    regions = []

    for label in range(1, num_labels):

        x = int(stats[label, cv2.CC_STAT_LEFT])
        y = int(stats[label, cv2.CC_STAT_TOP])
        w = int(stats[label, cv2.CC_STAT_WIDTH])
        h = int(stats[label, cv2.CC_STAT_HEIGHT])
        area = int(stats[label, cv2.CC_STAT_AREA])

        if area < 5000:
            continue

        regions.append({
            "bbox": [x, y, x + w, y + h],
            "area": area
        })

    return regions

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

        pipeline = VisionPipeline()

        regions = _discover_regions(image)
        pipeline.pipeline["regions"]["count"] = len(regions)

        pipeline.pipeline["regions"]["items"] = regions

        pipeline.log(
            f"Detected {len(regions)} regions"
        )

        overlay = _draw_region_overlay(
            image,
            regions
        )

        overlay_filename = os.path.join(
            DEBUG_FOLDER,
            f"page_{page_index+1:03d}_overlay.png"
        )

        overlay_saved = cv2.imwrite(
            overlay_filename,
            overlay
        )

        pipeline.log(
            f"Overlay saved={overlay_saved}"
        )

        pipeline.log(
            "Generated region overlay"
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

        pipeline.log(f"Image saved={saved}")

        pipeline.log(f"Saved to: {original_filename}")


        pipeline.page = page_index + 1

        pipeline.pipeline["observation"] = {

            "orientation":

                "landscape"

                if pix.width > pix.height

                else "portrait",

            "embedded_images": len(
                page.get_images(full=True)
            )
        }

        pipeline.pipeline["render"] = {

            "width": pix.width,

            "height": pix.height,

            "dpi": 200,

            "debug_image": {

                "saved": saved,

                "path": original_filename

            },

            "overlay_image": {

                "saved": overlay_saved,

                "path": overlay_filename

            }

        }

        pages.append(
            pipeline.to_dict()
        )

    document.close()

    return jsonify({

        "success": True,

        "pages": pages

    })