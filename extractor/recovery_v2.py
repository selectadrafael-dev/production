import logging
from flask import request, jsonify
from models import RecoveryPage
from asset_builder import asset_builder
from layout_engine import layout_engine
from product_detector import product_detector
from segmenter_v2 import segmenter_v2
from certifier import certifier
from asset_packager import asset_packager
import time

from extract_pdf import extract_pdf
from asset_inspector import asset_inspector
from evidence_collector import evidence_collector
from vision_provider import vision_provider
from adapter import adapter
from quality_gate import quality_gate
from decision_engine import decision_engine

_logger = logging.getLogger(__name__)


class RecoveryV2:

    def recover_page(self):

        start = time.time()

        data = request.get_json(silent=True) or {}

        page = RecoveryPage(

            page_number=data.get("page_number", 0),

            page_width=data.get("page_width", 0),

            page_height=data.get("page_height", 0),

            page_image=data.get("page_image"),

            metadata={

                "images": data.get("images", []),

                "text": data.get("text", "")

            }

        )

        page = layout_engine.process(page)

        page = asset_builder.process(page)

        page = asset_inspector.process(page)

        page = evidence_collector.process(page)

        for asset in page.assets:

            vision_provider.analyze(asset)

        page = quality_gate.process(page)

        page = decision_engine.process(page)

        page = product_detector.process(page)

        page = segmenter_v2.process(page)

        page = certifier.process(page)

        result = asset_packager.process(page)

        result["statistics"] = {

            "images_received": len(

                page.metadata.get(

                    "images",

                    []

                )

            ),

            "assets_created": len(

                page.assets

            ),

            "assets_certified": len(

                [

                    a for a in page.assets

                    if a.certified

                ]

            ),

            "assets_rejected": len(

                [

                    a for a in page.assets

                    if a.rejected

                ]

            )

        }

        result["processing_time"] = round(

            time.time() - start,

            3

        )

        return jsonify(

            result

        )


recovery_v2 = RecoveryV2()


def process_catalog(self, pdf_file):

    start = time.time()

    extracted = extract_pdf(pdf_file)

    pages = extracted.get(

        "pages",

        []

    )

    report = {

        "success": True,

        "version": "v2",

        "pages": len(pages),

        "processing_time": 0,

        "statistics": {

            "images_found": 0,

            "assets_created": 0,

            "assets_certified": 0,

            "assets_rejected": 0

        },

        "page_reports": []

    }

    for page in pages:

        page_report = self.process_page(page)

        report["page_reports"].append(

            page_report

        )

        report["statistics"]["images_found"] += page_report["images"]

        report["statistics"]["assets_created"] += page_report["assets"]

    report["processing_time"] = round(

        time.time() - start,

        2

    )

    return jsonify(report)


def process_page(self, page):

    images = page.get(

        "images",

        []

    )

    return {

        "page": page.get(

            "page_number",

            0

        ),

        "images": len(images),

        "assets": len(images)

    }


def process_blocks(

    self,

    normalized_blocks

):

    pages = adapter.build_pages(

        normalized_blocks

    )

    report = []

    for page in pages:

        page = layout_engine.process(

            page

        )

        page = asset_inspector.process(

            page

        )

        page = evidence_collector.process(

            page

        )

        for asset in page.assets:

            vision_provider.analyze(

                asset

            )

        page = product_detector.process(

            page

        )

        page = segmenter_v2.process(

            page
        )

        page = certifier.process(

            page

        )

        result = asset_packager.process(

            page

        )

        report.append(

            result

        )

    return report