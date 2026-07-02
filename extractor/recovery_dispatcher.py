import logging
import os

from recovery import recover_page
from recovery_v2 import recovery_v2

_logger = logging.getLogger(__name__)


def dispatch():

    engine = os.getenv("RECOVERY_ENGINE", "v1").lower()

    _logger.warning(
        f"[RECOVERY DISPATCH] ENV={engine}"
    )

    # TEMPORARY: Force V2 for testing
    engine = "v2"

    _logger.warning(
        f"[RECOVERY DISPATCH] USING={engine}"
    )

    if engine == "v2":

        _logger.warning("[USING RECOVERY V2]")

        return recovery_v2.recover_page()

    _logger.warning("[USING RECOVERY V1]")

    return recover_page()