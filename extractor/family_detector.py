import logging
import fitz

from PIL import Image

from page_features import analyze_page
from page_analyzer import page_analyzer
from layout_classifier import LayoutClassifier
from layout_fingerprint import layout_fingerprint

_logger = logging.getLogger(__name__)

classifier = LayoutClassifier()


def detect_family(file):

    pdf_bytes = file.read()

    file.seek(0)

    doc = fitz.open(

        stream=pdf_bytes,

        filetype="pdf"

    )

    page = doc[0]

    pix = page.get_pixmap(

        matrix=fitz.Matrix(1, 1),

        alpha=False

    )

    image = Image.frombytes(

        "RGB",

        [pix.width, pix.height],

        pix.samples

    )

    features = analyze_page(image)

    layout = page_analyzer.analyze(image)

    features.update(layout)

    result = classifier.classify(features)

    _logger.warning(

        f"[FAMILY DETECTOR] "

        f"features={features}"

    )

    _logger.warning(

        f"[FAMILY DETECTOR] "

        f"family={result['family']} "

        f"confidence={result['confidence']}"

    )

    return result["family"]