from odoo import http
from odoo.http import request
import base64
import json
import logging

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

            # ---------------- CREATE JOB ----------------
            job = request.env['vendor.import.job'].sudo().create({
                'data_url': url,
                'extra_info': extra_info,
                'state': 'draft'
            })

            # 🔥 SAFE BACKGROUND EXECUTION
            request.env.cr.commit()  # ensure record saved

            request.env['vendor.import.job'].sudo().browse(job.id)._process_async()

            _logger.info(f"Job created: {job.id}")

            # ---------------- FILE HANDLING ----------------
            if pdf:
                job.pdf_file = base64.b64encode(pdf.read())

            if excel:
                job.excel_file = base64.b64encode(excel.read())

            if logo:
                job.logo_file = base64.b64encode(logo.read())

            # 🚫 DO NOT PROCESS HERE (CRITICAL)
            # job.process_import()  ← NEVER CALL THIS

            # ---------------- FAST RESPONSE ----------------
            return request.make_response(
                json.dumps({
                    "success": True,
                    "message": "Upload successful. Processing in background. This may take 2-5 mins depending on the file size."
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