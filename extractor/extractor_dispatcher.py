import logging
from family_detector import detect_family
from extract_family_a import extract_pdf as extract_family_a
from extract_family_b import extract_pdf as extract_family_b

_logger = logging.getLogger(__name__)


def extract_pdf(file):

    result = detect_family(file)

    family = result["family"]

    _logger.warning(

        f"[CATALOG FAMILY] "

        f"{family}"

    )

    _logger.warning(

        f"[DISPATCHER] "

        f"family={family} "

        f"confidence={result['confidence']}"

    )

    file.seek(0)

    if family == "A":

        return extract_family_a(file)

    return extract_family_b(file)