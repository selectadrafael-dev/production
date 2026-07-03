from flask import jsonify
import logging
import fitz

from PIL import Image

import io

from page_regions import page_region_analyzer
from region_classifier import region_classifier

from product_region_selector import product_region_selector
from product_region_decomposer import product_region_decomposer
from product_cropper import product_cropper

_logger = logging.getLogger(__name__)


def extract_pdf(file):

    _logger.warning(

        "[FAMILY B] "

        "Extractor Selected"

    )

    pdf_bytes = file.read()

    doc = fitz.open(

        stream=pdf_bytes,

        filetype="pdf"

    )

    page = doc[0]

    pix = page.get_pixmap(

        matrix=fitz.Matrix(2,2),

        alpha=False

    )

    image = Image.frombytes(

        "RGB",

        [pix.width, pix.height],

        pix.samples

    )


    regions = page_region_analyzer.analyze(
        image
    )

    classified = region_classifier.classify(

        image,

        regions

    )

    selected = product_region_selector.select(

        classified

    )

    selected = product_region_decomposer.decompose(

        image,

        selected

    )

    selected = product_cropper.crop(

        image,

        selected

    )

  
    return jsonify({

        "family": "B",

        "regions": classified,

        "product_regions": selected

    })