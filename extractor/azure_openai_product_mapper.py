import base64
import json
import logging
import os

from openai import OpenAI


_logger = logging.getLogger(__name__)


# ==========================================================
# OPENAI CLIENT
# ==========================================================

def _get_client():
    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured."
        )

    return OpenAI(
        api_key=api_key
    )


# ==========================================================
# IMAGE DATA URL
# ==========================================================

def _image_data_url(
    image_base64,
    mime_type="image/png"
):
    if not image_base64:
        return None

    # Azure normally gives us base64 without
    # the data:image/... prefix.
    if image_base64.startswith(
        "data:image/"
    ):
        return image_base64

    return (
        f"data:{mime_type};base64,"
        f"{image_base64}"
    )


# ==========================================================
# BUILD FIGURE MANIFEST
# ==========================================================

def _build_figure_manifest(
    evidence
):
    manifest = []

    for figure in evidence.get(
        "figures",
        []
    ):

        regions = figure.get(
            "bounding_regions",
            []
        )

        region = (
            regions[0]
            if regions
            else {}
        )

        manifest.append({

            "figure_id":
                figure.get(
                    "figure_id"
                ),

            "page_number":
                region.get(
                    "page_number"
                ),

            "bbox":
                region.get(
                    "bbox"
                ),

            "caption":
                figure.get(
                    "caption"
                ),

            "elements":
                figure.get(
                    "elements",
                    []
                ),

        })

    return manifest


# ==========================================================
# BUILD OCR MANIFEST
# ==========================================================

def _build_ocr_manifest(
    evidence
):
    pages = []

    for page in evidence.get(
        "pages",
        []
    ):

        page_number = page.get(
            "page_number"
        )

        lines = []

        for index, line in enumerate(
            page.get(
                "lines",
                []
            )
        ):

            text = (
                line.get(
                    "content"
                )
                or ""
            ).strip()

            if not text:
                continue

            lines.append({

                "line_index":
                    index,

                "text":
                    text,

                "bbox":
                    line.get(
                        "bbox"
                    ),

            })

        pages.append({

            "page_number":
                page_number,

            "lines":
                lines,

        })

    return pages


# ==========================================================
# PROMPT
# ==========================================================

def _build_system_prompt():

    return """
You are a catalogue product-association specialist.

Your task is NOT simply to identify images.

You must determine which visual figures belong to
which actual products on a catalogue page.

IMPORTANT RULES:

1. One figure does NOT necessarily equal one product.

2. One product may contain multiple figures.

3. A small figure may be:
   - a detail image
   - alternate view
   - colour/detail image
   - accessory image
   - secondary product image

4. Do NOT assign text to a figure merely because
   the text is geographically nearby.

5. Use the COMPLETE ORIGINAL PAGE IMAGE as the
   primary visual context.

6. Use Azure figure IDs and bounding boxes as
   precise evidence.

7. Use OCR text and its coordinates as supporting
   evidence.

8. Determine product boundaries from the complete
   visual layout.

9. Keep different products separate even when their
   images are close together.

10. If multiple images clearly represent the same
    product, place them in the same product group.

11. If an image is ambiguous, do NOT invent a
    product. Mark it as ambiguous or secondary.

12. Preserve every Azure figure ID. Never silently
    discard an image.

13. Preserve the original OCR text. Do not invent
    specifications, stock quantities, dimensions,
    colours, or product names.

14. Your output must be valid JSON matching the
    requested structure.

Your objective is to produce reliable product-to-image
association evidence for a downstream catalogue
importer.
"""


# ==========================================================
# USER PROMPT
# ==========================================================

def _build_user_prompt(
    evidence
):

    figure_manifest = (
        _build_figure_manifest(
            evidence
        )
    )

    ocr_manifest = (
        _build_ocr_manifest(
            evidence
        )
    )

    return f"""
Analyze this catalogue page.

Azure detected these figures:

{json.dumps(
    figure_manifest,
    indent=2,
    ensure_ascii=False
)}

Azure extracted this OCR evidence:

{json.dumps(
    ocr_manifest,
    indent=2,
    ensure_ascii=False
)}

Determine:

A. How many actual products are present?

B. Which figure IDs belong to each product?

C. Which figure is the primary product image?

D. Which figures are secondary/detail images?

E. Which OCR text belongs to each product?

F. Which figures are ambiguous or should not be
   treated as independent products?

Return ONLY JSON in this structure:

{{
  "products": [
    {{
      "product_id": "product_1",
      "product_name": "",
      "figure_ids": [],
      "primary_figure_id": "",
      "secondary_figure_ids": [],
      "ocr_text": [],
      "confidence": 0.0,
      "reason": ""
    }}
  ],
  "unassigned_figures": [],
  "notes": []
}}

Do not create information that is not supported by
the page, figures, or OCR.
"""


