import fitz

import io

from PIL import Image

from page_features import analyze_page

from layout_classifier import LayoutClassifier

from page_analyzer import page_analyzer


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

    features = analyze_page(

        image

    )

    layout = page_analyzer.analyze(
        image
    )

    features.update(layout)

    result = classifier.classify(

        features

    )

    return result["family"]