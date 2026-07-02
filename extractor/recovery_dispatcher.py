import logging
import os

from recovery import recover_page
from recovery_v2 import recovery_v2

_logger = logging.getLogger(__name__)

RECOVERY_ENGINE = os.getenv(
    "RECOVERY_ENGINE",
    "v1"
).lower()


def dispatch():

    _logger.warning(
        f"[RECOVERY DISPATCH] engine={RECOVERY_ENGINE}"
    )

    if RECOVERY_ENGINE == "v2":

        _logger.warning("[USING RECOVERY V2]")

        return recovery_v2.recover_page()

    _logger.warning("[USING RECOVERY V1]")

    return recover_page()