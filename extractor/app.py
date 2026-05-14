from flask import Flask, request, jsonify
import fitz
import base64
import logging
import os
from PIL import Image
import io
import gc  # 🔥 memory cleanup
import cv2
import numpy as np

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


# ================= HOME =================
@app.route('/')
def home():
    return "OK"


def split_catalog_image(pil_image):

    try:

        import cv2
        import numpy as np

        image = np.array(pil_image)

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_RGB2GRAY
        )

        thresh = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            21,
            5
        )

        kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (5, 5)
        )

        thresh = cv2.morphologyEx(
            thresh,
            cv2.MORPH_CLOSE,
            kernel,
            iterations=1
        )

        contours, _ = cv2.findContours(
            thresh,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        results = []

        for contour in contours:

            area = cv2.contourArea(contour)

            if area < 8000:
                continue

            x, y, w, h = cv2.boundingRect(contour)

            if w < 120 or h < 120:
                continue

            ratio = w / float(h)

            if ratio > 4.5 or ratio < 0.22:
                continue

            crop = image[
                y:y+h,
                x:x+w
            ]

            crop_pil = Image.fromarray(crop)

            buffer = io.BytesIO()

            crop_pil.save(
                buffer,
                format="JPEG",
                quality=75
            )

            results.append(
                base64.b64encode(
                    buffer.getvalue()
                ).decode("utf-8")
            )

        return results[:12]

    except Exception:

        return []
    

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

    pix = page.get_pixmap(
        matrix=fitz.Matrix(2, 2)
    )

    img = Image.frombytes(

        "RGB",

        [pix.width, pix.height],

        pix.samples
    )

    page_np = np.array(img)

    gray = cv2.cvtColor(
        page_np,
        cv2.COLOR_RGB2GRAY
    )

    # ===============================
    # THRESHOLD
    # ===============================

    thresh = cv2.threshold(

        gray,

        240,

        255,

        cv2.THRESH_BINARY_INV

    )[1]

    # ===============================
    # FIND CONTOURS
    # ===============================

    contours, _ = cv2.findContours(

        thresh,

        cv2.RETR_EXTERNAL,

        cv2.CHAIN_APPROX_SIMPLE
    )

    candidate_images = []

    # ===============================
    # EXTRACT CROPS
    # ===============================

    for contour in contours:

        x, y, w, h = cv2.boundingRect(
            contour
        )

        # skip tiny areas
        if w < 180 or h < 180:
            continue

        # skip full-page blocks
        if w > page_np.shape[1] * 0.95:
            continue

        if h > page_np.shape[0] * 0.95:
            continue

        crop = page_np[
            y:y+h,
            x:x+w
        ]

        # =================================
        # TEXT FILTER
        # =================================

        text_ratio = np.mean(

            crop < 80
        )

        if text_ratio > 0.45:
            continue

        # =================================
        # HUMAN FILTER
        # =================================

        aspect_ratio = h / float(w)

        # portrait human-like layout
        if aspect_ratio > 1.7 and w < 400:
            continue

        candidate_images.append({

            "crop": crop,

            "score": (w * h)
        })

    # ===============================
    # SORT BEST FIRST
    # ===============================

    candidate_images = sorted(

        candidate_images,

        key=lambda x: x["score"],

        reverse=True
    )

    MAX_IMAGES_PER_PAGE = 10

    image_list = []

    for item in candidate_images[
        :MAX_IMAGES_PER_PAGE
    ]:

        try:

            crop = item["crop"]

            crop_img = Image.fromarray(
                crop
            ).convert("RGB")

            crop_img.thumbnail((800, 800))

            buffer = io.BytesIO()

            crop_img.save(

                buffer,

                format="JPEG",

                quality=85
            )

            image_base64 = base64.b64encode(

                buffer.getvalue()

            ).decode("utf-8")

            image_list.append(
                image_base64
            )

        except Exception:
            continue

        # 🔒 limit text
        text = text[:2000]

        f"PAGE {page_number+1} → SEGMENTS: {len(candidate_images)} | KEPT: {len(image_list)}"
        
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