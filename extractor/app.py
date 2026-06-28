from flask import Flask, request, jsonify
import logging
import os

from extract_pdf import extract_pdf
from recovery import recover_page

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

# ================= HOME =================
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

        result = extract_pdf(file)

        return jsonify(result)

    except Exception as e:

        _logger.exception(

            "[PDF EXTRACTION FAILED]"
        )

        return jsonify({

            "error": str(e)

        }), 500

# ================= RECOVERY =================
@app.route("/recover_page", methods=["POST"])
def recover():

     return recover_page()

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