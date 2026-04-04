from flask import Flask, request, jsonify
import fitz
import base64
import logging
import os
from PIL import Image
import io

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


# ================= HOME =================
@app.route('/')
def home():
    return "OK"


# ================= PDF EXTRACT =================
@app.route("/extract", methods=["POST"])
def extract():

    _logger.info("PDF REQUEST RECEIVED")

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    try:
        pdf_bytes = file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception:
        return jsonify({"error": "Invalid PDF"}), 400

    pages_data = []

    for page_number, page in enumerate(doc):

        text = page.get_text("text") or ""
        image_list = []

        images = page.get_images(full=True)

        MAX_IMAGES_PER_PAGE = 5

        for img_data in images:
            try:
                if len(image_list) >= MAX_IMAGES_PER_PAGE:
                    break

                xref = img_data[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image.get("image")

                if not image_bytes:
                    continue

                img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

                img.thumbnail((800, 800))

                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=70)

                compressed_bytes = buffer.getvalue()

                image_base64 = base64.b64encode(compressed_bytes).decode("utf-8")

                image_list.append(image_base64)

            except Exception:
                continue

        _logger.info(f"PAGE {page_number+1} → IMAGES KEPT: {len(image_list)}")

        pages_data.append({
            "page": page_number + 1,
            "text": text,
            "images": image_list
        })

    return jsonify(pages_data)

# ================= START APP =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)