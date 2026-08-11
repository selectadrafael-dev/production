import os

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import (
    DocumentIntelligenceClient
)


AZURE_ENDPOINT = os.environ["AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"]
AZURE_KEY = os.environ["AZURE_DOCUMENT_INTELLIGENCE_KEY"]


client = DocumentIntelligenceClient(
    endpoint=AZURE_ENDPOINT,
    credential=AzureKeyCredential(AZURE_KEY)
)

def analyze_pdf_with_azure(pdf_bytes):

    poller = client.begin_analyze_document(
        "prebuilt-layout",
        body=pdf_bytes,
        output=["figures"]
    )

    result = poller.result()

    return result