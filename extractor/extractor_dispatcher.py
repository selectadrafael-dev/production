import logging
from family_detector import detect_family
from extract_family_a import extract_pdf as extract_family_a
from extract_family_b import extract_pdf as extract_family_b

_logger = logging.getLogger(__name__)


def extract_pdf(

    file,

    preview=False

):

    family = detect_family(file)

    _logger.warning(

        f"[DISPATCHER] family={family}"

    )

    file.seek(0)

    if family == "A":

        return extract_family_a(

            file,

            preview=preview

        )

    return extract_family_b(

        file,

        preview=preview

    )