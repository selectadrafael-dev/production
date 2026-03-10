(function () {
  'use strict';

    document.addEventListener("DOMContentLoaded", function () {

        const form = document.getElementById("vendorDataForm");

        if (!form) return;

        const errorBox = document.getElementById("vendorErrorBox");

        function showError(message) {
            errorBox.classList.remove("d-none");
            errorBox.innerText = message;
        }

        function clearError() {
            errorBox.classList.add("d-none");
            errorBox.innerText = "";
        }

        form.addEventListener("submit", function (e) {

            clearError();

            const urlInput = form.querySelector("input[name='data_url']");
            const pdfInput = form.querySelector("input[name='pdf_file']");
            const excelInput = form.querySelector("input[name='excel_file']");

            const url = urlInput.value.trim();
            const pdfFile = pdfInput.files[0];
            const excelFile = excelInput.files[0];

            const urlRegex = /^(https?:\/\/)[^\s$.?#].[^\s]*$/i;

            /* Validate URL */

            if (url && !urlRegex.test(url)) {
                e.preventDefault();
                showError("Please provide a valid URL starting with http:// or https://");
                return;
            }

            /* Validate PDF */

            if (pdfFile) {

                if (pdfFile.type !== "application/pdf") {
                    e.preventDefault();
                    showError("Only PDF files are allowed in the PDF field.");
                    pdfInput.value = "";
                    return;
                }

                if (pdfFile.size > 10 * 1024 * 1024) {
                    e.preventDefault();
                    showError("PDF file exceeds 10MB limit.");
                    return;
                }

            }

            /* Validate Excel */

            if (excelFile) {

                const allowedExcel = [
                    "application/vnd.ms-excel",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "text/csv"
                ];

                if (!allowedExcel.includes(excelFile.type)) {
                    e.preventDefault();
                    showError("Only Excel (.xls, .xlsx) or CSV files allowed.");
                    excelInput.value = "";
                    return;
                }

                if (excelFile.size > 10 * 1024 * 1024) {
                    e.preventDefault();
                    showError("Excel/CSV exceeds 10MB limit.");
                    return;
                }

            }

            /*Require at least one input*/

            if (!url && !pdfFile && !excelFile) {
                e.preventDefault();
                showError("Please provide a URL, PDF, or Excel file.");
            }

        });

    });

})();