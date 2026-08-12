import os
import base64
import logging
import fitz

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeOutputOption


_logger = logging.getLogger(__name__)


AZURE_ENDPOINT = os.environ.get(
    "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"
)

AZURE_KEY = os.environ.get(
    "AZURE_DOCUMENT_INTELLIGENCE_KEY"
)


def _polygon_to_bbox(polygon):
    """
    Convert Azure polygon coordinates into a simple bounding box.

    Azure polygons are returned as:
    [x1, y1, x2, y2, x3, y3, x4, y4]
    """

    if not polygon:
        return None

    xs = polygon[0::2]
    ys = polygon[1::2]

    if not xs or not ys:
        return None

    return {
        "left": min(xs),
        "top": min(ys),
        "right": max(xs),
        "bottom": max(ys),
    }


def _serialize_bounding_regions(regions):
    """
    Convert Azure bounding regions into JSON-safe dictionaries.
    """

    output = []

    if not regions:
        return output

    for region in regions:

        output.append({
            "page_number": getattr(region, "page_number", None),
            "polygon": list(region.polygon) if region.polygon else [],
            "bbox": _polygon_to_bbox(
                list(region.polygon)
                if region.polygon
                else None
            ),
        })

    return output


def _serialize_spans(spans):
    """
    Convert Azure document spans into JSON-safe dictionaries.
    """

    output = []

    if not spans:
        return output

    for span in spans:

        output.append({
            "offset": getattr(span, "offset", None),
            "length": getattr(span, "length", None),
        })

    return output


def _serialize_elements(elements):
    """
    Preserve Azure element references such as:

        /paragraphs/15
        /tables/2
    """

    if not elements:
        return []

    return list(elements)


def _json_safe(value):
    """
    Convert unexpected SDK/Python objects into JSON-safe values.

    This is a safety layer for the diagnostic endpoint.
    It prevents Flask jsonify() from receiving objects such
    as FileStorage, enums, or SDK model instances.
    """

    if value is None:
        return None

    if isinstance(value, (
        str,
        int,
        float,
        bool
    )):
        return value

    if isinstance(value, dict):

        return {
            str(key): _json_safe(val)
            for key, val in value.items()
        }

    if isinstance(value, (list, tuple)):

        return [
            _json_safe(item)
            for item in value
        ]

    # Handle objects that expose a dictionary
    # representation.
    if hasattr(value, "as_dict"):

        try:
            return _json_safe(
                value.as_dict()
            )
        except Exception:
            pass

    # Final diagnostic fallback.
    return str(value)

