import logging

_logger = logging.getLogger(__name__)


class LayoutFingerprint:

    def build(self, features):

        fingerprint = {

            "region_density":

                features["total_regions"],

            "large_ratio":

                features["large_regions"],

            "small_ratio":

                features["small_regions"],

            "page_size": (

                features["page_width"],

                features["page_height"]

            )

        }

        _logger.warning(

            f"[LAYOUT FINGERPRINT] "

            f"{fingerprint}"

        )

        return fingerprint


layout_fingerprint = LayoutFingerprint()