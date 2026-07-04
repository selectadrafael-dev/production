import logging

from family_detector import detect_family

from extract_family_a import extract_pdf as extract_family_a
from extract_family_b import extract_pdf as extract_family_b


_logger = logging.getLogger(__name__)


#
# Temporary switch
#
USE_GROUP_B = True


def extract_pdf(

    file,

    preview=False

):

    # ===================================
    # TEMPORARY UNIVERSAL ENGINE
    # ===================================

    if USE_GROUP_B:

        _logger.warning(

            "[DISPATCHER] "

            "Routing ALL catalogues "

            "to Group B"

        )

        return extract_family_b(

            file,

            preview=preview

        )

    # ===================================
    # Legacy fallback
    # ===================================

    family = detect_family(file)

    if family == "A":

         return extract_family_a(file)

    return extract_family_b(

        file,

        preview=preview

    )