def analyze_pdf(file_stream):
    """
    Analyze a PDF using Azure Document Intelligence Layout.

    The incoming Flask FileStorage object is immediately converted
    to raw PDF bytes so that no Flask request object can leak into
    the Azure result or JSON response.
    """

    if not AZURE_ENDPOINT:
        raise RuntimeError(
            "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT "
            "is not configured."
        )

    if not AZURE_KEY:
        raise RuntimeError(
            "AZURE_DOCUMENT_INTELLIGENCE_KEY "
            "is not configured."
        )

    # ==========================================================
    # CONVERT UPLOADED FILE TO RAW BYTES
    # ==========================================================

    try:
        file_stream.seek(0)
    except Exception:
        pass

    pdf_bytes = file_stream.read()

    if not pdf_bytes:
        raise RuntimeError(
            "Uploaded PDF is empty."
        )

    _logger.info(
        "[AZURE] PDF bytes received: %s",
        len(pdf_bytes)
    )

    original_page_images = (
        _extract_original_page_images(
            pdf_bytes
        )
    )

    # ==========================================================
    # AZURE CLIENT
    # ==========================================================

    client = DocumentIntelligenceClient(
        endpoint=AZURE_ENDPOINT,
        credential=AzureKeyCredential(AZURE_KEY),
    )

    _logger.info(
        "[AZURE] Starting Layout analysis..."
    )

    poller = client.begin_analyze_document(
        "prebuilt-layout",
        body=pdf_bytes,
        output=[AnalyzeOutputOption.FIGURES],
    )

    result = poller.result()

    operation_id = poller.details.get(
        "operation_id"
    )

    _logger.info(
        "[AZURE] Analysis complete. operation_id=%s",
        operation_id
    )

    # ==========================================================
    # BASE EVIDENCE
    # ==========================================================

    evidence = {
        "model_id": getattr(
            result,
            "model_id",
            None
        ),

        "operation_id": operation_id,

        "content": getattr(
            result,
            "content",
            None
        ),

        "pages": [],

        "figures": [],

        "paragraphs": [],

        "original_page_images":
            original_page_images,
    }

    # ==========================================================
    # PAGES
    # ==========================================================

    if result.pages:

        for page in result.pages:

            page_data = {
                "page_number": page.page_number,

                "width": page.width,

                "height": page.height,

                "unit": page.unit,

                "lines": [],

                "words": [],
            }

            # --------------------------------------------------
            # LINES
            # --------------------------------------------------

            if page.lines:

                for line in page.lines:

                    polygon = (
                        list(line.polygon)
                        if line.polygon
                        else []
                    )

                    page_data["lines"].append({

                        "content":
                            line.content,

                        "polygon":
                            polygon,

                        "bbox":
                            _polygon_to_bbox(
                                polygon
                            ),

                        "spans":
                            _serialize_spans(
                                line.spans
                            ),
                    })

            # --------------------------------------------------
            # WORDS
            # --------------------------------------------------

            if page.words:

                for word in page.words:

                    polygon = (
                        list(word.polygon)
                        if word.polygon
                        else []
                    )

                    page_data["words"].append({

                        "content":
                            word.content,

                        "confidence":
                            word.confidence,

                        "polygon":
                            polygon,

                        "bbox":
                            _polygon_to_bbox(
                                polygon
                            ),

                        "span": {

                            "offset":
                                (
                                    word.span.offset
                                    if word.span
                                    else None
                                ),

                            "length":
                                (
                                    word.span.length
                                    if word.span
                                    else None
                                ),
                        },
                    })

            evidence["pages"].append(
                page_data
            )

    # ==========================================================
    # PARAGRAPHS
    # ==========================================================

    if result.paragraphs:

        for paragraph in result.paragraphs:

            evidence["paragraphs"].append({

                "content":
                    paragraph.content,

                "role":
                    getattr(
                        paragraph,
                        "role",
                        None
                    ),

                "bounding_regions":
                    _serialize_bounding_regions(
                        paragraph.bounding_regions
                    ),

                "spans":
                    _serialize_spans(
                        paragraph.spans
                    ),
            })

    # ==========================================================
    # FIGURES
    # ==========================================================

    if result.figures:

        _logger.info(
            "[AZURE] Figures detected: %s",
            len(result.figures)
        )

        for figure in result.figures:

            figure_id = figure.id

            figure_data = {

                "figure_id":
                    figure_id,

                "bounding_regions":
                    _serialize_bounding_regions(
                        figure.bounding_regions
                    ),

                "spans":
                    _serialize_spans(
                        figure.spans
                    ),

                "elements":
                    _serialize_elements(
                        figure.elements
                    ),

                "caption":
                    None,

                "image_base64":
                    None,
            }

            # --------------------------------------------------
            # CAPTION
            # --------------------------------------------------

            if figure.caption:

                figure_data["caption"] = {

                    "content":
                        figure.caption.content,

                    "bounding_regions":
                        _serialize_bounding_regions(
                            figure.caption.bounding_regions
                        ),

                    "spans":
                        _serialize_spans(
                            figure.caption.spans
                        ),

                    "elements":
                        _serialize_elements(
                            figure.caption.elements
                        ),
                }

            # --------------------------------------------------
            # CROPPED FIGURE IMAGE
            # --------------------------------------------------

            if figure_id and operation_id:

                try:

                    response = (
                        client.get_analyze_result_figure(
                            model_id=result.model_id,
                            result_id=operation_id,
                            figure_id=figure_id,
                        )
                    )

                    image_bytes = b"".join(
                        response
                    )

                    figure_data[
                        "image_base64"
                    ] = base64.b64encode(
                        image_bytes
                    ).decode("utf-8")

                    _logger.info(
                        "[AZURE] Retrieved figure %s (%s bytes)",
                        figure_id,
                        len(image_bytes)
                    )

                except Exception:

                    _logger.exception(
                        "[AZURE] Failed retrieving figure %s",
                        figure_id
                    )

            evidence["figures"].append(
                figure_data
            )

    return evidence

