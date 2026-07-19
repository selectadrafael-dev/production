import fitz
import cv2
import numpy as np
import logging
import os
import base64

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
# Region Inspector
# ==========================================================

def _inspect_regions(
    regions,
    page_width,
    page_height
):

    page_area = page_width * page_height

    inspected = []

    for idx, region in enumerate(regions, start=1):

        x1, y1, x2, y2 = region["bbox"]

        width = x2 - x1
        height = y2 - y1

        coverage = round(
            region["area"] / page_area,
            4
        )

        inspected.append({

            "id": idx,

            "geometry": {

                "bbox": region["bbox"],

                "width": width,

                "height": height,

                "area": region["area"],

                "coverage": coverage

            },

            "analysis": {

                "touches_left": x1 <= 0,

                "touches_top": y1 <= 0,

                "touches_right": x2 >= page_width,

                "touches_bottom": y2 >= page_height,

                "aspect_ratio": round(
                    width / max(height, 1),
                    3
                ),

                "is_large_region": coverage > 0.60

            },

            "debug": {

                "preview": region["preview"]

            }

        })

    return inspected

def _merge_regions(
    regions,
    page_width,
    page_height
):
    """
    Temporary implementation.

    Returns regions unchanged.

    Future versions will:
        - merge overlapping regions
        - split oversized regions
        - remove duplicate detections
        - normalize ordering
    """
    return regions

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

# ==========================================================
# Encode Image
# ==========================================================

def _encode_image(image):

    success, buffer = cv2.imencode(
        ".png",
        image
    )

    if not success:
        return None

    return (
        "data:image/png;base64,"
        + base64.b64encode(buffer).decode("utf-8")
    )

# ==========================================================
# Stage 5
# Analyze Regions
# ==========================================================

def _analyze_regions(
    regions,
    page_width,
    page_height
):

    page_area = page_width * page_height

    analyzed = []

    refinement_required = False

    for idx, region in enumerate(regions, start=1):

        coverage = round(
            region["area"] / page_area,
            4
        )

        needs_refinement = coverage > 0.60

        if needs_refinement:
            refinement_required = True

        analyzed.append({

            "id": idx,

            "bbox": region["bbox"],

            "area": region["area"],

            "coverage": coverage,

            "needs_refinement": needs_refinement

        })

    return analyzed, refinement_required

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

    blurred = cv2.GaussianBlur(
        gray,
        (5, 5),
        0
    )

    edges = cv2.Canny(
        blurred,
        50,
        150
    )

    kernel = np.ones((5, 5), np.uint8)

    edges = cv2.dilate(
        edges,
        kernel,
        iterations=2
    )

    contours, _ = cv2.findContours(
        edges,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    regions = []

    for contour in contours:

        x, y, w, h = cv2.boundingRect(contour)

        area = w * h

        if area < 5000:
            continue

        regions.append({

            "bbox": [x, y, x + w, y + h],

            "area": area

        })

    regions.sort(
        key=lambda r: r["area"],
        reverse=True
    )

    return regions

# ==========================================================
# Region Crop Generator
# ==========================================================

def _generate_region_previews(
    image,
    regions
):

    updated_regions = []

    for region in regions:

        x1, y1, x2, y2 = region["bbox"]

        crop = image[
            y1:y2,
            x1:x2
        ]

        preview = _encode_image(crop)

        updated = dict(region)

        updated["preview"] = preview

        updated_regions.append(updated)

    return updated_regions



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

        raw_regions = _discover_regions(image)

        overlay = _draw_region_overlay(
            image,
            raw_regions
        )

        preview_regions = _generate_region_previews(
            image,
            raw_regions
        )

        inspected_regions = _inspect_regions(
            preview_regions,
            pix.width,
            pix.height
        )

        pipeline.pipeline["regions"]["count"] = len(inspected_regions)

        pipeline.pipeline["regions"]["items"] = inspected_regions

        overlay_filename = os.path.join(
            DEBUG_FOLDER,
            f"page_{page_index+1:03d}_overlay.png"
        )

        overlay_preview = _encode_image(
            overlay
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

            "overlay": {

                "preview": overlay_preview

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