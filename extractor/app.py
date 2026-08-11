from flask import Flask, request, jsonify, send_file
import logging
import os

import base64
from io import BytesIO

from extractor_dispatcher import extract_pdf
from recovery_dispatcher import dispatch
from recovery_v2 import recovery_v2
import vision_test

from azure_layout import analyze_pdf
from azure_product_evidence import build_product_evidence

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

# ================= HOME ========================
@app.route("/")
def home():
    # return "OK"

    return jsonify({

        "status": "ok",

        "service": "catalog-extractor"

    })

# ================= PDF EXTRACT =================
@app.route("/extract", methods=["POST"])
def extract():

    _logger.warning("========== EXTRACT ==========")

    _logger.warning(f"Content-Type: {request.content_type}")

    _logger.warning(f"Request.files = {request.files}")

    _logger.warning(f"Request.form = {request.form}")

    _logger.warning(f"Request.headers = {dict(request.headers)}")

    if len(request.files) == 0:

        return jsonify({

            "error": "No file uploaded",

            "content_type": request.content_type,

            "files": list(request.files.keys()),

            "form": list(request.form.keys())

        }), 400

    file = next(iter(request.files.values()))


    try:

        return extract_pdf(file)

    except Exception as e:

        _logger.exception(

            "[PDF EXTRACTION FAILED]"
        )

        return jsonify({

            "error": str(e)

        }), 500

#===========Catalogue Route==============================
@app.route(

    "/preview_catalog",

    methods=["POST"]

)
def preview_catalog():

    _logger.warning("========== PREVIEW ==========")

    _logger.warning(f"FILES: {request.files}")

    _logger.warning(f"FORM : {request.form}")

    if len(request.files) == 0:

        return jsonify({

            "error": "No PDF uploaded yet",

            "files": list(request.files.keys()),

            "form": list(request.form.keys()),

            "content_type": request.content_type

        }), 400

    file = next(iter(request.files.values()))

    return extract_pdf(

        file,

        preview=True

    )

# ================= RECOVERY =================
# @app.route("/recover_page", methods=["POST"])
# def recover():

#      return recover_page()

@app.route("/recover_page", methods=["POST"])
def recover():

    return dispatch()

#=================RECOVERY 2===================
@app.route("/recover_page_v2", methods=["POST"])
def recover_v2():

    return recovery_v2.recover_page()

#=================RECOVERY V2 TEST====================

@app.route("/test_recovery_v2", methods=["POST"])

def test_recovery_v2():

    return recovery_v2.recover_page()


#=================CATALOG TEST====================

@app.route("/test_catalog", methods=["POST"])
def test_catalog():

    if "file" not in request.files:

        return jsonify({

            "success": False,

            "error": "No PDF uploaded"

        }), 400

    file = request.files["file"]

    return recovery_v2.process_catalog(file)

#=================VISION TEST====================

@app.route(

    "/test_vision",

    methods=["POST"]

)

def test_vision():

    if "file" not in request.files:

        return jsonify({

            "success": False,

            "error": "No PDF uploaded"

        }), 400

    file = request.files["file"]

    return vision_test.process_catalog(

        file
    )

# ================= AZURE LAYOUT EVIDENCE TEST =================

@app.route("/test_azure_layout", methods=["POST"])
def test_azure_layout():

    _logger.warning(
        "========== AZURE LAYOUT TEST =========="
    )

    if "file" not in request.files:

        return jsonify({
            "success": False,
            "error": "No PDF uploaded"
        }), 400

    file = request.files["file"]

    try:

        evidence = analyze_pdf(file)

        return jsonify({
            "success": True,
            "evidence": evidence
        })

    except Exception as e:

        _logger.exception(
            "[AZURE LAYOUT TEST FAILED]"
        )

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ==========================================================
# AZURE PRODUCT EVIDENCE TEST
# ==========================================================

@app.route(
    "/test_azure_product_evidence",
    methods=["POST"]
)
def test_azure_product_evidence():

    _logger.warning(
        "========== AZURE PRODUCT EVIDENCE TEST =========="
    )

    if "file" not in request.files:

        return jsonify({

            "success": False,

            "error":
                "No PDF uploaded"

        }), 400

    file = request.files["file"]

    try:

        # ==================================================
        # ONE AZURE ANALYSIS ONLY
        # ==================================================

        evidence = analyze_pdf(
            file
        )

        # ==================================================
        # BUILD SPATIAL PRODUCT EVIDENCE
        # ==================================================

        product_evidence = (
            build_product_evidence(
                evidence
            )
        )

        return jsonify({

            "success": True,

            "evidence":
                product_evidence

        })

    except Exception as e:

        _logger.exception(
            "[AZURE PRODUCT EVIDENCE TEST FAILED]"
        )

        return jsonify({

            "success": False,

            "error":
                str(e)

        }), 500

#========== AZURE FIGURE TEST ==========
@app.route(
    "/test_azure_figure",
    methods=["POST"]
)
def test_azure_figure():

    _logger.warning(
        "========== AZURE FIGURE TEST =========="
    )

    if "file" not in request.files:

        return jsonify({

            "success": False,

            "error": "No PDF uploaded"

        }), 400

    figure_id = request.form.get(
        "figure_id"
    )

    if not figure_id:

        return jsonify({

            "success": False,

            "error": "figure_id is required"

        }), 400

    file = request.files["file"]

    try:

        evidence = analyze_pdf(
            file
        )

        figures = evidence.get(
            "figures",
            []
        )

        _logger.warning(
            "[AZURE FIGURE TEST] "
            "Figures detected: %s",
            len(figures)
        )

        target_figure = None

        for figure in figures:

            if str(
                figure.get("figure_id")
            ) == str(figure_id):

                target_figure = figure

                break

        if not target_figure:

            return jsonify({

                "success": False,

                "error":
                    f"Figure {figure_id} "
                    "was not found",

                "available_figures": [

                    figure.get(
                        "figure_id"
                    )

                    for figure in figures

                ]

            }), 404

        image_base64 = target_figure.get(
            "image_base64"
        )

        if not image_base64:

            return jsonify({

                "success": False,

                "error":
                    f"Figure {figure_id} "
                    "has no image data"

            }), 404

        image_bytes = base64.b64decode(
            image_base64
        )

        return send_file(

            BytesIO(image_bytes),

            mimetype="image/png",

            download_name=(
                "azure_figure_"
                f"{str(figure_id).replace('.', '_')}.png"
            )

        )

    except Exception as e:

        _logger.exception(
            "[AZURE FIGURE TEST FAILED]"
        )

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500

# ================= START APP =================
if __name__ == "__main__":

    port = int(

        os.environ.get(

            "PORT",

            5000
        )
    )

    app.run(

        host="0.0.0.0",

        port=port
    )