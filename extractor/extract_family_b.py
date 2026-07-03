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
from product_grid_splitter import product_grid_splitter
from product_candidate_builder import product_candidate_builder
from metadata_detector import metadata_detector
from association_engine import association_engine
from ocr_block_extractor import ocr_block_extractor

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

    ocr_blocks = ocr_block_extractor.extract(

        page

    )

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

    candidates = product_candidate_builder.build(

        "B",

        1,

        selected

    )

    metadata = metadata_detector.detect(
        ocr_blocks
    )

    candidates = association_engine.associate(
        candidates,
        metadata
    )


    selected = product_grid_splitter.split(

        image,
        selected

    )


    return jsonify({
        "family": "B",

        "regions": classified,

        "metadata": metadata,

        "candidates": candidates
    })