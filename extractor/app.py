from flask import Flask, request, jsonify
import fitz
import base64
import logging
import os
from PIL import Image
import io
import gc  # 🔥 memory cleanup

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
    except Exception as e:
        _logger.error(f"INVALID PDF → {str(e)}")
        return jsonify({"error": "Invalid PDF"}), 400

    pages_data = []

    # 🔒 MUST remain 1 (Odoo sends one page)
    MAX_PAGES = 1

    for page_number, page in enumerate(doc):

        if page_number >= MAX_PAGES:
            break

        text = page.get_text("text") or ""
        image_list = []
        images = page.get_images(full=True)
        images = sorted(
                images,
                key=lambda x: x[2] * x[3] if len(x) > 3 else 0,
                reverse=True
            )

        MAX_IMAGES_PER_PAGE = 10

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
                width, height = img.size

                # skip tiny images (icons, logos)
                if width < 200 or height < 200:
                    continue

                # 🔒 reduce size
                img.thumbnail((800, 800))

                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=75)

                compressed_bytes = buffer.getvalue()

                # 🔒 skip large images
                # if len(compressed_bytes) > 500000:
                #     continue

                image_base64 = base64.b64encode(compressed_bytes).decode("utf-8")

                image_list.append(image_base64)

                # 🔥 free memory
                buffer.close()

            except Exception:
                continue

        # 🔒 limit text
        text = text[:2000]

        _logger.info(
                f"PAGE {page_number+1} → RAW IMAGES: {len(images)} | KEPT: {len(image_list)}"
        )
        pages_data.append({
            "page": page_number + 1,
            "text": text,
            "images": image_list
        })

    # 🔒 response size protection
    try:
        response_size = len(str(pages_data))
        _logger.info(f"RESPONSE SIZE → {response_size}")

        if response_size > 500000:
            _logger.warning("RESPONSE TOO LARGE → reducing images per page")

            for p in pages_data:
               p["images"] = p["images"][:6]  # keep at least some images

    except Exception:
        pass

    # 🔥 CLOSE DOC + CLEAN MEMORY
    try:
        doc.close()
        del doc
        gc.collect()
    except Exception:
        pass

    return jsonify({
        "pages": pages_data
    })


# ================= START APP =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)