# ==========================================================
# VALIDATE RESPONSE
# ==========================================================

def _validate_result(
    result,
    known_figure_ids
):

    if not isinstance(
        result,
        dict
    ):
        raise ValueError(
            "OpenAI returned a non-object result."
        )

    products = result.get(
        "products"
    )

    if not isinstance(
        products,
        list
    ):
        raise ValueError(
            "OpenAI result does not contain "
            "a valid products list."
        )

    assigned_ids = []

    for product in products:

        figure_ids = product.get(
            "figure_ids",
            []
        )

        if not isinstance(
            figure_ids,
            list
        ):
            raise ValueError(
                "figure_ids must be a list."
            )

        for figure_id in figure_ids:

            figure_id = str(
                figure_id
            )

            if figure_id not in known_figure_ids:

                raise ValueError(
                    "OpenAI referenced unknown "
                    f"figure_id: {figure_id}"
                )

            assigned_ids.append(
                figure_id
            )

    duplicates = {

        figure_id

        for figure_id in assigned_ids

        if assigned_ids.count(
            figure_id
        ) > 1
    }

    if duplicates:

        raise ValueError(
            "A figure was assigned to multiple "
            "products: "
            f"{sorted(duplicates)}"
        )

    return result


# ==========================================================
# MAIN PUBLIC FUNCTION
# ==========================================================

def map_products_with_openai(
    evidence,
    page_images=None,
    model=None
):

    """
    Send one catalogue page plus Azure evidence
    to OpenAI for semantic product grouping.

    page_images:
        Optional list of base64 page images.

    evidence:
        Output returned by analyze_pdf().
    """

    if not isinstance(
        evidence,
        dict
    ):
        raise ValueError(
            "evidence must be a dictionary."
        )

    client = _get_client()

    model = (
        model
        or os.environ.get(
            "OPENAI_VISION_MODEL",
            "gpt-4.1-mini"
        )
    )

    figure_manifest = (
        _build_figure_manifest(
            evidence
        )
    )

    known_figure_ids = {

        str(
            item["figure_id"]
        )

        for item
        in figure_manifest

        if item.get(
            "figure_id"
        )
    }

    content = [

        {
            "type":
                "input_text",

            "text":
                _build_system_prompt()
                +
                "\n\n"
                +
                _build_user_prompt(
                    evidence
                ),
        }

    ]

    # ======================================================
    # ORIGINAL PAGE IMAGE(S)
    # ======================================================

    for page_image in (
        page_images or []
    ):

        image_url = _image_data_url(
            page_image
        )

        if image_url:

            content.append({

                "type":
                    "input_image",

                "image_url":
                    image_url,

            })

    # ======================================================
    # INDIVIDUAL AZURE FIGURES
    # ======================================================

    for figure in evidence.get(
        "figures",
        []
    ):

        figure_id = figure.get(
            "figure_id"
        )

        image_base64 = figure.get(
            "image_base64"
        )

        image_url = _image_data_url(
            image_base64
        )

        if not image_url:
            continue

        content.append({

            "type":
                "input_text",

            "text":
                (
                    "Azure FIGURE ID: "
                    f"{figure_id}"
                ),

        })

        content.append({

            "type":
                "input_image",

            "image_url":
                image_url,

        })

    _logger.warning(
        "[OPENAI PRODUCT MAPPER] "
        "Sending %s figures to model=%s",
        len(
            figure_manifest
        ),
        model
    )

    response = client.responses.create(

        model=model,

        input=[
            {
                "role":
                    "user",

                "content":
                    content,
            }
        ],

        text={
            "format": {
                "type":
                    "json_object"
            }
        }

    )

    raw_text = (
        response.output_text
        or ""
    ).strip()

    if not raw_text:

        raise RuntimeError(
            "OpenAI returned an empty response."
        )

    try:

        result = json.loads(
            raw_text
        )

    except json.JSONDecodeError as exc:

        _logger.error(
            "[OPENAI PRODUCT MAPPER] "
            "Invalid JSON: %s",
            raw_text
        )

        raise RuntimeError(
            "OpenAI returned invalid JSON."
        ) from exc

    result = _validate_result(
        result,
        known_figure_ids
    )

    return {

        "success":
            True,

        "model":
            model,

        "azure_figure_count":
            len(
                figure_manifest
            ),

        "mapping":
            result,

    }