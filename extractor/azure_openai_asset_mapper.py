import base64
import json
import logging
import os

from openai import OpenAI


_logger = logging.getLogger(__name__)


# ============================================================
# OPENAI CLIENT
# ============================================================

def _get_openai_client():

    api_key = os.environ.get(
        "OPENAI_API_KEY"
    )

    if not api_key:

        raise RuntimeError(
            "OPENAI_API_KEY is not configured."
        )

    return OpenAI(
        api_key=api_key
    )


# ============================================================
# IMAGE DATA URL
# ============================================================

def _image_data_url(
    image_base64,
    mime_type="image/png"
):

    if not image_base64:
        return None

    if image_base64.startswith(
        "data:image/"
    ):
        return image_base64

    return (
        f"data:{mime_type};base64,"
        f"{image_base64}"
    )


# ============================================================
# SYSTEM PROMPT
# ============================================================

def _build_asset_system_prompt():

    return """
You are the visual asset segmentation and product-relationship
engine for a product catalogue extraction system.

Your task is NOT simply to identify every object in an image.

A catalogue page may contain:

- multiple independent products
- multiple variants of one product
- multiple views of one product
- lifestyle photographs
- marketing accessories
- props
- bundled products
- decorative objects
- several products intentionally photographed together
- one Azure figure containing multiple commercial products

IMPORTANT:

An Azure figure is NOT automatically one product.

An object inside an Azure figure is NOT automatically a
separate product.

You must reason using:

1. The complete original catalogue page.
2. Azure figure boundaries.
3. Azure OCR text.
4. Product mapping supplied by the previous AI stage.
5. Visual appearance.
6. Product names, SKUs and catalogue numbering.
7. Spatial relationships.
8. Variant relationships.
9. Whether an image is a primary product image, secondary
   product image, lifestyle image, prop, accessory or
   unrelated object.

============================================================
COMMERCIAL PRODUCT RULE
============================================================

If two visually separate objects have separate catalogue
names/SKUs/numbers, they should normally be treated as
separate commercial products even if intentionally
photographed together.

Example:

Card holder + ballpoint pen

If the catalogue identifies both separately:

6. Card holder - NLC406X
7. Ballpoint pen - NSC3284X

then identify two separate assets/products.

Do NOT merge them merely because they appear in one
photographic composition.

============================================================
VARIANT RULE
============================================================

Several visually different images may represent variants
of ONE product.

Examples:

- Grey bag
- Black bag
- Red bag
- Blue bag

If the catalogue context indicates that they are variants
of the same product, classify them as product variants,
NOT independent products.

A variant does NOT require the colour/variant name to be
explicitly written beside the image.

If the visual distinction is clear but the text does not
explicitly name the colour:

- identify it as a visual variant;
- provide a visual variant hint only when reasonably clear;
- mark the source as "visual";
- do not invent an unsupported colour name.

If the colour/variant cannot be reliably determined:

variant_hint = null

============================================================
IMAGE ROLE RULE
============================================================

Classify each relevant visual asset as one of:

catalog_product
product_variant
secondary_product_image
lifestyle_image
marketing_accessory
bundle_component
decorative_or_irrelevant
ambiguous

Definitions:

catalog_product:
A standalone commercial product.

product_variant:
A distinct variant of the same commercial product.

secondary_product_image:
Another useful image/view of the same product or variant.

lifestyle_image:
A person/environment showing the product being used.

marketing_accessory:
An object intentionally shown to promote/complement the
main product but not necessarily the main product.

bundle_component:
An item explicitly represented as part of a bundle/set.

decorative_or_irrelevant:
Not useful as a product image.

ambiguous:
Insufficient evidence for reliable classification.

============================================================
CROPPING RULE
============================================================

For every relevant visual asset, provide a normalized
bounding box relative to the COMPLETE ORIGINAL PAGE IMAGE.

Coordinates must be between 0 and 1.

Use:

x
y
width
height

where:

x = left position / page width
y = top position / page height
width = asset width / page width
height = asset height / page height

The bounding box must contain the actual visual object,
not the surrounding caption or unrelated text.

If two products are photographed together, return separate
bounding boxes whenever their visual boundaries can be
reasonably determined.

Do NOT return the entire Azure figure as the bounding box
when it contains multiple independent products.

============================================================
TEXT ASSOCIATION
============================================================

Associate each asset with the OCR text that supports it.

Do not copy unrelated OCR text into an asset.

If a text block describes the whole product, it may be
associated with multiple variant images of that product.

============================================================
PRIMARY IMAGE RULE
============================================================

For each product/variant, identify the best clean visual
representation as:

image_role = primary

Lifestyle images should normally NOT be primary.

If a product image is unavailable but a lifestyle image is
the only representation, classify it as lifestyle_image
rather than pretending it is a clean product image.

============================================================
OUTPUT
============================================================

Return ONLY valid JSON.

The JSON must contain:

{
  "assets": [
    {
      "asset_id": "...",
      "figure_id": "...",
      "product_id": "...",
      "product_name": "...",
      "sku": "...",
      "relationship": "...",
      "image_role": "...",
      "variant_hint": null,
      "variant_hint_source": null,
      "bbox": {
        "x": 0,
        "y": 0,
        "width": 0,
        "height": 0
      },
      "ocr_text": [],
      "confidence": 0,
      "reason": "..."
    }
  ],
  "notes": []
}

Never invent a SKU.

Never invent a product name when the evidence does not
support it.

Never force two products into one product merely because
they share an Azure figure.

Never force visually different variants into separate
products merely because their colours differ.

The objective is accurate commercial-product and
individual-image mapping.
"""


