import logging

_logger = logging.getLogger(__name__)


class Certifier:

    def process(self, page):

        _logger.warning(

            "[CERTIFIER] "

            f"assets={len(page.assets)}"

        )

        return page


certifier = Certifier()