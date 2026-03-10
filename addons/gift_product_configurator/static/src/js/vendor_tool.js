(function () {
'use strict';

document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("vendorDataForm");
    if (!form) return;

    const successBox = document.getElementById("vendorSuccessBox");
    const errorBox = document.getElementById("vendorErrorBox");

    const progressWrapper = document.getElementById("uploadProgressWrapper");
    const progressBar = document.getElementById("uploadProgressBar");

    const MAX_SIZE = 10 * 1024 * 1024;

    function showError(message) {
        console.error("Upload error:", message);

        successBox.classList.add("d-none");
        errorBox.classList.remove("d-none");
        errorBox.innerText = message;

        scrollModalTop();
    }

    function showSuccess(message) {
        console.log("Upload success:", message);

        errorBox.classList.add("d-none");
        successBox.classList.remove("d-none");
        successBox.innerText = message;

        scrollModalTop();
    }

    function clearMessages() {
        successBox.classList.add("d-none");
        errorBox.classList.add("d-none");
    }

    function scrollModalTop() {
        const modalBody = document.querySelector("#vendorDataModal .modal-body");
        if (modalBody) modalBody.scrollTop = 0;
    }

    function validateForm() {

        const urlInput = form.querySelector("input[name='data_url']");
        const pdfInput = form.querySelector("input[name='pdf_file']");
        const excelInput = form.querySelector("input[name='excel_file']");

        const url = urlInput.value.trim();
        const pdfFile = pdfInput.files[0];
        const excelFile = excelInput.files[0];

        const urlRegex = /^(https?:\/\/)[^\s$.?#].[^\s]*$/i;

        if (url && !urlRegex.test(url)) {
            showError("Please provide a valid URL starting with http:// or https://");
            return false;
        }

        if (pdfFile) {

            if (pdfFile.type !== "application/pdf") {
                showError("Only PDF files are allowed in the PDF field.");
                pdfInput.value = "";
                return false;
            }

            if (pdfFile.size > MAX_SIZE) {
                showError("PDF file exceeds 10MB limit.");
                return false;
            }

        }

        if (excelFile) {

            const allowedExcel = [
                "application/vnd.ms-excel",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "text/csv"
            ];

            if (!allowedExcel.includes(excelFile.type)) {
                showError("Only Excel (.xls, .xlsx) or CSV files allowed.");
                excelInput.value = "";
                return false;
            }

            if (excelFile.size > MAX_SIZE) {
                showError("Excel/CSV exceeds 10MB limit.");
                return false;
            }

        }

        if (!url && !pdfFile && !excelFile) {
            showError("Please provide a URL, PDF, or Excel file.");
            return false;
        }

        return true;
    }

    form.addEventListener("submit", function (e) {

        e.preventDefault();

        clearMessages();

        if (!validateForm()) return;

        const formData = new FormData(form);

        if (progressWrapper) progressWrapper.classList.remove("d-none");
        if (progressBar) progressBar.style.width = "10%";

        const xhr = new XMLHttpRequest();

        xhr.open("POST", "/vendor-data/submit", true);

        xhr.upload.onprogress = function (event) {

            if (event.lengthComputable && progressBar) {

                let percent = (event.loaded / event.total) * 100;

                progressBar.style.width = percent + "%";
            }
        };

        xhr.onload = function () {

            console.log("Upload response status:", xhr.status);
            console.log("Raw response:", xhr.responseText);

            if (xhr.status === 200) {

                try {

                    const data = JSON.parse(xhr.responseText);

                    console.log("Parsed response:", data);

                    if (data.error) {
                        showError(data.error);
                        return;
                    }

                    showSuccess(data.message || "Upload successful. Your catalog is being processed.");

                    if (progressBar) progressBar.style.width = "100%";

                    form.reset();

                } catch (err) {

                    console.error("JSON parse error:", err);
                    showError("Unexpected server response.");

                }

            } else {

                console.error("Server returned error status:", xhr.status);
                showError("Upload failed. Server returned error.");

            }

        };

        xhr.onerror = function () {

            console.error("Network error occurred");

            showError("Network error. Check browser console.");

        };

        xhr.send(formData);

    });

});

})();