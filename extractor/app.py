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

# LEGACY METHOD (currently unused)
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
                _logger.warning(

                    f"[EXTRACTOR REJECT AREA] "

                    f"area={area}"
                )
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

        # =====================================
        # PROFESSIONAL PAGE RENDER
        # =====================================

        pix = page.get_pixmap(

            matrix=fitz.Matrix(2, 2),

            alpha=False
        )

        img = Image.frombytes(

            "RGB",

            [pix.width, pix.height],

            pix.samples
        )

        img = img.convert("RGB")
        # =====================================
        # SAFE RESIZE
        # =====================================

        max_width = 1800

        if img.width > max_width:

            ratio = max_width / img.width

            img = img.resize(

                (

                    int(img.width * ratio),

                    int(img.height * ratio)
                ),

                Image.LANCZOS
            )

        # =====================================
        # PAGE DEBUG
        # =====================================

        _logger.warning(

            f"[PDF IMAGE READY] "

            f"page={page_number + 1} "

            f"width={img.width} "

            f"height={img.height}"
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

            242,

            255,

            cv2.THRESH_BINARY_INV

        )[1]

        kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (3, 3)
        )

        thresh = cv2.morphologyEx(
            thresh,
            cv2.MORPH_CLOSE,
            kernel,
            iterations=1
        )

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

            _logger.warning(

                f"[EXTRACTOR CONTOUR] "

                f"x={x} y={y} "

                f"w={w} h={h}"
            )

            # skip tiny areas

            if w < 90 or h < 90:

                _logger.warning(

                    f"[EXTRACTOR REJECT SMALL] "

                    f"w={w} h={h}"
                )

                continue

            # skip full-page blocks
            if w > page_np.shape[1] * 0.995:

                _logger.warning(

                    f"[EXTRACTOR REJECT FULLWIDTH] "

                    f"w={w}"
                )

                continue

           
            if h > page_np.shape[0] * 0.995:

                _logger.warning(

                    f"[EXTRACTOR REJECT FULLHEIGHT] "

                    f"h={h}"
                )

                continue

            crop = page_np[
                y:y+h,
                x:x+w
            ]

            # =================================
            # SMART TEXT FILTER
            # =================================

            crop_gray = cv2.cvtColor(

                crop,

                cv2.COLOR_RGB2GRAY
            )

            dark_pixels = np.mean(
                crop_gray < 55
            )

            pixel_std = np.std(crop_gray)

            # =================================
            # REJECT TRUE TEXT BLOCKS ONLY
            # =================================

            if (

                dark_pixels > 0.72

                and

                pixel_std < 18
            ):

                _logger.warning(

                    f"[EXTRACTOR REJECT TEXT] "

                    f"dark={dark_pixels:.2f} "

                    f"std={pixel_std:.2f}"
                )

                continue

            # =================================
            # HUMAN FILTER
            # =================================

            aspect_ratio = h / float(w)

            # portrait human-like layout

            if aspect_ratio > 2.4 and w < 180:

                _logger.warning(

                    f"[EXTRACTOR REJECT HUMAN] "

                    f"aspect={aspect_ratio:.2f} "

                    f"w={w} h={h}"
                )

                continue

            score = (w * h)

            # =================================
            # CLEAN PRODUCT BONUS
            # =================================

            white_ratio = np.mean(
                crop_gray > 235
            )

            # ecommerce-like isolated product
            if white_ratio > 0.42:

                score *= 1.55

                _logger.warning(
                    f"[CLEAN PRODUCT BONUS] "
                    f"white_ratio={white_ratio:.2f}"
                )

            # lifestyle/noisy backgrounds
            elif white_ratio < 0.10:

                score *= 0.65

                _logger.warning(
                    f"[NOISY BACKGROUND PENALTY] "
                    f"white_ratio={white_ratio:.2f}"
                )

            # =================================
            # TEXT/BANNER PENALTY
            # =================================

            gray_crop = cv2.cvtColor(

                crop,

                cv2.COLOR_RGB2GRAY
            )

            edges = cv2.Canny(

                gray_crop,

                80,

                180
            )

            edge_ratio = np.mean(
                edges > 0
            )

            # =================================
            # TEXT-LIKE STRUCTURE DETECTION
            # =================================

            text_penalty = False

            # high edge density usually text-heavy
            if edge_ratio > 0.18:
                text_penalty = True

            # brochure/document layout
            vertical_ratio = h / float(w)

            if (
                vertical_ratio > 1.15
                and
                edge_ratio > 0.12
            ):
                text_penalty = True

            # excessive text-like darkness
            dark_ratio = np.mean(gray_crop < 90)

            if (
                dark_ratio > 0.35
                and
                edge_ratio > 0.12
            ):
                text_penalty = True

            if text_penalty:

                score *= 0.18

                _logger.warning(
                    f"[TEXT PANEL PENALTY] "
                    f"edge={edge_ratio:.3f} "
                    f"dark={dark_ratio:.3f}"
                )

                # =================================
                # EXTREME TEXT PANEL PENALTY
                # =================================

                try:

                    vertical_ratio = h / float(w)

                    # very tall brochure-like panels
                    if (

                        vertical_ratio > 1.35

                        and

                        edge_ratio > 0.14
                    ):

                        score *= 0.12

                        _logger.warning(

                            f"[EXTREME TEXT PANEL] "

                            f"ratio={vertical_ratio:.2f} "

                            f"edge={edge_ratio:.3f}"
                        )

                except Exception as e:

                    _logger.warning(

                        f"[TEXT PANEL CHECK FAILED] "

                        f"{str(e)}"
                    )

                _logger.warning(

                    f"[TEXT BANNER PENALTY] "

                    f"edge_ratio={edge_ratio:.3f}"
                )

            # =================================
            # PRODUCT SHAPE BONUS
            # =================================

            ratio = w / float(h)

            if 0.35 <= ratio <= 2.8:
                score *= 1.25

            # =================================
            # CENTER BONUS
            # =================================

            center_x = x + (w / 2)

            page_center = page_np.shape[1] / 2

            distance = abs(
                center_x - page_center
            )

            center_factor = 1 - (
                distance / page_center
            )

            score *= (
                1 + (center_factor * 0.18)
            )

            candidate_images.append({

                "crop": crop,

                "score": score
            })


        # ===============================
        # SORT BEST FIRST
        # ===============================

        candidate_images = sorted(

            candidate_images,

            key=lambda x: x["score"],

            reverse=True
        )

        MAX_IMAGES_PER_PAGE = 12

        image_list = []

        for item in candidate_images[
            :MAX_IMAGES_PER_PAGE
        ]:
        

            try:


                crop = item["crop"]

                # =================================
                # SMART BORDER TRIM
                # =================================

                try:

                    crop_gray = cv2.cvtColor(

                        crop,

                        cv2.COLOR_RGB2GRAY
                    )

                    thresh_crop = cv2.threshold(

                        crop_gray,

                        245,

                        255,

                        cv2.THRESH_BINARY_INV

                    )[1]

                    trim_contours, _ = cv2.findContours(

                        thresh_crop,

                        cv2.RETR_EXTERNAL,

                        cv2.CHAIN_APPROX_SIMPLE
                    )

                    if trim_contours:

                        largest = max(

                            trim_contours,

                            key=cv2.contourArea
                        )

                        tx, ty, tw, th = cv2.boundingRect(
                            largest
                        )

                        # avoid tiny accidental trims
                        if tw > 80 and th > 80:

                            crop = crop[
                                ty:ty+th,
                                tx:tx+tw
                            ]

                            _logger.warning(

                                f"[SMART TRIM APPLIED] "

                                f"w={tw} h={th}"
                            )

                except Exception as e:

                    _logger.warning(

                        f"[SMART TRIM FAILED] "

                        f"{str(e)}"
                    )

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

                # reject fallback if page is mostly text
                fallback_gray = np.array(
                    fallback_img.convert("L")
                )

                fallback_edges = cv2.Canny(
                    fallback_gray,
                    80,
                    180
                )

                fallback_edge_ratio = np.mean(
                    fallback_edges > 0
                )

                if fallback_edge_ratio > 0.22:

                    _logger.warning(
                        "[FALLBACK REJECTED] "
                        "TEXT-HEAVY PAGE"
                    )

                    continue

                image_list.append(
                    image_base64
                )

                
                _logger.warning(

                    f"[EXTRACTOR IMAGE] "

                    f"page={page_number + 1} "

                    f"w={crop_img.width} "

                    f"h={crop_img.height}"
                )

            except Exception:
                continue


        # =====================================
        # FALLBACK FULL PAGE IMAGE
        # =====================================

        if not image_list:

            try:

                fallback_img = img.copy()

                fallback_img.thumbnail((1200, 1200))

                fallback_buffer = io.BytesIO()

                fallback_img.save(

                    fallback_buffer,

                    format="JPEG",

                    quality=80
                )

                fallback_base64 = base64.b64encode(

                    fallback_buffer.getvalue()

                ).decode("utf-8")

                image_list.append(
                    fallback_base64
                )

                _logger.warning(

                    f"[EXTRACTOR FALLBACK USED] "

                    f"page={page_number + 1} "

                    f"| NO CROPS DETECTED"
                )

                _logger.warning(

                    f"[EXTRACTOR FALLBACK PAGE] "

                    f"page={page_number + 1}"
                )

            except Exception as e:

                _logger.warning(

                    f"[EXTRACTOR FALLBACK FAILED] "

                    f"{str(e)}"
                )
        
        # 🔒 limit text
        text = text[:2000]

        _logger.warning(

            f"PAGE {page_number+1} "

            f"→ SEGMENTS: {len(candidate_images)} "

            f"| KEPT: {len(image_list)}"
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
                p["images"] = p["images"][:10]

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