# ============================================================
# MAIN ASSET MAPPER
# ============================================================

def map_assets_with_openai(
    evidence,
    product_mapping,
    model=None
):
    """
    Identify individual visual assets inside Azure figures.

    This is intentionally separate from the product mapper.

    Product mapper:
        figure -> commercial product grouping

    Asset mapper:
        product grouping -> individual visual assets/crops
    """

    if not isinstance(
        evidence,
        dict
    ):

        raise ValueError(
            "evidence must be a dictionary."
        )

    if not isinstance(
        product_mapping,
        dict
    ):

        raise ValueError(
            "product_mapping must be a dictionary."
        )

    client = _get_openai_client()

    model = (
        model
        or os.environ.get(
            "OPENAI_VISION_MODEL",
            "gpt-4.1-mini"
        )
    )

    original_pages = evidence.get(
        "original_page_images",
        []
    )

    figures = evidence.get(
        "figures",
        []
    )

    pages = evidence.get(
        "pages",
        []
    )

    paragraphs = evidence.get(
        "paragraphs",
        []
    )

    content = [

        {
            "type":
                "input_text",

            "text":
                _build_asset_system_prompt()
        },

        {
            "type":
                "input_text",

            "text":
                (
                    "Here is the PRODUCT MAPPING "
                    "produced by the previous AI stage.\n\n"
                    + json.dumps(
                        product_mapping,
                        ensure_ascii=False,
                        default=str
                    )
                )
        },

        {
            "type":
                "input_text",

            "text":
                (
                    "Here is the Azure evidence.\n\n"
                    + json.dumps(
                        {
                            "figures": figures,
                            "pages": pages,
                            "paragraphs": paragraphs,
                        },
                        ensure_ascii=False,
                        default=str
                    )
                )
        },

    ]

    # ========================================================
    # ORIGINAL PAGE FIRST
    # ========================================================

    for page_image in (
        original_pages or []
    ):

        if isinstance(
            page_image,
            dict
        ):

            image_base64 = (
                page_image.get(
                    "image_base64"
                )
            )

            mime_type = (
                page_image.get(
                    "mime_type",
                    "image/png"
                )
            )

            page_number = (
                page_image.get(
                    "page_number"
                )
            )

        else:

            image_base64 = page_image
            mime_type = "image/png"
            page_number = None

        image_url = _image_data_url(
            image_base64,
            mime_type
        )

        if not image_url:
            continue

        content.append({

            "type":
                "input_text",

            "text":
                (
                    "ORIGINAL CATALOGUE PAGE "
                    f"{page_number or ''}. "
                    "Use this as the PRIMARY visual "
                    "reference for all asset segmentation."
                )
        })

        content.append({

            "type":
                "input_image",

            "image_url":
                image_url,

        })

    # ========================================================
    # AZURE FIGURES
    # ========================================================

    for figure in (
        figures or []
    ):

        if not isinstance(
            figure,
            dict
        ):
            continue

        figure_id = (
            figure.get(
                "figure_id"
            )
        )

        image_base64 = (
            figure.get(
                "image_base64"
            )
        )

        mime_type = (
            figure.get(
                "mime_type",
                "image/png"
            )
        )

        image_url = _image_data_url(
            image_base64,
            mime_type
        )

        content.append({

            "type":
                "input_text",

            "text":
                (
                    "AZURE FIGURE "
                    f"{figure_id}. "
                    "This is supporting evidence. "
                    "Do not assume the entire figure is "
                    "one commercial product."
                )
        })

        if image_url:

            content.append({

                "type":
                    "input_image",

                "image_url":
                    image_url,

            })

    # ========================================================
    # FINAL TASK
    # ========================================================

    content.append({

        "type":
            "input_text",

        "text":
            (
                "Now identify every relevant individual "
                "visual asset required for product and "
                "variant creation. Separate products "
                "photographed together when catalogue "
                "evidence identifies them separately. "
                "Keep multiple images together when they "
                "represent one product or its variants. "
                "Return exact normalized bounding boxes "
                "on the COMPLETE ORIGINAL PAGE IMAGE."
            )
    })

    response = client.responses.create(

        model=model,

        input=[

            {
                "role":
                    "user",

                "content":
                    content
            }

        ],

        temperature=0,

    )

    raw_text = (
        response.output_text
    )

    try:

        result = json.loads(
            raw_text
        )

    except Exception:

        _logger.exception(
            "[OPENAI ASSET MAPPER] "
            "Invalid JSON returned."
        )

        raise RuntimeError(
            "OpenAI asset mapper returned "
            "invalid JSON."
        )

    return result