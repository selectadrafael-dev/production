import logging

_logger = logging.getLogger(__name__)


class SegmenterV2:

    def process(self, page):

        _logger.warning(

            "[SEGMENTER] "

            f"assets={len(page.assets)}"

        )

        return page


segmenter_v2 = SegmenterV2()