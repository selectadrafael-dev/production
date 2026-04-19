from odoo import http
from odoo.http import request
import base64
import json
import logging
import hashlib

_logger = logging.getLogger(__name__)


class VendorDataController(http.Controller):

    @http.route('/vendor-data/submit', type='http', auth='public', website=True, csrf=False)
    def submit_vendor_data(self, **post):

        try:
            _logger.warning("🚀 CONTROLLER HIT")

            # 🔥 GET CURRENT USER → VENDOR
            user = request.env.user
            partner_id = user.partner_id.id if user else False

            if not partner_id:
                raise Exception("Vendor not identified")

            url = post.get("data_url")
            extra_info = post.get("extra_info")

            pdf = request.httprequest.files.get("pdf_file")
            excel = request.httprequest.files.get("excel_file")
            logo = request.httprequest.files.get("logo_file")

            # =====================================================
            # 🔥 SAFE FILE READ
            # =====================================================
            file_content = b''
            excel_base64 = False
            pdf_base64 = False

            if url:
                file_content = url.encode()

            elif excel:
                file_content = excel.read()
                if not file_content:
                    raise Exception("Excel file is empty")
                excel_base64 = base64.b64encode(file_content)

            elif pdf:
                file_content = pdf.read()
                if not file_content:
                    raise Exception("PDF file is empty")
                pdf_base64 = base64.b64encode(file_content)

            else:
                return request.make_response(
                    json.dumps({"error": "No valid input provided"}),
                    headers=[('Content-Type', 'application/json')]
                )

            # =====================================================
            # 🔥 SIGNATURE
            # =====================================================
            signature = hashlib.md5(file_content).hexdigest()

            # =====================================================
            # 🔥 JOB VALUES (FIXED)
            # =====================================================
            job_vals = {
                'extra_info': extra_info,
                'upload_signature': signature,
                'state': 'draft',
                'partner_id': partner_id,   # 🔥 CRITICAL FIX
            }

            # =====================================================
            # 🔥 INPUT TYPE
            # =====================================================
            if url:
                job_vals['data_url'] = url
                job_vals['pdf_file'] = False
                job_vals['excel_file'] = False
                _logger.warning("INPUT TYPE → URL")

            elif excel:
                job_vals['excel_file'] = excel_base64
                job_vals['pdf_file'] = False
                job_vals['data_url'] = False
                _logger.warning("INPUT TYPE → EXCEL")

            elif pdf:
                job_vals['pdf_file'] = pdf_base64
                job_vals['excel_file'] = False
                job_vals['data_url'] = False
                _logger.warning("INPUT TYPE → PDF")

            # =====================================================
            # 🔥 CREATE JOB
            # =====================================================
            job = request.env['vendor.import.job'].sudo().create(job_vals)

            if not job:
                raise Exception("JOB CREATION FAILED")

            _logger.warning(f"✅ JOB CREATED → ID {job.id} (Vendor {partner_id})")

            # =====================================================
            # 🔥 OPTIONAL LOGO
            # =====================================================
            if logo:
                job.logo_file = base64.b64encode(logo.read())

            # =====================================================
            # 🔥 COMMIT
            # =====================================================
            request.env.cr.commit()

            _logger.warning("✅ CONTROLLER DONE")

            return request.make_response(
                json.dumps({
                    "success": True,
                    "message": "Upload successful. Processing in background."
                }),
                headers=[('Content-Type', 'application/json')]
            )

        except Exception as e:

            _logger.exception("❌ CONTROLLER FAILED")

            return request.make_response(
                json.dumps({
                    "error": str(e)
                }),
                headers=[('Content-Type', 'application/json')]
            )