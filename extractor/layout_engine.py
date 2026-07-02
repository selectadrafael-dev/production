import logging

_logger = logging.getLogger(__name__)


class LayoutEngine:

    def process(self, page):

        _logger.warning(

            "[LAYOUT ENGINE] "

            f"page={page.page_number}"

        )

        page.metadata["layout"] = {

            "status": "ready"

        }

        return page


layout_engine = LayoutEngine()