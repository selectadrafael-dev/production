from odoo import http
from odoo.http import request
import base64
import json
import logging
import hashlib   # ✅ NEW

_logger = logging.getLogger(__name__)


class VendorDataController(http.Controller):

    @http.route('/vendor-data/submit', type='http', auth='public', website=True, csrf=False)
    def submit_vendor_data(self, **post):

        try:

            _logger.info("Vendor upload request received")

            url = post.get("data_url")
            extra_info = post.get("extra_info")

            pdf = request.httprequest.files.get("pdf_file")
            excel = request.httprequest.files.get("excel_file")
            logo = request.httprequest.files.get("logo_file")

            # =====================================================
            # 🔥 GENERATE SIGNATURE (NEW)
            # =====================================================
            file_content = b''

            if url:
                file_content = url.encode()

            elif excel:
                file_content = excel.read()

            elif pdf:
                file_content = pdf.read()

            else:
                return request.make_response(
                    json.dumps({"error": "No valid input provided"}),
                    headers=[('Content-Type', 'application/json')]
                )

            signature = hashlib.md5(file_content).hexdigest()

            # 🔥 RESET FILE POINTER (CRITICAL)
            if excel:
                excel.seek(0)
            if pdf:
                pdf.seek(0)

            # =====================================================
            # 🔥 DETERMINE INPUT TYPE (STRICT)
            # =====================================================
            job_vals = {
                'extra_info': extra_info,
                'upload_signature': signature,   # ✅ NEW
                'state': 'draft'
            }

            # ================= PRIORITY =================
            if url:
                job_vals['data_url'] = url
                job_vals['pdf_file'] = False
                job_vals['excel_file'] = False

                _logger.info("INPUT TYPE → URL")

            elif excel:
                job_vals['excel_file'] = base64.b64encode(excel.read())
                job_vals['pdf_file'] = False
                job_vals['data_url'] = False

                _logger.info("INPUT TYPE → EXCEL")

            elif pdf:
                job_vals['pdf_file'] = base64.b64encode(pdf.read())
                job_vals['excel_file'] = False
                job_vals['data_url'] = False

                _logger.info("INPUT TYPE → PDF")

            # ---------------- CREATE JOB ----------------
            job = request.env['vendor.import.job'].sudo().create(job_vals)

            # ---------------- OPTIONAL LOGO ----------------
            if logo:
                job.logo_file = base64.b64encode(logo.read())

            # 🔥 COMMIT FOR CRON VISIBILITY
            request.env.cr.commit()

            _logger.info(f"Job created: {job.id}")

            return request.make_response(
                json.dumps({
                    "success": True,
                    "message": "Upload successful. Processing in background."
                }),
                headers=[('Content-Type', 'application/json')]
            )

        except Exception as e:

            _logger.exception("Vendor upload failed")

            return request.make_response(
                json.dumps({
                    "error": "Upload failed due to server error"
                }),
                headers=[('Content-Type', 'application/json')]
            )