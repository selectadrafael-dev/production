(function () {
'use strict';

document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("vendorDataForm");
    if (!form) return;

    const successBox = document.getElementById("vendorSuccessBox");
    const errorBox = document.getElementById("vendorErrorBox");

    const progressWrapper = document.getElementById("uploadProgressWrapper");
    const progressBar = document.getElementById("uploadProgressBar");
    const percentText = document.getElementById("uploadPercentText");

    const MAX_SIZE = 100 * 1024 * 1024; //max 100b upload allowed 

    function showError(message) {

        console.error("Upload error:", message);

        if (successBox) successBox.classList.add("d-none");

        if (errorBox) {
            errorBox.classList.remove("d-none");
            errorBox.innerText = message;
        }

        scrollModalTop();
    }

    function showSuccess(message) {

        console.log("Upload success:", message);

        if (errorBox) errorBox.classList.add("d-none");

        if (successBox) {
            successBox.classList.remove("d-none");
            successBox.innerText = message;
        }

        scrollModalTop();

        setTimeout(() => {

            if (progressWrapper) progressWrapper.classList.add("d-none");

            if (progressBar) progressBar.style.width = "0%";

            if (percentText) percentText.innerText = "0%";

            if (successBox) successBox.classList.add("d-none");

        }, 5000);
    }

    function clearMessages() {

        if (successBox) successBox.classList.add("d-none");
        if (errorBox) errorBox.classList.add("d-none");
    }

    //auto scroll to the to of modal
   function scrollModalTop() {

        setTimeout(() => {

            const modal = document.getElementById("vendorDataModal");
            const modalBody = modal ? modal.querySelector(".modal-body") : null;

            if (modalBody) {
                modalBody.scrollTo({
                    top: 0,
                    behavior: "smooth"
                });
            } else if (modal) {
                modal.scrollTo({
                    top: 0,
                    behavior: "smooth"
                });
            }

        }, 150); // delay ensures DOM update first
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

                showError("PDF file exceeds 100MB limit.");
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

                showError("Excel/CSV exceeds 100MB limit.");
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
            const submitBtn = form.querySelector("button[type='submit']");
            if (submitBtn) submitBtn.disabled = true;// disbale submit button untill process complete
        
        scrollModalTop();// autoscrolling to top

        const formData = new FormData(form);

        if (progressWrapper) progressWrapper.classList.remove("d-none");

        if (progressBar) progressBar.style.width = "5%";

        if (percentText) percentText.innerText = "5%";

        const xhr = new XMLHttpRequest();

        xhr.open("POST", "/vendor-data/submit", true);

        xhr.upload.onprogress = function (event) {

            if (event.lengthComputable && progressBar) {

                let percent = Math.round((event.loaded / event.total) * 100);

                progressBar.style.width = percent + "%";

                if (percentText) percentText.innerText = percent + "%";
            }
        };

        xhr.onload = function () {

            console.log("XHR STATUS:", xhr.status);
            console.log("RAW RESPONSE:", xhr.responseText);

            if (xhr.status === 200) {

                try {

                    const data = JSON.parse(xhr.responseText);

                    console.log("Parsed response:", data);

                    if (data.error) {

                        showError(data.error);
                        return;
                    }

                    if (progressBar) progressBar.style.width = "100%";
                    if (percentText) percentText.innerText = "100%";

                    showSuccess(data.message || "Upload successful. Your catalog is being processed. This may take a few minutes.");

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

/*vendor portal*/
let vendorCurrentPage = 1;

async function loadVendorProducts(page = 1) {

    try {

        const result = await fetch('/vendor/products', {

            method: 'POST',

            headers: {
                'Content-Type': 'application/json',
            },

            body: JSON.stringify({
                page: page,
                limit: 50,
            })

        });

        const data = await result.json();

        const grid = document.getElementById(
            'vendorProductsGrid'
        );

        grid.innerHTML = '';

        data.result.products.forEach(product => {

            grid.innerHTML += `

                <div class="col-xl-3 col-lg-4 col-md-6">

                    <div class="vendor-product-card">

                        <div class="vendor-product-image-wrap">

                            <img
                                src="${product.image}"
                                class="vendor-product-image"
                            >

                        </div>

                        <div class="vendor-product-content">

                            <h6 class="vendor-product-title">
                                ${product.name}
                            </h6>

                            <button
                                class="btn btn-dark w-100 manage-product-btn"
                                data-product-id="${product.id}"
                            >
                                Manage Product
                            </button>

                        </div>

                    </div>

                </div>

            `;
        });

        if (!data.result.products.length) {

            grid.innerHTML = `

                <div class="col-12">

                    <div class="alert alert-light text-center">

                        No products found

                    </div>

                </div>
            `;

            return;
        }

        document.getElementById(
            'vendorPageInfo'
        ).innerText = `Page ${data.result.page}`;

        document.getElementById(
            'vendorPrevPage'
        ).disabled = !data.result.has_prev;

        document.getElementById(
            'vendorNextPage'
        ).disabled = !data.result.has_next;

        vendorCurrentPage = data.result.page;

    } catch (err) {

        console.error(
            'Vendor products load failed',
            err
        );
    }
}

const vendorModal = document.getElementById(
    'vendorProductsModal'
);

vendorModal.addEventListener(
    'shown.bs.modal',
    function () {

        loadVendorProducts(1);
    }
);

/**pagination */
document
.getElementById('vendorNextPage')
.addEventListener('click', function () {

    loadVendorProducts(
        vendorCurrentPage + 1
    );
});


document
.getElementById('vendorPrevPage')
.addEventListener('click', function () {

    loadVendorProducts(
        vendorCurrentPage - 1
    );
});


})();