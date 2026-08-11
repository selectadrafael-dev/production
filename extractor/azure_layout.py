import os
import base64
import logging

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

    This is deliberately independent from the existing /extract
    pipeline.
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

    client = DocumentIntelligenceClient(
        endpoint=AZURE_ENDPOINT,
        credential=AzureKeyCredential(AZURE_KEY),
    )

    # Make sure we are reading from the beginning.
    try:
        file_stream.seek(0)
    except Exception:
        pass

    _logger.info(
        "[AZURE] Starting Layout analysis..."
    )

    poller = client.begin_analyze_document(
        "prebuilt-layout",
        body=file_stream,
        output=[AnalyzeOutputOption.FIGURES],
    )

    result = poller.result()

    operation_id = poller.details.get(
        "operation_id"
    )

    _logger.info(
        "[AZURE] Analysis complete. operation_id=%s",
        operation_id,
    )

    evidence = {
        "model_id": getattr(result, "model_id", None),
        "operation_id": operation_id,
        "content": getattr(result, "content", None),
        "pages": [],
        "figures": [],
        "paragraphs": [],
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

            if page.lines:

                for line in page.lines:

                    page_data["lines"].append({
                        "content": line.content,
                        "polygon": (
                            list(line.polygon)
                            if line.polygon
                            else []
                        ),
                        "bbox": _polygon_to_bbox(
                            list(line.polygon)
                            if line.polygon
                            else None
                        ),
                        "spans": _serialize_spans(
                            line.spans
                        ),
                    })

            if page.words:

                for word in page.words:

                    page_data["words"].append({
                        "content": word.content,
                        "confidence": word.confidence,
                        "polygon": (
                            list(word.polygon)
                            if word.polygon
                            else []
                        ),
                        "bbox": _polygon_to_bbox(
                            list(word.polygon)
                            if word.polygon
                            else None
                        ),
                        "span": {
                            "offset": (
                                word.span.offset
                                if word.span
                                else None
                            ),
                            "length": (
                                word.span.length
                                if word.span
                                else None
                            ),
                        },
                    })

            evidence["pages"].append(page_data)

    # ==========================================================
    # PARAGRAPHS
    # ==========================================================

    if result.paragraphs:

        for paragraph in result.paragraphs:

            evidence["paragraphs"].append({
                "content": paragraph.content,
                "role": getattr(
                    paragraph,
                    "role",
                    None,
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
            len(result.figures),
        )

        for figure in result.figures:

            figure_id = figure.id

            figure_data = {
                "figure_id": figure_id,
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
                "caption": None,
                "image_base64": None,
            }

            # --------------------------------------------------
            # CAPTION
            # --------------------------------------------------

            if figure.caption:

                figure_data["caption"] = {
                    "content": figure.caption.content,
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
                        len(image_bytes),
                    )

                except Exception:

                    _logger.exception(
                        "[AZURE] Failed retrieving figure %s",
                        figure_id,
                    )

            evidence["figures"].append(
                figure_data
            )

    return _json_safe(evidence)