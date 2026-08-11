import os
import logging

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeOutputOption


_logger = logging.getLogger(__name__)


AZURE_ENDPOINT = os.environ.get(
    "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"
)

AZURE_KEY = os.environ.get(
    "AZURE_DOCUMENT_INTELLIGENCE_KEY"
)


if not AZURE_ENDPOINT:
    raise RuntimeError(
        "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT is not configured"
    )

if not AZURE_KEY:
    raise RuntimeError(
        "AZURE_DOCUMENT_INTELLIGENCE_KEY is not configured"
    )


client = DocumentIntelligenceClient(
    endpoint=AZURE_ENDPOINT,
    credential=AzureKeyCredential(AZURE_KEY)
)


def analyze_pdf(file_stream):

    """
    Send a PDF to Azure Document Intelligence Layout
    and return the raw structured analysis required
    for our product-association pipeline.
    """

    _logger.warning(
        "[AZURE LAYOUT] Starting document analysis"
    )

    poller = client.begin_analyze_document(
        "prebuilt-layout",
        body=file_stream,
        output=[
            AnalyzeOutputOption.FIGURES
        ]
    )

    result = poller.result()

    _logger.warning(
        "[AZURE LAYOUT] Analysis completed"
    )

    return result

def _polygon_to_list(polygon):

    if not polygon:
        return []

    return [
        float(value)
        for value in polygon
    ]


def _bounding_regions(regions):

    output = []

    if not regions:
        return output

    for region in regions:

        output.append({

            "page_number": region.page_number,

            "polygon": _polygon_to_list(
                region.polygon
            )

        })

    return output


def serialize_result(result):

    data = {

        "model_id": getattr(
            result,
            "model_id",
            None
        ),

        "content": getattr(
            result,
            "content",
            ""
        ),

        "pages": [],

        "paragraphs": [],

        "figures": [],

        "tables": []

    }

    # =====================================================
    # Pages
    # =====================================================

    for page in result.pages or []:

        page_data = {

            "page_number": page.page_number,

            "width": page.width,

            "height": page.height,

            "unit": page.unit,

            "angle": page.angle,

            "lines": [],

            "words": []

        }

        # -------------------------------------------------
        # Lines
        # -------------------------------------------------

        for line in page.lines or []:

            page_data["lines"].append({

                "content": line.content,

                "polygon": _polygon_to_list(
                    line.polygon
                )

            })

        # -------------------------------------------------
        # Words
        # -------------------------------------------------

        for word in page.words or []:

            page_data["words"].append({

                "content": word.content,

                "confidence": word.confidence,

                "polygon": _polygon_to_list(
                    word.polygon
                )

            })

        data["pages"].append(
            page_data
        )

    # =====================================================
    # Paragraphs
    # =====================================================

    for paragraph in result.paragraphs or []:

        data["paragraphs"].append({

            "content": paragraph.content,

            "role": getattr(
                paragraph,
                "role",
                None
            ),

            "bounding_regions":
                _bounding_regions(
                    paragraph.bounding_regions
                )

        })

    # =====================================================
    # Figures
    # =====================================================

    for figure in result.figures or []:

        figure_data = {

            "id": figure.id,

            "bounding_regions":
                _bounding_regions(
                    figure.bounding_regions
                ),

            "spans": [],

            "elements": [],

            "caption": None

        }

        # -------------------------------------------------
        # Spans
        # -------------------------------------------------

        for span in figure.spans or []:

            figure_data["spans"].append({

                "offset": span.offset,

                "length": span.length

            })

        # -------------------------------------------------
        # Related elements
        # -------------------------------------------------

        if figure.elements:

            figure_data["elements"] = list(
                figure.elements
            )

        # -------------------------------------------------
        # Caption
        # -------------------------------------------------

        if figure.caption:

            figure_data["caption"] = {

                "content":
                    figure.caption.content,

                "bounding_regions":
                    _bounding_regions(
                        figure.caption.bounding_regions
                    )

            }

        data["figures"].append(
            figure_data
        )

    # =====================================================
    # Tables
    # =====================================================

    for table in result.tables or []:

        table_data = {

            "row_count":
                table.row_count,

            "column_count":
                table.column_count,

            "bounding_regions":
                _bounding_regions(
                    table.bounding_regions
                ),

            "cells": []

        }

        for cell in table.cells or []:

            table_data["cells"].append({

                "row_index":
                    cell.row_index,

                "column_index":
                    cell.column_index,

                "content":
                    cell.content,

                "kind":
                    getattr(
                        cell,
                        "kind",
                        None
                    ),

                "bounding_regions":
                    _bounding_regions(
                        cell.bounding_regions
                    )

            })

        data["tables"].append(
            table_data
        )

    return data