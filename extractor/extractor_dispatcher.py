import logging

from family_detector import detect_family

from extract_family_a import extract_pdf as extract_family_a
from extract_family_b import extract_pdf as extract_family_b

_logger = logging.getLogger(__name__)


def extract_pdf(file):

    _logger.warning(
        f"[DISPATCHER ENTRY] file={file}"
    )

    _logger.warning(
        f"[DISPATCHER ENTRY] filename={getattr(file, 'filename', None)}"
    )

    family = detect_family(file)

    # Reset stream after detector reads it
    file.seek(0)

    _logger.warning(

        f"[CATALOG FAMILY] {family}"

    )

    _logger.warning(

        f"[DISPATCHER] family={family}"

    )

    if family == "A":

        _logger.warning(
            f"[DISPATCHER -> FAMILY A] file={file}"
        )
        
        return extract_family_a(file)

    return extract_family_b(file)