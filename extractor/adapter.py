import logging

from models import RecoveryPage
from models import Asset

_logger = logging.getLogger(__name__)


class RecoveryV2Adapter:

    def build_pages(self, normalized_blocks):

        pages = []

        for block in normalized_blocks:

            page = RecoveryPage(

                page_number=block.get(
                    "page",
                    0
                ),

                page_width=block.get(
                    "page_width",
                    0
                ),

                page_height=block.get(
                    "page_height",
                    0
                ),

                page_image=block.get(
                    "page_image"
                ),

                metadata={

                    "text": block.get(
                        "text",
                        ""
                    ),

                    "price": block.get(
                        "price",
                        ""
                    ),

                    "stock": block.get(
                        "stock",
                        ""
                    )

                }

            )

            for image in block.get(

                "images",

                []

            ):

                asset = Asset(

                    page_number=page.page_number,

                    image=image,

                    bbox=[

                        image.get(
                            "x",
                            0
                        ),

                        image.get(
                            "y",
                            0
                        ),

                        image.get(
                            "width",
                            0
                        ),

                        image.get(
                            "height",
                            0
                        )

                    ],

                    source="normalized"

                )

                page.assets.append(

                    asset

                )

            pages.append(page)

        _logger.warning(

            "[RECOVERY ADAPTER] "

            f"pages={len(pages)}"

        )

        return pages


adapter = RecoveryV2Adapter()