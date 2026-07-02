import logging

_logger = logging.getLogger(__name__)


class EvidenceCollector:

    def process(self, page):

        for asset in page.assets:

            image = asset.image or {}

            width = image.get("width", 0)
            height = image.get("height", 0)

            asset.metadata["evidence"] = {

                "width": width,

                "height": height,

                "area": width * height,

                "aspect_ratio":
                    round(width / height, 3)
                    if height else 0,

                "page_number":
                    asset.page_number,

                "source":
                    asset.source

            }

        _logger.warning(

            "[EVIDENCE COLLECTOR] "

            f"assets={len(page.assets)}"

        )

        return page


evidence_collector = EvidenceCollector()