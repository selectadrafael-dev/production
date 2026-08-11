import os
import logging

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import (
    DocumentIntelligenceClient
)
from azure.ai.documentintelligence.models import (
    AnalyzeOutputOption,
    AnalyzeDocumentRequest
)


_logger = logging.getLogger(__name__)


AZURE_ENDPOINT = os.environ.get(
    "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"
)

AZURE_KEY = os.environ.get(
    "AZURE_DOCUMENT_INTELLIGENCE_KEY"
)


if not AZURE_ENDPOINT:
    raise RuntimeError(
        "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT "
        "is not configured"
    )

if not AZURE_KEY:
    raise RuntimeError(
        "AZURE_DOCUMENT_INTELLIGENCE_KEY "
        "is not configured"
    )


client = DocumentIntelligenceClient(
    endpoint=AZURE_ENDPOINT,
    credential=AzureKeyCredential(
        AZURE_KEY
    )
)


def analyze_pdf(file_stream):

    _logger.warning(
        "[AZURE LAYOUT] Starting document analysis"
    )

    document_bytes = file_stream.read()

    if not document_bytes:

        raise ValueError(
            "Uploaded PDF is empty"
        )

    _logger.warning(
        "[AZURE LAYOUT] Received %s bytes",
        len(document_bytes)
    )

    request = AnalyzeDocumentRequest(
        bytes_source=document_bytes
    )

    poller = client.begin_analyze_document(

        model_id="prebuilt-layout",

        body=request,

        output=[
            AnalyzeOutputOption.FIGURES
        ]

    )

    _logger.warning(
        "[AZURE LAYOUT] Waiting for analysis..."
    )

    result = poller.result()

    operation_id = poller.details.get(
        "operation_id"
    )

    _logger.warning(
        "[AZURE LAYOUT] Analysis completed"
    )

    _logger.warning(
        "[AZURE LAYOUT] Operation ID: %s",
        operation_id
    )

    return result, operation_id


def get_figure(
    result,
    operation_id,
    figure_id
):

    if not operation_id:
        raise RuntimeError(
            "Azure operation ID is missing"
        )

    if not figure_id:
        raise ValueError(
            "Figure ID is required"
        )

    _logger.warning(
        "[AZURE FIGURE] Retrieving figure %s",
        figure_id
    )

    response = client.get_analyze_result_figure(
        model_id=result.model_id,
        result_id=operation_id,
        figure_id=figure_id
    )

    return b"".join(response)