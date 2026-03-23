from flask import Flask, request, jsonify
import fitz
import base64
import logging
import os

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


@app.route('/')
def home():
    return "OK"


@app.route("/extract", methods=["POST"])
def extract():

    _logger.info("REQUEST RECEIVED")

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if not file:
        return jsonify({"error": "Empty file"}), 400

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

        for img in images:
            try:
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image.get("image")

                if not image_bytes:
                    continue

                image_base64 = base64.b64encode(image_bytes).decode("utf-8")
                image_list.append(image_base64)

            except Exception:
                continue

        pages_data.append({
            "page": page_number + 1,
            "text": text,
            "images": image_list
        })

    return jsonify(pages_data)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)