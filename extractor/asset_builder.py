import logging

from models import Asset

_logger = logging.getLogger(__name__)


class AssetBuilder:

    def process(self, page):

        images = page.metadata.get("images", [])

        _logger.warning(

            "[ASSET BUILDER] "

            f"images={len(images)}"

        )

        for image in images:

            asset = Asset(

                page_number=page.page_number,

                bbox=[

                    image.get("x", 0),

                    image.get("y", 0),

                    image.get("width", 0),

                    image.get("height", 0)

                ],

                image=image,

                source="extractor"

            )

            page.assets.append(asset)

        _logger.warning(

            "[ASSET BUILDER] "

            f"assets={len(page.assets)}"

        )

        return page


asset_builder = AssetBuilder()