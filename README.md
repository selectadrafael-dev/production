# PDF Extractor Service

This service extracts:
- Text
- Images (base64)

Endpoint:
POST /extract

Input:
- file (PDF)

Output:
[
  {
    "page": 1,
    "text": "...",
    "images": ["base64..."]
  }
]