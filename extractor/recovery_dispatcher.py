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

        "[RECOVERY DISPATCH] "

        f"engine={RECOVERY_ENGINE}"

    )

    if RECOVERY_ENGINE == "v2":

        return recovery_v2.recover_page()

    return recover_page()