from flask import Flask, request, jsonify
import fitz
import base64
import logging
import os
from PIL import Image
import io
#import requests  # ✅ FIXED (global import)

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


# ================= URL EXTRACT (PLAYWRIGHT) =================

@app.route("/extract-url", methods=["POST"])
def extract_url():

    from playwright.sync_api import sync_playwright
    import subprocess
    import requests
    import base64

    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "Missing URL"}), 400

    _logger.info(f"PLAYWRIGHT SCRAPE → {url}")

    products = []

    try:
        with sync_playwright() as p:

            # ================= BROWSER LAUNCH (SAFE) =================
            try:
                browser = p.chromium.launch(headless=True)
            except Exception as e:
                _logger.warning(f"PLAYWRIGHT BROWSER MISSING → INSTALLING NOW ({str(e)[:100]})")
                subprocess.run(["playwright", "install", "chromium"], check=True)
                browser = p.chromium.launch(headless=True)

            page = browser.new_page()

            # ================= LOAD PAGE =================
            page.goto(url, timeout=60000)
            page.wait_for_timeout(5000)

            # ================= HANDLE COOKIE =================
            try:
                page.locator("button:has-text('Accept')").click(timeout=3000)
            except:
                pass

            # ================= SCROLL =================
            for _ in range(5):
                page.mouse.wheel(0, 4000)
                page.wait_for_timeout(1500)

            # ================= SMART SELECTORS =================
            selectors = [
                ".product-item",
                ".product-card",
                ".product",
                ".item",
                "[class*='product']",
                "li"
            ]

            items = []

            for sel in selectors:
                found = page.query_selector_all(sel)
                if found:
                    items = found
                    _logger.info(f"SELECTOR HIT → {sel} ({len(found)})")
                    break

            _logger.info(f"TOTAL ITEMS FOUND → {len(items)}")

            # ================= EXTRACTION =================
            for item in items[:200]:

                try:
                    text = item.inner_text().strip()

                    if not text or len(text) < 10:
                        continue

                    img_el = item.query_selector("img")
                    if not img_el:
                        continue

                    img_url = img_el.get_attribute("src")
                    if not img_url:
                        continue

                    if img_url.startswith("//"):
                        img_url = "https:" + img_url

                    # ================= IMAGE FETCH =================
                    img_base64 = None

                    try:
                        res = requests.get(img_url, timeout=10)
                        if res.status_code == 200:
                            img_base64 = base64.b64encode(res.content).decode("utf-8")
                    except:
                        continue

                    if not img_base64:
                        continue

                    products.append({
                        "name": text[:120],
                        "image": img_base64
                    })

                except:
                    continue

            browser.close()

    except Exception as e:
        _logger.error(f"PLAYWRIGHT FAILED → {str(e)}")
        return jsonify({"error": str(e)}), 500

    # ================= FINAL CHECK =================
    if not products:
        _logger.warning("NO PRODUCTS EXTRACTED")
        return jsonify({"error": "No products found"}), 500

    _logger.info(f"PLAYWRIGHT DONE → {len(products)} PRODUCTS")

    pages = [{
        "page": 1,
        "text": "\n".join([p["name"] for p in products]),
        "images": [p["image"] for p in products if p["image"]]
    }]

    return jsonify(pages)

# ================= START APP =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)