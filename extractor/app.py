from flask import Flask, request, jsonify
import fitz  # PyMuPDF
import base64
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


@app.route("/extract", methods=["POST"])
def extract():

    _logger.info("REQUEST RECEIVED")

    # ---------------- VALIDATION ----------------
    if "file" not in request.files:
        _logger.error("NO FILE IN REQUEST")
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if not file:
        _logger.error("EMPTY FILE")
        return jsonify({"error": "Empty file"}), 400

    try:
        pdf_bytes = file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as e:
        _logger.exception("FAILED TO OPEN PDF")
        return jsonify({"error": "Invalid PDF"}), 400

    pages_data = []

    _logger.info(f"TOTAL PAGES: {len(doc)}")

    # ---------------- LOOP THROUGH PAGES ----------------
    for page_number, page in enumerate(doc):

        try:
            _logger.info(f"PROCESSING PAGE: {page_number + 1}")

            # -------- TEXT --------
            text = page.get_text("text") or ""

            # -------- IMAGES --------
            image_list = []

            images = page.get_images(full=True)
            _logger.info(f"FOUND {len(images)} IMAGES ON PAGE {page_number + 1}")

            for img_index, img in enumerate(images):
                try:
                    xref = img[0]
                    base_image = doc.extract_image(xref)

                    image_bytes = base_image.get("image")

                    if not image_bytes:
                        continue

                    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

                    # ✅ CORRECT: append each image separately
                    image_list.append(image_base64)

                except Exception as e:
                    _logger.warning(f"IMAGE EXTRACTION FAILED ON PAGE {page_number + 1}, INDEX {img_index}")
                    continue

            pages_data.append({
                "page": page_number + 1,
                "text": text,
                "images": image_list
            })

        except Exception as e:
            _logger.exception(f"FAILED PAGE {page_number + 1}")
            continue

    _logger.info(f"EXTRACTION COMPLETE → TOTAL PAGES PROCESSED: {len(pages_data)}")

    return jsonify(pages_data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)