import logging
import math


_logger = logging.getLogger(__name__)


# ==========================================================
# BASIC GEOMETRY
# ==========================================================

def _center(bbox):
    if not bbox:
        return None

    return (
        (bbox["left"] + bbox["right"]) / 2,
        (bbox["top"] + bbox["bottom"]) / 2,
    )


def _width(bbox):
    if not bbox:
        return 0

    return max(
        0,
        bbox["right"] - bbox["left"]
    )


def _height(bbox):
    if not bbox:
        return 0

    return max(
        0,
        bbox["bottom"] - bbox["top"]
    )


def _horizontal_overlap(a, b):
    if not a or not b:
        return 0

    left = max(
        a["left"],
        b["left"]
    )

    right = min(
        a["right"],
        b["right"]
    )

    return max(
        0,
        right - left
    )


def _vertical_overlap(a, b):
    if not a or not b:
        return 0

    top = max(
        a["top"],
        b["top"]
    )

    bottom = min(
        a["bottom"],
        b["bottom"]
    )

    return max(
        0,
        bottom - top
    )


def _distance_between_boxes(a, b):
    """
    Minimum geometric distance between two rectangles.
    """

    if not a or not b:
        return float("inf")

    dx = max(
        a["left"] - b["right"],
        b["left"] - a["right"],
        0,
    )

    dy = max(
        a["top"] - b["bottom"],
        b["top"] - a["bottom"],
        0,
    )

    return math.sqrt(
        (dx * dx) +
        (dy * dy)
    )


# ==========================================================
# TEXT NORMALIZATION
# ==========================================================

def _clean_text(value):
    if not value:
        return ""

    return " ".join(
        str(value).split()
    ).strip()


def _looks_like_product_text(text):
    """
    Lightweight heuristic only.

    This does NOT decide whether something is a product.
    It simply gives stronger weight to lines that often
    contain product information.
    """

    if not text:
        return False

    lowered = text.lower()

    product_keywords = [

        "stock",
        "pcs",
        "piece",
        "pieces",

        "size",
        "capacity",
        "colour",
        "color",

        "model",
        "code",
        "sku",

        "mm",
        "cm",
        "kg",
        "ml",

    ]

    return any(
        keyword in lowered
        for keyword in product_keywords
    )


# ==========================================================
# FIGURE → TEXT ASSOCIATION
# ==========================================================

def _score_text_for_figure(
    figure_bbox,
    text_bbox,
    text,
):
    """
    Calculate how strongly a text line is associated
    spatially with a figure.

    This is deliberately deterministic.

    OpenAI will NOT be used here yet.
    """

    if not figure_bbox or not text_bbox:
        return 0.0

    distance = _distance_between_boxes(
        figure_bbox,
        text_bbox
    )

    figure_w = max(
        _width(figure_bbox),
        0.001
    )

    figure_h = max(
        _height(figure_bbox),
        0.001
    )

    # Normalize distance relative to figure size.
    normalized_distance = (
        distance /
        max(
            figure_w,
            figure_h,
            0.001
        )
    )

    score = 1.0 / (
        1.0 +
        normalized_distance
    )

    # ------------------------------------------------------
    # Alignment bonuses
    # ------------------------------------------------------

    horizontal_overlap = (
        _horizontal_overlap(
            figure_bbox,
            text_bbox
        )
    )

    vertical_overlap = (
        _vertical_overlap(
            figure_bbox,
            text_bbox
        )
    )

    if horizontal_overlap > 0:
        score += 0.30

    if vertical_overlap > 0:
        score += 0.15

    # ------------------------------------------------------
    # Product-information bonus
    # ------------------------------------------------------

    if _looks_like_product_text(
        text
    ):
        score += 0.20

    return round(
        score,
        6
    )


# ==========================================================
# BUILD PAGE TEXT INDEX
# ==========================================================

def _build_page_text_index(
    evidence
):
    """
    Convert Azure page lines into a simple searchable
    spatial text index.
    """

    pages = {}

    for page in evidence.get(
        "pages",
        []
    ):

        page_number = page.get(
            "page_number"
        )

        lines = []

        for index, line in enumerate(
            page.get("lines", [])
        ):

            text = _clean_text(
                line.get("content")
            )

            bbox = line.get(
                "bbox"
            )

            if not text or not bbox:
                continue

            lines.append({

                "line_index":
                    index,

                "text":
                    text,

                "bbox":
                    bbox,
            })

        pages[page_number] = lines

    return pages


# ==========================================================
# FIND FIGURE PAGE
# ==========================================================

def _get_figure_page(
    figure
):
    regions = figure.get(
        "bounding_regions",
        []
    )

    if not regions:
        return None

    return regions[0].get(
        "page_number"
    )


# ==========================================================
# FIGURE EVIDENCE
# ==========================================================

