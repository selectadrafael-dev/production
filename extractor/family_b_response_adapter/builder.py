"""
builder.py
Family B Response Adapter - builds Family A compatible response.
"""
import logging
from .serializer import response_serializer
_logger = logging.getLogger(__name__)

class FamilyBResponseBuilder:

    def build(self, response_data, preview=False):

        response_data = response_serializer.sanitize(
            response_data
        )

        _logger.warning(
            "[FAMILY B ADAPTER INPUT] "
            "family=%s "
            "| version=%s "
            "| page_image=%s "
            "| page_image_chars=%s "
            "| trace=%s "
            "| candidates=%s",
            response_data.get(
                "extractor_family"
            ),
            response_data.get(
                "extractor_version"
            ),
            bool(
                response_data.get(
                    "page_image"
                )
            ),
            len(
                response_data.get(
                    "page_image"
                ) or ""
            ),
            bool(
                response_data.get(
                    "extractor_trace"
                )
            ),
            len(
                response_data.get(
                    "candidates"
                ) or []
            ),
        )

       

        pages = []

        candidates = response_data.get("candidates", [])
        text = response_data.get("text", "")

        images = []

        for item in candidates:
            if not isinstance(item, dict):
                continue

            if "image" in item:
                images.append({
                    "image": item.get("image"),
                    "width": item.get("width", 0),
                    "height": item.get("height", 0),
                    "x": item.get("x", 0),
                    "y": item.get("y", 0),
                    "score": item.get("score", 0),
                    "is_lifestyle": item.get("is_lifestyle", False),
                })


        # ===================================================
        # FAMILY B → FAMILY A COMPATIBLE PAGE
        # ===================================================

        page_image = response_data.get(
            "page_image",
            ""
        )

        page_width = response_data.get(
            "page_width",
            0
        )

        page_height = response_data.get(
            "page_height",
            0
        )

       
        pages.append({

            "page": 1,

            "text": text,

            # =================================================
            # ORIGINAL CATALOGUE PAGE
            # =================================================

            "page_image": page_image,

            "page_image_size":
                len(page_image or ""),

            "page_width":
                page_width,

            "page_height":
                page_height,

            # =================================================
            # EXTRACTED ASSETS
            # =================================================

            "images": images,
        })


        # =================================================
        # FAMILY B STANDARD RESPONSE CONTRACT
        # =================================================

        result = {

            "extractor_family":
                response_data.get(
                    "extractor_family",
                    "B"
                ),

            "extractor_version":
                response_data.get(
                    "extractor_version",
                    "family_b_v1"
                ),

            "extractor_trace":
                response_data.get(
                    "extractor_trace",
                    []
                ),

            "pages":
                pages,
        }

        if preview:
            debug = {}
            for key in ("pipeline","statistics","diagnostics","regions","selected_regions","family"):
                if key in response_data:
                    debug[key]=response_data[key]
            result["debug"]=debug

        # =================================================
        # FAMILY B ADAPTER FINAL RESPONSE
        # =================================================

        _logger.warning(
            "[FAMILY B ADAPTER FINAL] "
            "family=%s "
            "| version=%s "
            "| pages=%s "
            "| page_image=%s "
            "| page_image_chars=%s "
            "| assets=%s",
            result.get(
                "extractor_family"
            ),
            result.get(
                "extractor_version"
            ),
            len(
                result.get(
                    "pages"
                ) or []
            ),
            bool(
                pages
                and pages[0].get(
                    "page_image"
                )
            ),
            len(
                pages[0].get(
                    "page_image"
                ) or ""
            ) if pages else 0,
            len(
                pages[0].get(
                    "images"
                ) or []
            ) if pages else 0,
        )

        # =================================================
        # FAMILY B ADAPTER FINAL RESPONSE
        # =================================================

        _logger.warning(
            "[FAMILY B ADAPTER FINAL] "
            "family=%s "
            "| version=%s "
            "| pages=%s "
            "| page_image=%s "
            "| page_image_chars=%s "
            "| assets=%s",
            result.get(
                "extractor_family"
            ),
            result.get(
                "extractor_version"
            ),
            len(
                result.get(
                    "pages"
                ) or []
            ),
            bool(
                pages
                and pages[0].get(
                    "page_image"
                )
            ),
            (
                len(
                    pages[0].get(
                        "page_image"
                    ) or ""
                )
                if pages else 0
            ),
            (
                len(
                    pages[0].get(
                        "images"
                    ) or []
                )
                if pages else 0
            ),
        )
        return result

family_b_response_builder = FamilyBResponseBuilder()
