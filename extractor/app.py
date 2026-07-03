from flask import Flask, request, jsonify
import logging
import os

# from extract_pdf import extract_pdf
# from recovery import recover_page
from extractor_dispatcher import extract_pdf
from recovery_dispatcher import dispatch
from recovery_v2 import recovery_v2

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

    if "file" not in request.files:

        return jsonify({

            "error": "No file uploaded"

        }), 400


    file = request.files["file"]

    try:

        return extract_pdf(file)

        # result = extract_pdf(file)
        # return jsonify(result)

    except Exception as e:

        _logger.exception(

            "[PDF EXTRACTION FAILED]"
        )

        return jsonify({

            "error": str(e)

        }), 500

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