def _extract_original_page_images(pdf_bytes):
    """
    Render every original PDF page to PNG.

    These are complete catalogue page images, not Azure
    figure crops. They are preserved so the OpenAI visual
    mapper can understand the complete page layout.
    """

    document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    pages = []

    try:

        for page_index in range(
            len(document)
        ):

            page = document[
                page_index
            ]

            # 2x rendering gives OpenAI a reasonably
            # detailed page image without unnecessarily
            # producing huge images.
            matrix = fitz.Matrix(
                2,
                2
            )

            pixmap = page.get_pixmap(
                matrix=matrix,
                alpha=False
            )

            image_bytes = (
                pixmap.tobytes(
                    "png"
                )
            )

            pages.append({

                "page_number":
                    page_index + 1,

                "image_base64":
                    base64.b64encode(
                        image_bytes
                    ).decode(
                        "utf-8"
                    ),

                "mime_type":
                    "image/png",

                "width":
                    pixmap.width,

                "height":
                    pixmap.height,

            })

    finally:

        document.close()

    return pages


# ============================================================
# ODOO AZURE EVIDENCE NORMALIZER
# ============================================================

def build_azure_evidence_package(evidence):
    """
    Convert the raw Azure evidence into a compact,
    Odoo/OpenAI-friendly catalogue evidence package.

    IMPORTANT:
    - The original page image is preserved.
    - Azure figure images are preserved.
    - Figure coordinates are preserved.
    - Raw Azure internals such as words/spans/elements
      are not sent to the Odoo/OpenAI layer.
    """

    pages = []

    original_page_images = (
        evidence.get(
            "original_page_images",
            []
        )
    )

    raw_pages = (
        evidence.get(
            "pages",
            []
        )
    )

    figures = (
        evidence.get(
            "figures",
            []
        )
    )

    paragraphs = (
        evidence.get(
            "paragraphs",
            []
        )
    )

    # ========================================================
    # BUILD PAGE-LEVEL EVIDENCE
    # ========================================================

    for raw_page in raw_pages:

        page_number = raw_page.get(
            "page_number"
        )

        page_image = None

        # ----------------------------------------------------
        # Find corresponding original page image
        # ----------------------------------------------------

        for original_page in original_page_images:

            if (
                original_page.get(
                    "page_number"
                )
                == page_number
            ):

                page_image = (
                    original_page.get(
                        "image_base64"
                    )
                )

                break

        # ----------------------------------------------------
        # Page OCR
        # ----------------------------------------------------

        page_lines = []

        for line in (
            raw_page.get(
                "lines",
                []
            )
        ):

            content = line.get(
                "content"
            )

            if not content:
                continue

            page_lines.append({

                "text": content,

                "bbox": line.get(
                    "bbox"
                )

            })

        # ----------------------------------------------------
        # Figures belonging to this page
        # ----------------------------------------------------

        page_figures = []

        for figure in figures:

            figure_regions = (
                figure.get(
                    "bounding_regions",
                    []
                )
            )

            figure_page = None

            if figure_regions:

                figure_page = (
                    figure_regions[0]
                    .get("page_number")
                )

            if figure_page != page_number:
                continue

            figure_bbox = None

            if figure_regions:

                figure_bbox = (
                    figure_regions[0]
                    .get("bbox")
                )

            caption = (
                figure.get(
                    "caption"
                )
            )

            caption_text = []

            if caption:

                caption_content = (
                    caption.get(
                        "content"
                    )
                )

                if caption_content:

                    caption_text.append(
                        caption_content
                    )

            page_figures.append({

                "figure_id":
                    figure.get(
                        "figure_id"
                    ),

                "bbox":
                    figure_bbox,

                "image_base64":
                    figure.get(
                        "image_base64"
                    ),

                "caption":
                    caption_text

            })

        pages.append({

            "page_number":
                page_number,

            "page_width":
                raw_page.get(
                    "width"
                ),

            "page_height":
                raw_page.get(
                    "height"
                ),

            "page_unit":
                raw_page.get(
                    "unit"
                ),

            # ------------------------------------------------
            # ORIGINAL CATALOGUE PAGE
            # ------------------------------------------------

            "page_image":
                page_image,

            # ------------------------------------------------
            # OCR
            # ------------------------------------------------

            "ocr":
                page_lines,

            # ------------------------------------------------
            # AZURE FIGURES
            # ------------------------------------------------

            "figures":
                page_figures

        })

    # ========================================================
    # FINAL PACKAGE
    # ========================================================

    return {

        "model_id":
            evidence.get(
                "model_id"
            ),

        "operation_id":
            evidence.get(
                "operation_id"
            ),

        "pages":
            pages

    }

