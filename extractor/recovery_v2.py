import logging
import time

from flask import jsonify

from models import RecoveryPage

_logger = logging.getLogger(__name__)


class RecoveryV2:

def recover_page(self):

    return jsonify({

        "success": True,

        "version": "v2",

        "message": "Recovery V2 reached successfully.",

        "assets": []

    })

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