import logging
import time

from models import RecoveryPage

_logger = logging.getLogger(__name__)


class RecoveryV2:

    def recover_page(self, page_data):

        start = time.time()

        _logger.info("========== RECOVERY V2 START ==========")

        page = RecoveryPage(

            page_number=page_data.get("page_number", 0),

            page_width=page_data.get("page_width", 0),

            page_height=page_data.get("page_height", 0),

            page_image=page_data.get("page_image")

        )

        self.layout(page)

        self.detect(page)

        self.segment(page)

        self.certify(page)

        result = self.package(page)

        _logger.info(

            "[RECOVERY V2 FINISHED] %.2fs",

            time.time() - start

        )

        return result

    def layout(self, page):

        _logger.info("[LAYOUT ENGINE]")

        return page

    def detect(self, page):

        _logger.info("[PRODUCT DETECTOR]")

        return page

    def segment(self, page):

        _logger.info("[SEGMENTER]")

        return page

    def certify(self, page):

        _logger.info("[CERTIFIER]")

        return page

    def package(self, page):

        _logger.info("[PACKAGER]")

        return {

            "success": True,

            "assets": [],

            "page": page.page_number

        }


recovery_v2 = RecoveryV2()