# ============================================================
# AZURE → FAMILY A COORDINATE CONVERSION
# ============================================================

def _azure_bbox_to_page_pixels(
    bbox,
    azure_page_width,
    azure_page_height,
    rendered_page_width,
    rendered_page_height,
):
    """
    Convert Azure page coordinates into pixel coordinates
    of the original rendered page image.

    We deliberately use the actual page dimensions rather
    than a hard-coded DPI value.
    """

    if not bbox:
        return {
            "x": 0,
            "y": 0,
            "width": 0,
            "height": 0,
        }

    try:

        left = float(
            bbox.get("left", 0)
        )

        top = float(
            bbox.get("top", 0)
        )

        right = float(
            bbox.get("right", 0)
        )

        bottom = float(
            bbox.get("bottom", 0)
        )

        if (
            not azure_page_width
            or not azure_page_height
            or not rendered_page_width
            or not rendered_page_height
        ):
            return {
                "x": 0,
                "y": 0,
                "width": 0,
                "height": 0,
            }

        scale_x = (
            rendered_page_width
            / float(azure_page_width)
        )

        scale_y = (
            rendered_page_height
            / float(azure_page_height)
        )

        x = int(
            round(left * scale_x)
        )

        y = int(
            round(top * scale_y)
        )

        width = int(
            round(
                (right - left)
                * scale_x
            )
        )

        height = int(
            round(
                (bottom - top)
                * scale_y
            )
        )

        # ----------------------------------------------------
        # Clamp to actual page boundaries
        # ----------------------------------------------------

        x = max(
            0,
            min(
                x,
                rendered_page_width
            )
        )

        y = max(
            0,
            min(
                y,
                rendered_page_height
            )
        )

        width = max(
            0,
            min(
                width,
                rendered_page_width - x
            )
        )

        height = max(
            0,
            min(
                height,
                rendered_page_height - y
            )
        )

        return {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
        }

    except Exception:

        _logger.exception(
            "[AZURE] Failed converting bbox to pixels"
        )

        return {
            "x": 0,
            "y": 0,
            "width": 0,
            "height": 0,
        }


# ============================================================
# AZURE EVIDENCE → FAMILY A COMPATIBLE STRUCTURE
# ============================================================

