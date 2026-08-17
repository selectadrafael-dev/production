# Flask
from flask import jsonify, request

# Standard
import logging
import fitz
import base64
import io

import base64
import io

# Pillow
from PIL import Image

# OCR
from ocr_block_extractor import ocr_block_extractor

# Analysis
from page_regions import page_region_analyzer
from region_classifier import region_classifier
from product_region_selector import product_region_selector
from product_region_decomposer import product_region_decomposer
from product_grid_splitter import product_grid_splitter

# Candidate
from product_cropper import product_cropper
from product_candidate_builder import product_candidate_builder
from metadata_detector import metadata_detector
from asset_recovery.recovery_engine import recovery_engine
from association_engine import association_engine

# QA
from qa.preview_generator import preview_generator
from qa.processing_report import processing_report
from qa.region_diagnostics import region_diagnostics

from region_analyzer_dispatcher import region_analyzer_dispatcher
from product_relationship_engine import product_relationship_engine
# from qa.preview_generator import preview_generator
from qa.asset_preview_generator import asset_preview_generator
from universal_contour_detector import universal_contour_detector
from family_b_response_adapter import family_b_response_builder


_logger = logging.getLogger(__name__)


def extract_pdf(

    file,

    preview=False

):
    _logger.warning(

        "[FAMILY B] "

        "Extractor Selected"

    )

    processing_report.clear()

    pdf_bytes = file.read()

    doc = fitz.open(

        stream=pdf_bytes,

        filetype="pdf"

    )

    page = doc[0]

    ocr_blocks = ocr_block_extractor.extract(

        page
    )

    page_text = "\n".join(

        block.get(

            "text",

            ""

        ).strip()

        for block in ocr_blocks

        if block.get(

            "text"

        )

    )

    pix = page.get_pixmap(

        matrix=fitz.Matrix(2,2),

        alpha=False

    )

    # =================================================
    # FAMILY B ORIGINAL CATALOGUE PAGE
    # =================================================

    page_buffer = io.BytesIO()

    image.save(
        page_buffer,
        format="JPEG",
        quality=85
    )

    page_base64 = base64.b64encode(
        page_buffer.getvalue()
    ).decode("utf-8")

    _logger.warning(
        "[FAMILY B PAGE IMAGE] "
        "page=1 "
        "| present=%s "
        "| chars=%s "
        "| size=%sx%s",
        bool(page_base64),
        len(page_base64),
        image.width,
        image.height,
    )

    image = Image.frombytes(

        "RGB",

        [pix.width, pix.height],

        pix.samples

    )

    # =================================================
    # FAMILY B ORIGINAL PAGE IMAGE
    # =================================================

    page_buffer = io.BytesIO()

    image.save(
        page_buffer,
        format="JPEG",
        quality=85
    )

    page_base64 = base64.b64encode(
        page_buffer.getvalue()
    ).decode("utf-8")

    _logger.warning(
        "[FAMILY B PAGE IMAGE] "
        "page=1 "
        "| present=%s "
        "| chars=%s "
        "| size=%sx%s",
        bool(page_base64),
        len(page_base64),
        image.width,
        image.height,
    )

    regions = page_region_analyzer.analyze(
        image
    )

    # regions_old = page_region_analyzer.analyze(

    #     image

    # )

    # regions_new = universal_contour_detector.detect(

    #     image

    # )

    # _logger.warning(

    #     "[COMPARE] "

    #     f"Old={len(regions_old)} "

    #     f"New={len(regions_new)}"

    # )

    #
    #  Temporarily use the better detector
    #

    # if len(regions_new) > len(regions_old):

    #     regions = regions_new

    # else:

    #     regions = regions_old

    regions = region_analyzer_dispatcher.analyze(

        image,

        regions

    )


    classified = region_classifier.classify(

        image,

        regions

    )

    processing_report.add(
        "Region Classifier",
        "PASS",
        {
            "regions": len(classified)
        }
    )

    selected = product_region_selector.select(

        classified

    )

    processing_report.add(
        "Region Selector",
        "PASS",
        {
            "selected": len(selected)
        }
    )

    selected = product_region_decomposer.decompose(

        image,

        selected

    )

    # selected = region_refiner.refine(

    #     image,

    #     selected

    # )


    processing_report.add(
        "Region Decomposer",
        "PASS",
        {
            "regions": len(selected)
        }
    )


    selected = product_grid_splitter.split(

        image,
        selected

    )

    for region in selected:

        region["detected_products"] = len(

            region.get(

                "products",

                []

            )

        )

    diagnostics = region_diagnostics.build(

        classified,

        selected

    )

    processing_report.add(

        "Grid Splitter",

        "PASS",

        {

            "products": len(selected)

        }

    )


    selected = product_cropper.crop(

        image,

        selected

    )

    processing_report.add(
        "Cropper",
        "PASS",
        {
            "products": len(selected)
        }
    )

    candidates = product_candidate_builder.build(

        "B",

        1,

        selected

    )

    processing_report.add(
        "Candidate Builder",
        "PASS",
        {
            "candidates": len(candidates)
        }
    )

    metadata = metadata_detector.detect(
        ocr_blocks
    )

    processing_report.add(

        "Metadata Detector",

        "PASS",

        {

            "blocks": len(metadata)

        }

    )


    candidates = association_engine.associate(
        candidates,
        metadata
    )

    #
    # Recovery Layer
    #

    candidates, recovery_report = recovery_engine.recover(

        image,

        candidates,

        metadata,

        classified

    )

    candidates = product_relationship_engine.build(

        candidates,

        metadata

    )

    processing_report.add(
        "Association Engine",
        "PASS",
        {
            "candidates": len(candidates)
        }
    )

    pipeline = processing_report.to_dict()

    preview_context = {

        "page_image": image.copy(),

        "text": page_text,

        "family": "B",

        "regions": classified,

        "selected": selected,

        "metadata": metadata,

        "candidates": candidates,

        "pipeline": pipeline,

        "diagnostics": diagnostics,

        "recovery": recovery_report,

        "statistics": {

            "regions": len(classified),

            "selected_regions": len(selected),

            "candidates": len(candidates),

            "metadata_blocks": len(metadata),

            "family": "B",

            "pipeline_steps": pipeline["summary"]["steps"],

            "processing_time": pipeline["summary"]["duration"]

        }

    }

    response_data = {

        # =================================================
        # EXTRACTOR IDENTITY
        # =================================================

        "extractor_family": "B",
        "extractor_version": "family_b_v1",

        # =================================================
        # ORIGINAL PAGE IMAGE
        # =================================================

        "page_image": page_base64,
        "page_image_size": len(page_base64),
        "page_width": image.width,
        "page_height": image.height,

        # =================================================
        # EXISTING RESPONSE
        # =================================================

        "family": preview_context["family"],
        "regions": preview_context["regions"],
        "selected": preview_context["selected"],
        "metadata": preview_context["metadata"],
        "candidates": preview_context["candidates"],
        "pipeline": preview_context["pipeline"],
        "statistics": preview_context["statistics"],
        "diagnostics": preview_context["diagnostics"],
        "recovery": preview_context["recovery"],
        "text": preview_context["text"],
    }

    # =================================================
    # FAMILY B RESPONSE TRACE
    # =================================================

    response_data["extractor_trace"] = [{

        "page": 1,

        "extractor_family": "B",

        "extractor_version": "family_b_v1",

        "page_image_present":
            bool(page_base64),

        "page_image_chars":
            len(page_base64),

        "page_width":
            image.width,

        "page_height":
            image.height,

        "regions":
            len(classified),

        "selected_regions":
            len(selected),

        "candidates":
            len(candidates),

        "metadata_blocks":
            len(metadata),
    }]

    _logger.warning(
        "[FAMILY B RESPONSE] %s",
        response_data["extractor_trace"]
    )

    try:
        # existing processing logic...

        preview_type = request.args.get(

            "type",

            "boxes"

        )

        if preview:

            if preview_type == "assets":

                return asset_preview_generator.preview(

                    preview_context

                )

            return preview_generator.preview(

                preview_context

            )
        

        response_data = family_b_response_builder.build(

            response_data,

            preview=preview

        )

        # =================================================
        # FAMILY B RESPONSE TRACE
        # =================================================

        response_data["extractor_trace"] = [{
            "page": 1,
            "extractor_family": "B",
            "extractor_version": "family_b_v1",
            "page_image_present": bool(page_base64),
            "page_image_chars": len(page_base64),
            "page_width": image.width,
            "page_height": image.height,
            "regions": len(classified),
            "selected_regions": len(selected),
            "candidates": len(candidates),
            "metadata_blocks": len(metadata),
        }]

        _logger.warning(
            "[FAMILY B FINAL RESPONSE] %s",
            response_data["extractor_trace"]
        )

        return jsonify(

            response_data

        )

    finally:
        try:
            doc.close()
        except Exception:
            pass
