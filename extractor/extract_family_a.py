import fitz
import base64
import logging
import os
from PIL import Image
import io
import gc  # 🔥 memory cleanup
import cv2
import numpy as np
from flask import request, jsonify
from product_region_splitter import product_region_splitter
from preview_generator import preview_generator
from debug_pipeline import pipeline_tracer


#app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

# ================= HOME =================
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

        _logger.warning(

            f"[CONTOUR COUNT] "

            f"{len(contours)}"

        )

        results = []

        for contour in contours:

            area = cv2.contourArea(contour)

            if area < 8000:
                continue

            x, y, w, h = cv2.boundingRect(contour)

            _logger.warning(

                f"[CONTOUR FOUND] "

                f"x={x} "

                f"y={y} "

                f"w={w} "

                f"h={h} "

                f"area={w*h}"

            )
           
            area = cv2.contourArea(
                contour
            )

            if area < 4500:

                _logger.warning(

                    f"[EXTRACTOR REJECT AREA] "

                    f"area={area}"
                )

                continue

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
def extract_pdf(

    file,

    preview=False

):

    _logger.info("PDF REQUEST RECEIVED")

    _logger.warning(
        f"[FAMILY A ENTRY] file={file}"
    )

    _logger.warning(
        f"[FAMILY A ENTRY] filename={getattr(file, 'filename', None)}"
    )

    _logger.warning(
        f"[FAMILY A CHECK] is_none={file is None}"
    )

    if file is None:

        return {
            "error": "No file uploaded this time"
        }
    #file = request.files["file"]
    # file is already passed in

    try:
        pdf_bytes = file.read()

        file.seek(0)

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

        # =====================================

        # STRUCTURED PDF TEXT EXTRACTION

        # =====================================

        raw_text = page.get_text("text") or ""

        blocks = page.get_text("blocks") or []


        # =====================================

        # STABLE READING ORDER

        # =====================================

        blocks = sorted(

            blocks,

            key=lambda b: (

                round(b[1] / 10) * 10,

                b[0]
            )

        )


        # =====================================

        # TITLE CANDIDATE STORAGE

        # =====================================

        title_candidates = []

        structured_lines = []

        for block in blocks:

            try:

                x0, y0, x1, y1, block_text, *_ = block

                if not block_text:
                    continue

                clean = block_text.strip()

                if not clean:
                    continue

                # =====================================

                # VERY LARGE PARAGRAPH PENALTY

                # =====================================

                long_text_penalty = 0

                if len(clean.split()) > 40:
                   
                    long_text_penalty = 6
                 
                elif len(clean.split()) > 25:

                    long_text_penalty = 3
                   

                # =====================================

                # BLOCK METRICS

                # =====================================

                block_height = y1 - y0

                # =====================================

                # POSITIONAL BONUS

                # =====================================

                position_bonus = 0

                page_height = page.rect.height

                relative_y = y0 / max(page_height, 1)

                # upper area

                if relative_y < 0.30:

                    position_bonus += 2

                # middle area

                elif relative_y < 0.72:

                    position_bonus += 1
           
                word_count = len(clean.split())

                text_length = len(clean)

                uppercase_ratio = (

                
                sum(1 for c in clean if c.isupper())

                / max(
                    sum(1 for c in clean if c.isalpha()),
                    1
                )
                

                )

                # =====================================

                # TITLE SCORING SYSTEM

                # =====================================

                title_score = position_bonus - long_text_penalty

                # larger typography

                if block_height >= 16:
                    title_score += 3

                # short title behavior

                if 1 <= word_count <= 6:
                    title_score += 3

                # =====================================
                # PRODUCT MODEL TITLE BOOST
                # =====================================

                import re

                if re.search(

                    r"\b\d+\s*(panel|pc|piece|inch|ml|oz)\b",

                    clean.lower()
                ):

                    title_score += 12

                # compact text

                if text_length <= 60:
                    title_score += 2

                # uppercase bonus

                if uppercase_ratio > 0.35:
                    title_score += 2

                # block height
                if 22 <= block_height <= 42:
                    title_score += 3


                # avoid sentences

                if clean.endswith("."):
                    title_score -= 3

                # avoid feature lines

                bad_patterns = [

                "cotton",
                "polyester",
                "closure",
                "features",
                "material",
                "fabric",
                "dimensions",
                "capacity",
                "size:",
                "weight",

                ]

                generic_bad_titles = [
                    "new",
                    "featured",
                    "collection",
                    "summer",
                    "winter",
                    "premium",
                    "eco",
                    "range",
                    "series",
                    "edition",
                    "sale",
                ]


                if any(
                p in clean.lower()
                for p in bad_patterns
                ):
                    title_score -= 4

                # =====================================

                # SPECIFICATION-LIKE LINES

                # =====================================

                digit_ratio = (

                sum(1 for c in clean if c.isdigit())

                / max(len(clean), 1)

                )

                if digit_ratio > 0.35:

                    title_score -= 5


                # =====================================

                # FINAL TITLE DETECTION

                # =====================================

                if clean.lower().strip() in generic_bad_titles:

                    title_score -= 6

                _logger.warning(
                    f"[TITLE SCORE] "

                    f"text={clean[:80]} "

                    f"| score={title_score} "

                    f"| height={block_height:.1f} "

                    f"| y={relative_y:.2f}"
                )

                if title_score >= 7:

                    title_candidates.append({

                        "text": clean,

                        "x0": x0,
                        "y0": y0,
                        "x1": x1,
                        "y1": y1,

                        "height": block_height,

                        "score": title_score
                    })
               

                else:

                    structured_lines.append(clean)
              
            except Exception:
                continue

        # =====================================

        # PROFESSIONAL TITLE FUSION

        # =====================================

        merged_titles = []

        used_indexes = set()

        for i, candidate in enumerate(title_candidates):

           
            if i in used_indexes:
                continue

            merged_text = candidate["text"]

            used_indexes.add(i)

            for j, other in enumerate(title_candidates):

                if j == i:
                    continue

                if j in used_indexes:
                    continue

                # =====================================
                # SAME HORIZONTAL ALIGNMENT
                # =====================================

                x_distance = abs(
                    candidate["x0"] - other["x0"]
                )

                # =====================================
                # VERTICAL PROXIMITY
                # =====================================

                vertical_gap = abs(
                    candidate["y1"] - other["y0"]
                )

                # =====================================
                # TYPOGRAPHY SIMILARITY
                # =====================================

                height_gap = abs(
                    candidate["height"]
                    - other["height"]
                )


                if (

                    x_distance < 80

                    and

 
                    vertical_gap < (
                        candidate["height"] * 1.15
                    )

                    and

                    abs(candidate["x1"] - other["x1"]) < 120

                    and

                    height_gap < 8

                    and

                    abs(candidate["score"] - other["score"]) <= 4
                ):


                    # =====================================

                    # DUPLICATE PREVENTION

                    # =====================================

                    if other["text"] in merged_text:
                        continue

                    merged_text += " " + other["text"]

                    used_indexes.add(j)

            merged_titles.append(merged_text)

            # =====================================

            # PUSH MERGED TITLES INTO STRUCTURE

            # =====================================

        for title in merged_titles:

           
            structured_lines.append(
                f"[TITLE_CANDIDATE] {title}"
            )

            _logger.warning(

                f"[PDF TITLE MERGED] "

                    f"{title}"
            )
            

        # =====================================

        # PRIORITIZE TITLE CANDIDATES

        # =====================================

        title_lines = [
            line

            for line in structured_lines

            if line.startswith("[TITLE_CANDIDATE]")

        ]

        other_lines = [

            line

            for line in structured_lines

            if not line.startswith("[TITLE_CANDIDATE]")

        ]

        structured_lines = title_lines + other_lines


        structured_text = "\n".join(
        structured_lines
        )

        # =====================================

        # FINAL PAGE TEXT

        # =====================================

        text = structured_text or raw_text


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

        if len(contours) <= 2:

            _logger.warning(

                "[EDGE SEGMENTATION MODE]"

            )

            edges = cv2.Canny(

                gray,

                50,

                150

            )

            edge_contours, _ = cv2.findContours(

                edges,

                cv2.RETR_EXTERNAL,

                cv2.CHAIN_APPROX_SIMPLE

            )

            _logger.warning(

                f"[EDGE CONTOUR COUNT] "

                f"{len(edge_contours)}"

            )

            if len(edge_contours) > len(contours):

                contours = edge_contours

                _logger.warning(

                    "[EDGE CONTOURS SELECTED]"

                )

        candidate_images = []
        _logger.warning(

            f"[CONTOUR COUNT] "

            f"{len(contours)}"

        )

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

                _logger.warning(

                    f"[CONTOUR FOUND] "

                    f"x={x} "

                    f"y={y} "

                    f"w={w} "

                    f"h={h} "

                    f"area={w*h}"

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

            aspect_ratio = h / float(max(w, 1))

            lifestyle_score = 0

            if w > 300 and h > 300:
                lifestyle_score += 1

            if h > w:
                lifestyle_score += 1

            if (w * h) > 120000:
                lifestyle_score += 1

            _logger.warning(
                f"[LIFESTYLE RAW] "
                f"w={w} "
                f"h={h} "
                f"area={w*h} "
                f"large_image={w > 300 and h > 300} "
                f"portrait={h > w} "
                f"large_area={(w*h) > 120000}"
            )

            # =====================================
            # LIFESTYLE DETECTION V2
            # =====================================

            portrait = (
                h > w
            )

            large_area = (
                (w * h) > 120000
            )

            is_lifestyle = (
                portrait
                and
                large_area
            )

            _logger.warning(
                f"[LIFESTYLE FINAL] "
                f"w={w} "
                f"h={h} "
                f"portrait={portrait} "
                f"large_area={large_area} "
                f"lifestyle={is_lifestyle}"
            )



            # portrait human-like layout

            if aspect_ratio > 2.4 and w < 180:

                _logger.warning(

                    f"[EXTRACTOR REJECT HUMAN] "

                    f"aspect={aspect_ratio:.2f} "

                    f"w={w} h={h}"
                )

                continue

            score = (w * h)

            # ==================================
            # PRODUCT SHAPE BONUS
            # ==================================

            ratio = w / float(h)

            if 0.35 <= ratio <= 2.8:
                score *= 1.25

            # ===================================
            # CENTER BONUS
            # ==================================

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

            _logger.warning(

                f"[RENDER CROP] "

                f"w={w} "

                f"h={h} "

                f"ratio={aspect_ratio:.2f} "

                f"lifestyle={is_lifestyle}"
            )


            _logger.warning(

                f"[RENDER CLASSIFY] "

                f"w={w} "

                f"h={h} "

                f"area={w*h} "

                f"ratio={aspect_ratio:.2f} "

                f"large_image={w > 300 and h > 300} "

                f"portrait={h > w} "

                f"large_area={(w*h) > 120000} "

                f"score={lifestyle_score} "

                f"lifestyle={is_lifestyle}"
            )

            _logger.warning(
                f"[CROP QUALITY] "
                f"x={x} "
                f"y={y} "
                f"w={w} "
                f"h={h} "
                f"area={w*h}"
            )


            candidate_images.append({

                "crop": crop,

                "score": score,

                "x": x,
                "y": y,

                "width": w,
                "height": h,

                "aspect_ratio": aspect_ratio,

                "is_lifestyle": is_lifestyle,

                # ==========================
                # DEBUG TO ODOO
                # ==========================

                "crop_area": w * h,

                "lifestyle_score": lifestyle_score,

                "large_image": (
                    w > 300
                    and
                    h > 300
                ),

                "portrait": (
                    h > w
                ),

                "large_area": (
                    (w * h) > 120000
                )
            })


        # ===============================
        # SORT BEST FIRST
        # ===============================
        _logger.warning(
            f"[EXTRACTOR TOTAL CANDIDATES] "
            f"{len(candidate_images)}"
        )

        for idx, item in enumerate(candidate_images):

            crop = item["crop"]

            _logger.warning(
                f"[EXTRACTOR RANK] "
                f"idx={idx} "
                f"score={item['score']} "
                f"w={crop.shape[1]} "
                f"h={crop.shape[0]}"
            )

        _logger.warning(
            "[TRACE] "
            f"CandidateImagesBeforeSort={len(candidate_images)}"
        )
            
        candidate_images = sorted(

            candidate_images,

            key=lambda x: x["score"],

            reverse=True
        )

        MAX_IMAGES_PER_PAGE = 20

        image_list = []

        # for item in candidate_images[
        #     :MAX_IMAGES_PER_PAGE
        # ]:

        for rank, item in enumerate(candidate_images[:MAX_IMAGES_PER_PAGE]):
        

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

               
                image_list.append({

                    "image": image_base64,

                    "score": item.get("score", 0),

                    "x": item.get("x", 0),
                    "y": item.get("y", 0),

                    "extractor_rank": rank,
                    
                    "extractor_score": item["score"],

                    "width": item.get("width", 0),
                    "height": item.get("height", 0),

                    "is_lifestyle": item.get(
                        "is_lifestyle",
                        False
                    ),

                    # =========================
                    # DEBUG
                    # =========================

                    "lifestyle_score": item.get(
                        "lifestyle_score",
                        0
                    ),

                    "large_image": item.get(
                        "large_image",
                        False
                    ),

                    "portrait": item.get(
                        "portrait",
                        False
                    ),

                    "large_area": item.get(
                        "large_area",
                        False
                    ),
                    "crop_area": item.get(
                        "crop_area",
                        0
                    ),
                })

                _logger.warning(
                    "[TRACE FINAL] "
                    f"ImagesNow={len(image_list)} "
                    f"x={item.get('x')} "
                    f"y={item.get('y')} "
                    f"w={item.get('width')} "
                    f"h={item.get('height')}"
                )

                if item.get("is_lifestyle"):

                    _logger.warning(
                        "[RENDER LIFESTYLE SENT]"
                    )

                
                _logger.warning(

                    f"[EXTRACTOR IMAGE] "

                    f"page={page_number + 1} "

                    f"w={crop_img.width} "

                    f"h={crop_img.height}"
                )

            except Exception:
                continue


        # ======================================
        # FALLBACK FULL PAGE IMAGE
        # ======================================

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


                    image_list.append({

                        "image": fallback_base64,

                        "score": 0,

                        "x": 0,
                        "y": 0,

                        "width": fallback_img.width,
                        "height": fallback_img.height,

                        "is_lifestyle": False
                    })

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
        
        # 🔒 ======limit text=======
        text = text[:3500]

        _logger.warning(

            f"PAGE {page_number+1} "

            f"→ SEGMENTS: {len(candidate_images)} "

            f"| KEPT: {len(image_list)}"
        )

        if image_list:

            sample = image_list[0]

            _logger.warning(

                f"[RENDER IMAGE SAMPLE] "

                f"keys={list(sample.keys())}"

            )

            _logger.warning(

                f"[RENDER IMAGE DATA] "

                f"width={sample.get('width')} "

                f"height={sample.get('height')} "

                f"lifestyle={sample.get('is_lifestyle')}"
            )

        page_buffer = io.BytesIO()

        img.save(
            page_buffer,
            format="JPEG",
            quality=85
        )

        _logger.warning(

            f"[PAGE COMPLETE] "

            f"page={page_number+1} "

            f"products={len(image_list)}"

        )

        page_base64 = base64.b64encode(
            page_buffer.getvalue()
        ).decode("utf-8")

        _logger.warning(

            f"[PAGE IMAGE] "

            f"size={len(page_base64)}"

        )

        pages_data.append({

            "page": page_number + 1,

            "text": text,

            "page_image": page_base64,

            "page_image_size": len(page_base64),

            "page_width": img.width,

            "page_height": img.height,

            "images": image_list
        })

        # ======================================
        # FAMILY A DEBUG SUMMARY
        # ======================================

        _logger.warning(
            "========== FAMILY A SUMMARY =========="
        )

        _logger.warning(
            f"Pages Extracted: {len(pages_data)}"
        )

        for page in pages_data:

            _logger.warning(

                f"[PAGE {page['page']}] "

                f"Images={len(page['images'])} "

                f"PageSize={page['page_width']}x{page['page_height']}"

            )

            for index, image in enumerate(page["images"]):

                _logger.warning(

                    f"   Crop {index+1}: "

                    f"{image.get('width')}x{image.get('height')} "

                    f"Lifestyle={image.get('is_lifestyle')}"

                )

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