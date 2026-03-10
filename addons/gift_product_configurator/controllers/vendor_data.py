from odoo import http
from odoo.http import request
import base64
import re
import logging

_logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 10 * 1024 * 1024


class VendorDataController(http.Controller):

    @http.route('/vendor-data/submit', type='http', auth='public', website=True, csrf=False)
    def submit_vendor_data(self, **post):

        try:

            _logger.info("Vendor upload request received")

            url = post.get("data_url")

            pdf = request.httprequest.files.get("pdf_file")
            excel = request.httprequest.files.get("excel_file")
            logo = request.httprequest.files.get("logo_file")

            url_regex = r'^(https?:\/\/)[^\s$.?#].[^\s]*$'

            if url and not re.match(url_regex, url):
                return request.make_response(
                    '{"error": "Invalid URL provided."}',
                    headers=[('Content-Type', 'application/json')]
                )

            if pdf:

                _logger.info("PDF uploaded: %s", pdf.filename)

                if not pdf.filename.lower().endswith(".pdf"):
                    return request.make_response(
                        '{"error": "Only PDF files allowed."}',
                        headers=[('Content-Type', 'application/json')]
                    )

                pdf_data = pdf.read()

                if len(pdf_data) > MAX_FILE_SIZE:
                    return request.make_response(
                        '{"error": "PDF exceeds 10MB."}',
                        headers=[('Content-Type', 'application/json')]
                    )

            if excel:

                _logger.info("Excel uploaded: %s", excel.filename)

                if not excel.filename.lower().endswith((".xls",".xlsx",".csv")):
                    return request.make_response(
                        '{"error": "Only Excel/CSV allowed."}',
                        headers=[('Content-Type', 'application/json')]
                    )

            job = request.env['vendor.import.job'].sudo().create({
                'data_url': url,
                'extra_info': post.get("extra_info"),
                'state': 'draft'
            })

            _logger.info("Import job created ID=%s", job.id)

            if pdf:
                job.pdf_file = base64.b64encode(pdf_data)

            if excel:
                job.excel_file = base64.b64encode(excel.read())

            if logo:
                job.logo_file = base64.b64encode(logo.read())

            job.process_import()

            return request.make_response(
                '{"success": true, "message": "Upload successful. Processing started."}',
                headers=[('Content-Type', 'application/json')]
            )

        except Exception as e:

            _logger.exception("Vendor upload failed")

            return request.make_response(
                '{"error": "Server error occurred."}',
                headers=[('Content-Type', 'application/json')]
            )