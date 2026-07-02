import logging

_logger = logging.getLogger(__name__)


class AssetPackager:

    def process(self, page):

        _logger.warning(

            "[PACKAGER] "

            f"assets={len(page.assets)}"

        )


        inspection = page.metadata.get(
            "inspection",
            []
        )

        for item, asset in zip(
            inspection,
            page.assets
        ):

            item["evidence"] = asset.metadata.get(
                "evidence",
                {}
            )

            item["vision"] = asset.metadata.get(

                "vision",

                {}

            )

            item["certified"] = asset.certified

            item["rejected"] = asset.rejected

            item["rejection_reason"] = asset.rejection_reason

            item["decision"] = asset.metadata.get(
                "decision",
                {}
            )

        return {

            "success": True,

            "version": "v2",

            "statistics": {

                "assets": len(page.assets)

            },

            "inspection": inspection,

            "assets": []

        }


asset_packager = AssetPackager()