def _build_figure_evidence(
    figure,
    page_lines,
):
    figure_id = figure.get(
        "figure_id"
    )

    regions = figure.get(
        "bounding_regions",
        []
    )

    if not regions:
        return {
            "figure_id":
                figure_id,

            "page_number":
                None,

            "bbox":
                None,

            "image_base64":
                figure.get(
                    "image_base64"
                ),

            "nearby_text":
                [],

            "best_text":
                None,
        }

    region = regions[0]

    page_number = region.get(
        "page_number"
    )

    figure_bbox = region.get(
        "bbox"
    )

    candidates = []

    for line in page_lines:

        text_bbox = line.get(
            "bbox"
        )

        text = line.get(
            "text",
            ""
        )

        score = _score_text_for_figure(
            figure_bbox,
            text_bbox,
            text,
        )

        if score <= 0:
            continue

        distance = _distance_between_boxes(
            figure_bbox,
            text_bbox
        )

        candidates.append({

            "text":
                text,

            "bbox":
                text_bbox,

            "distance":
                round(
                    distance,
                    4
                ),

            "score":
                score,

            "line_index":
                line.get(
                    "line_index"
                ),
        })

    # Highest score first.
    candidates.sort(
        key=lambda item:
            item["score"],
        reverse=True
    )

    # Keep a small evidence window.
    nearby_text = candidates[:12]

    best_text = (
        nearby_text[0]
        if nearby_text
        else None
    )

    return {

        "figure_id":
            figure_id,

        "page_number":
            page_number,

        "bbox":
            figure_bbox,

        "image_base64":
            figure.get(
                "image_base64"
            ),

        "nearby_text":
            nearby_text,

        "best_text":
            best_text,

        "caption":
            figure.get(
                "caption"
            ),

        "elements":
            figure.get(
                "elements",
                []
            ),
    }


# ==========================================================
# BUILD PRODUCT CANDIDATE GROUPS
# ==========================================================

def _build_candidate_groups(
    figure_evidence
):
    """
    Create preliminary spatial groups.

    IMPORTANT:
    These are NOT final products.

    They are evidence groups that will later be reviewed
    by the catalogue/product reasoning layer.
    """

    groups = []

    for item in figure_evidence:

        figure_id = item.get(
            "figure_id"
        )

        page_number = item.get(
            "page_number"
        )

        nearby_text = item.get(
            "nearby_text",
            []
        )

        if not nearby_text:
            groups.append({

                "group_id":
                    f"page_{page_number}_figure_{figure_id}",

                "page_number":
                    page_number,

                "figure_ids":
                    [figure_id],

                "text":
                    [],

                "confidence":
                    0.0,
            })

            continue

        # --------------------------------------------------
        # Take the strongest few text lines as evidence.
        # --------------------------------------------------

        selected_text = nearby_text[:6]

        text_values = [
            item["text"]
            for item in selected_text
            if item.get("text")
        ]

        scores = [
            item["score"]
            for item in selected_text
            if item.get("score")
        ]

        confidence = (
            max(scores)
            if scores
            else 0.0
        )

        groups.append({

            "group_id":
                (
                    f"page_{page_number}"
                    f"_figure_{figure_id}"
                ),

            "page_number":
                page_number,

            "figure_ids":
                [figure_id],

            "text":
                text_values,

            "confidence":
                round(
                    confidence,
                    6
                ),
        })

    return groups


# ==========================================================
# PUBLIC FUNCTION
# ==========================================================

def build_product_evidence(
    evidence
):
    """
    Convert raw Azure Layout evidence into a product-aware
    evidence structure.

    Azure is still responsible for:
        - OCR
        - figure detection
        - figure coordinates
        - figure images

    This layer is responsible for:
        - spatial relationship
        - nearby text
        - preliminary evidence grouping

    It does NOT create final Odoo products.
    """

    if not isinstance(
        evidence,
        dict
    ):
        raise ValueError(
            "Azure evidence must be a dictionary."
        )

    page_text_index = (
        _build_page_text_index(
            evidence
        )
    )

    figures = evidence.get(
        "figures",
        []
    )

    figure_evidence = []

    for figure in figures:

        page_number = (
            _get_figure_page(
                figure
            )
        )

        page_lines = (
            page_text_index.get(
                page_number,
                []
            )
        )

        item = _build_figure_evidence(
            figure,
            page_lines,
        )

        figure_evidence.append(
            item
        )

    candidate_groups = (
        _build_candidate_groups(
            figure_evidence
        )
    )

    result = {

        "model_id":
            evidence.get(
                "model_id"
            ),

        "operation_id":
            evidence.get(
                "operation_id"
            ),

        "page_count":
            len(
                evidence.get(
                    "pages",
                    []
                )
            ),

        "figure_count":
            len(
                figures
            ),

        "figures":
            figure_evidence,

        "candidate_groups":
            candidate_groups,
    }

    _logger.warning(
        "[AZURE EVIDENCE] "
        "pages=%s figures=%s groups=%s",

        result["page_count"],

        result["figure_count"],

        len(
            candidate_groups
        ),
    )

    return result