from odoo import http
from odoo.http import request
import base64
import re

MAX_FILE_SIZE = 10 * 1024 * 1024

class VendorDataController(http.Controller):

    @http.route('/vendor-data/submit', type='http', auth='public', website=True)
    def submit_vendor_data(self, **post):

        url = post.get("data_url")

        pdf = post.get("pdf_file")
        excel = post.get("excel_file")
        logo = post.get("logo_file")

        url_regex = r'^(https?:\/\/)[^\s$.?#].[^\s]*$'

        if url and not re.match(url_regex, url):
            return request.redirect("/")

        if pdf:
            if not pdf.filename.lower().endswith(".pdf"):
                return request.redirect("/")
            if pdf.content_length > MAX_FILE_SIZE:
                return request.redirect("/")

        if excel:
            if not excel.filename.lower().endswith((".xls",".xlsx",".csv")):
                return request.redirect("/")
            if excel.content_length > MAX_FILE_SIZE:
                return request.redirect("/")

        if logo:
            if not logo.filename.lower().endswith((".png",".jpg",".jpeg",".svg")):
                return request.redirect("/")

        if not url and not pdf and not excel:
            return request.redirect("/")

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

        return request.redirect("/vendor-data-success")