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
        console.log(
            'VENDOR PRODUCTS RESPONSE',
            data
        );


        // const grid = document.getElementById(
        //     'vendorProductsGrid'
        // );

        // grid.innerHTML = '';

        const grid = document.getElementById(
            'vendorProductsGrid'
        );

        console.log(
            'GRID ELEMENT',
            grid
        );


        if (!grid) {

            console.error(
                'vendorProductsGrid NOT FOUND'
            );

            return;
        }


        grid.innerHTML = '';
    


    data.products.forEach(product => {

            grid.innerHTML += `

                <div class="col-xl-3 col-lg-4 col-md-6">

                    <div class="vendor-product-card">

                        <div class="vendor-product-image-wrap">

                            <img src="${product.image}" class="vendor-product-image open-vendor-product" data-product-id="${product.id}" >

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

        
if (!data.products.length) {

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
        ).innerText = `Page ${data.page}`;

        document.getElementById(
            'vendorPrevPage'
        ).disabled = !data.has_prev;

        document.getElementById(
            'vendorNextPage'
        ).disabled = !data.has_next;

        vendorCurrentPage = data.page;

    } catch (err) {

        console.error(
            'Vendor products load failed',
            err
        );
    }
}


//product loader
document.addEventListener(

    'DOMContentLoaded',

    function () {

        const vendorModal = (
            document.getElementById(
                'vendorProductsModal'
            )
        );

        console.log(
            'vendor Product modal -> ',
            vendorModal
        );


        if (!vendorModal) {

            console.error(
                'vendorProductsModal NOT FOUND'
            );

            return;
        }
    }
);


const vendorStatusBtn = document.querySelector(
    '.vendor-data-status'
);


if (vendorStatusBtn) {

    vendorStatusBtn.addEventListener(

        'click',

        function () {

            console.log(
                'LOADING VENDOR PRODUCTS'
            );

            setTimeout(function () {

                loadVendorProducts(1);

            }, 300);
        }
    );
}


//next page/pagination
const vendorNextBtn = document.getElementById(
    'vendorNextPage'
);

if (vendorNextBtn) {

    vendorNextBtn.addEventListener(

        'click',

        function () {

            loadVendorProducts(
                vendorCurrentPage + 1
            );
        }
    );
}


// previous btn
const vendorPrevBtn = document.getElementById(
    'vendorPrevPage'
);

if (vendorPrevBtn) {

    vendorPrevBtn.addEventListener(

        'click',

        function () {

            loadVendorProducts(
                vendorCurrentPage - 1
            );
        }
    );
}


//vendor product form view
// =====================================================
// VENDOR PRODUCT DETAILS
// =====================================================

async function loadVendorProductDetails(productId) {

    try {

        const result = await fetch(

            '/vendor/product/details',

            {
                method: 'POST',

                headers: {
                    'Content-Type': 'application/json'
                },

                body: JSON.stringify({
                    product_id: productId
                })
            }
        );

        const data = await result.json();
        console.log(
            'VENDOR PRODUCTS RESPONSE',
            data
        );


        // =========================================
        // ERROR
        // =========================================

        if (
            data.result &&
            data.result.error
        ) {

            alert(data.result.error);

            return;
        }

        const product = data.result;

        // =========================================
        // FORM VALUES
        // =========================================

        const productIdField =
            document.getElementById(
                'vendorProductId'
            );

        if (productIdField) {

            productIdField.value =
                product.id || '';
        }


        const productNameField =
            document.getElementById(
                'vendorProductName'
            );

        if (productNameField) {

            productNameField.value =
                product.name || '';
        }


        const descriptionField =
            document.getElementById(
                'vendorProductDescription'
            );

        if (descriptionField) {

            descriptionField.value =
                product.description || '';
        }


        const categoryField =
            document.getElementById(
                'vendorProductCategory'
            );

        if (categoryField) {

            categoryField.value =
                product.category || '';
        }


        const priceField =
            document.getElementById(
                'vendorProductPrice'
            );

        if (priceField) {

            priceField.value =
                product.price || 0;
        }


        const statusField =
            document.getElementById(
                'vendorProductStatus'
            );

        if (statusField) {

            statusField.value = (

                product.published

                    ? 'Published'

                    : 'Unpublished'
            );
        }


        const dateField =
            document.getElementById(
                'vendorProductDate'
            );

        if (dateField) {

            dateField.value =
                product.create_date || '';
        }


        // =========================================
        // IMAGE
        // =========================================

        const imagePreview =
            document.getElementById(
                'vendorProductPreview'
            );

        if (imagePreview) {

            imagePreview.src =
                product.image || '';
        }


        // =========================================
        // WARNING
        // =========================================

        const warningBox =
            document.getElementById(
                'vendorProductWarning'
            );

        if (warningBox) {

            if (product.warning) {

                warningBox.classList.remove(
                    'd-none'
                );

                warningBox.innerHTML =
                    product.warning;

            } else {

                warningBox.classList.add(
                    'd-none'
                );
            }
        }


        // =========================================
        // OPEN MODAL
        // =========================================

        const modalElement =
            document.getElementById(
                'vendorProductDetailsModal'
            );

        if (!modalElement) {
            return;
        }

        const modal =
            new bootstrap.Modal(
                modalElement
            );

        modal.show();

    } catch (err) {

        console.error(

            'LOAD PRODUCT DETAILS FAILED',

            err
        );

        alert(
            'Failed to load product details'
        );
    }
}


// =====================================================
// OPEN PRODUCT DETAILS MODAL
// =====================================================

document.addEventListener(

    'click',

    function (e) {

        const trigger = e.target.closest(
            '.open-vendor-product'
        );

        if (!trigger) {
            return;
        }

        e.preventDefault();

        const productId =
            trigger.dataset.productId;

        if (!productId) {
            return;
        }

        loadVendorProductDetails(
            productId
        );
    }
);


// =====================================================
// SAVE PRODUCT
// =====================================================

const saveVendorBtn =
    document.getElementById(
        'saveVendorProductBtn'
    );

if (saveVendorBtn) {

    saveVendorBtn.addEventListener(

        'click',

        async function () {

            try {

                const payload = {

                    product_id:

                        document.getElementById(
                            'vendorProductId'
                        ).value,


                    name:

                        document.getElementById(
                            'vendorProductName'
                        ).value,


                    description:

                        document.getElementById(
                            'vendorProductDescription'
                        ).value,


                    price:

                        document.getElementById(
                            'vendorProductPrice'
                        ).value,
                };


                const response = await fetch(

                    '/vendor/product/update',

                    {
                        method: 'POST',

                        headers: {
                            'Content-Type':
                                'application/json'
                        },

                        body: JSON.stringify(
                            payload
                        )
                    }
                );


                const data =
                    await response.json();


                if (
                    data.result &&
                    data.result.error
                ) {

                    alert(
                        data.result.error
                    );

                    return;
                }


                // =================================
                // REFRESH PRODUCTS
                // =================================

                loadVendorProducts(
                    vendorCurrentPage
                );


                alert(
                    'Product updated successfully'
                );

            } catch (err) {

                console.error(

                    'SAVE PRODUCT FAILED',

                    err
                );

                alert(
                    'Failed to update product'
                );
            }
        }
    );
}


// =====================================================
// DELETE PRODUCT
// =====================================================

const deleteVendorBtn =
    document.getElementById(
        'deleteVendorProductBtn'
    );

if (deleteVendorBtn) {

    deleteVendorBtn.addEventListener(

        'click',

        async function () {

            try {

                const productId =
                    document.getElementById(
                        'vendorProductId'
                    ).value;


                const confirmed = confirm(

                    'Delete this product?'
                );

                if (!confirmed) {
                    return;
                }


                const response = await fetch(

                    '/vendor/product/delete',

                    {
                        method: 'POST',

                        headers: {
                            'Content-Type':
                                'application/json'
                        },

                        body: JSON.stringify({

                            product_id:
                                productId
                        })
                    }
                );


                const data =
                    await response.json();


                if (
                    data.result &&
                    data.result.error
                ) {

                    alert(
                        data.result.error
                    );

                    return;
                }


                // =================================
                // REFRESH PRODUCTS
                // =================================

                loadVendorProducts(
                    vendorCurrentPage
                );


                // =================================
                // CLOSE MODAL
                // =================================

                const modalElement =
                    document.getElementById(
                        'vendorProductDetailsModal'
                    );

                const modal =
                    bootstrap.Modal
                    .getInstance(
                        modalElement
                    );

                if (modal) {

                    modal.hide();
                }


                alert(
                    'Product deleted successfully'
                );

            } catch (err) {

                console.error(

                    'DELETE PRODUCT FAILED',

                    err
                );

                alert(
                    'Failed to delete product'
                );
            }
        }
    );
}

})();