def build_family_a_compatible_azure_package(
    evidence
):
    """
    Convert Azure evidence into the structural contract
    expected by the existing Family A production pipeline.

    Azure remains the extraction source.

    Family A remains the downstream production contract.

    No existing Family A production method is modified here.
    """

    pages = []

    raw_pages = evidence.get(
        "pages",
        []
    )

    raw_figures = evidence.get(
        "figures",
        []
    )

    original_page_images = evidence.get(
        "original_page_images",
        []
    )

    # ========================================================
    # PAGE LOOP FIRST
    # ========================================================

    for raw_page in raw_pages:

        page_number = raw_page.get(
            "page_number"
        )

        azure_width = raw_page.get(
            "width",
            0
        )

        azure_height = raw_page.get(
            "height",
            0
        )

        azure_unit = raw_page.get(
            "unit"
        )

        # ----------------------------------------------------
        # Find original rendered page
        # ----------------------------------------------------

        original_page = None

        for item in original_page_images:

            if (
                item.get("page_number")
                == page_number
            ):

                original_page = item

                break

        page_image = (
            original_page.get(
                "image_base64"
            )
            if original_page
            else None
        )

        rendered_width = (
            original_page.get(
                "width",
                0
            )
            if original_page
            else 0
        )

        rendered_height = (
            original_page.get(
                "height",
                0
            )
            if original_page
            else 0
        )

        # ====================================================
        # PAGE TEXT
        # ====================================================

        text_lines = []

        for line in raw_page.get(
            "lines",
            []
        ):

            content = line.get(
                "content"
            )

            if content:
                text_lines.append(
                    content
                )

        page_text = "\n".join(
            text_lines
        )

        # ====================================================
        # FIGURES BELONGING TO THIS PAGE
        # ====================================================

        page_figures = []

        for figure in raw_figures:

            regions = figure.get(
                "bounding_regions",
                []
            )

            for region in regions:

                if (
                    region.get(
                        "page_number"
                    )
                    == page_number
                ):

                    page_figures.append(
                        figure
                    )

                    break

        # ====================================================
        # FAMILY A IMAGES
        # ====================================================

        family_a_images = []

        for rank, figure in enumerate(
            page_figures
        ):

            image_base64 = figure.get(
                "image_base64"
            )

            if not image_base64:
                continue

            regions = figure.get(
                "bounding_regions",
                []
            )

            if not regions:
                continue

            region = regions[0]

            bbox = region.get(
                "bbox",
                {}
            )

            pixel_bbox = (
                _azure_bbox_to_page_pixels(
                    bbox=bbox,

                    azure_page_width=
                        azure_width,

                    azure_page_height=
                        azure_height,

                    rendered_page_width=
                        rendered_width,

                    rendered_page_height=
                        rendered_height,
                )
            )

            x = pixel_bbox["x"]
            y = pixel_bbox["y"]
            width = pixel_bbox["width"]
            height = pixel_bbox["height"]

            crop_area = (
                width * height
            )

            portrait = (
                height > width
                if width and height
                else False
            )

            large_image = (
                width >= 300
                and height >= 300
            )

            large_area = (
                crop_area >= 120000
            )

            # ------------------------------------------------
            # IMPORTANT
            #
            # Azure does NOT decide lifestyle/product status.
            # OpenAI will make the semantic decision later.
            # ------------------------------------------------

            image_item = {

                # ============================================
                # FAMILY A CORE FIELDS
                # ============================================

                "image":
                    image_base64,

                "score":
                    0,

                "x":
                    x,

                "y":
                    y,

                "extractor_rank":
                    rank,

                "extractor_score":
                    0,

                "width":
                    width,

                "height":
                    height,

                "is_lifestyle":
                    False,

                "lifestyle_score":
                    0,

                "large_image":
                    large_image,

                "portrait":
                    portrait,

                "large_area":
                    large_area,

                "crop_area":
                    crop_area,

                # ============================================
                # AZURE IDENTIFICATION
                # ============================================

                "azure_figure_id":
                    figure.get(
                        "figure_id"
                    ),

                "azure_bbox":
                    bbox,

                "azure_page_number":
                    page_number,

                "azure_unit":
                    azure_unit,

                "azure_caption":
                    figure.get(
                        "caption"
                    ),

            }

            family_a_images.append(
                image_item
            )

        # ====================================================
        # FAMILY A PAGE OBJECT
        # ====================================================

        page_data = {

            "page":
                page_number,

            "text":
                page_text,

            "page_image":
                page_image,

            "page_image_size":
                len(page_image)
                if page_image
                else 0,

            "page_width":
                rendered_width,

            "page_height":
                rendered_height,

            "images":
                family_a_images,

            # =================================================
            # AZURE EVIDENCE EXTENSION
            # =================================================

            "azure_evidence": {

                "page_number":
                    page_number,

                "azure_width":
                    azure_width,

                "azure_height":
                    azure_height,

                "azure_unit":
                    azure_unit,

                "figure_ids": [

                    figure.get(
                        "figure_id"
                    )

                    for figure
                    in page_figures

                ],

                "ocr_lines": [

                    {
                        "text":
                            line.get(
                                "content"
                            ),

                        "bbox":
                            line.get(
                                "bbox"
                            ),

                        "polygon":
                            line.get(
                                "polygon"
                            ),

                    }

                    for line
                    in raw_page.get(
                        "lines",
                        []
                    )

                    if line.get(
                        "content"
                    )

                ],

            },

        }

        pages.append(
            page_data
        )

    # ========================================================
    # FINAL FAMILY-A COMPATIBLE PACKAGE
    # ========================================================

    return {

        "pages":
            pages,

        "azure_evidence": {

            "model_id":
                evidence.get(
                    "model_id"
                ),

            "operation_id":
                evidence.get(
                    "operation_id"
                ),

            "figure_count":
                len(raw_figures),

            "original_page_count":
                len(
                    original_page_images
                ),

        },

    }