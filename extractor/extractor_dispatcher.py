import logging

from family_detector import detect_family

from extract_family_a import extract_pdf as extract_family_a

from extract_family_b import extract_pdf as extract_family_b

_logger = logging.getLogger(__name__)


def extract_pdf(file):

    family = detect_family(file)

    _logger.warning(

        f"[CATALOG FAMILY] "

        f"{family}"

    )

    _logger.warning(

        f"[CATALOG FAMILY] "

        f"{family}"

    )

    _logger.warning(

        f"[DISPATCHER] "

        f"family={family}"

    )

    if family == "A":

        return extract_family_a()

    return extract_family_b(file)