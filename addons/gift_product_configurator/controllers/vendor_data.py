from odoo import http
from odoo.http import request
import base64
import re

MAX_FILE_SIZE = 10 * 1024 * 1024


class VendorDataController(http.Controller):

    @http.route('/vendor-data/submit', type='json', auth='public', website=True, csrf=False)
    def submit_vendor_data(self, **post):

        url = post.get("data_url")

        pdf = request.httprequest.files.get("pdf_file")
        excel = request.httprequest.files.get("excel_file")
        logo = request.httprequest.files.get("logo_file")

        url_regex = r'^(https?:\/\/)[^\s$.?#].[^\s]*$'

        if url and not re.match(url_regex, url):
            return {"error": "Invalid URL provided."}

        if pdf:
            if not pdf.filename.lower().endswith(".pdf"):
                return {"error": "Only PDF files allowed."}

            if len(pdf.read()) > MAX_FILE_SIZE:
                return {"error": "PDF exceeds 10MB."}

            pdf.seek(0)

        if excel:
            if not excel.filename.lower().endswith((".xls",".xlsx",".csv")):
                return {"error": "Only Excel/CSV allowed."}

        job = request.env['vendor.import.job'].sudo().create({
            'data_url': url,
            'extra_info': post.get("extra_info"),
            'state': 'draft'
        })

        if pdf:
            job.pdf_file = base64.b64encode(pdf.read())

        if excel:
            job.excel_file = base64.b64encode(excel.read())

        if logo:
            job.logo_file = base64.b64encode(logo.read())

        job.process_import()

        return {
            "success": True,
            "message": "Upload successful. Your catalog is being processed."
        }