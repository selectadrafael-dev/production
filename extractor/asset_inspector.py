import logging

_logger = logging.getLogger(__name__)


class AssetInspector:

    def process(self, page):

        report = []

        for index, asset in enumerate(page.assets):

            image = asset.image or {}

            report.append({

                "asset_id": asset.id,

                "index": index,

                "x": image.get("x", 0),

                "y": image.get("y", 0),

                "width": image.get("width", 0),

                "height": image.get("height", 0),

                "source": asset.source,

                "confidence": asset.confidence,

                "status": "pending"

            })

        page.metadata["inspection"] = report

        _logger.warning(

            "[ASSET INSPECTOR] "

            f"assets={len(report)}"

        )

        return page


asset_inspector = AssetInspector()