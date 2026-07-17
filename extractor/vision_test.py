import fitz
import logging

from flask import jsonify

_logger = logging.getLogger(__name__)


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

        page_info = {

            "page": page_index + 1,

            "width": pix.width,

            "height": pix.height,

            "text_length": len(

                page.get_text()

            ),

            "image_count": len(

                page.get_images(

                    full=True

                )
            )

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