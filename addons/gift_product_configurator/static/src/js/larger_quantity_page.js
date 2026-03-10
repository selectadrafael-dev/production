(function () {

"use strict";

/* =====================================================
PAGE DETECTION
===================================================== */

function isProductPage() {
    return document.querySelector(".qty_wrapper") !== null;
}

function isLargeQtyPage() {
    return document.querySelector(".qty-input") !== null;
}


/* =====================================================
STATE
===================================================== */

let lastQtySource = "tier";


/* =====================================================
UTILITIES
===================================================== */

function getSelectedQty() {

    if (lastQtySource === "manual") {

        const input = document.querySelector(".custom-qty input");

        if (input) {
            return parseInt(input.value, 10) || 1;
        }
    }

    const tier = document.querySelector(".tier-card.active strong");

    if (tier) {
        return parseInt(tier.innerText.replace("+", ""), 10);
    }

    return 1;
}

window.getSelectedQty = getSelectedQty;


/* =====================================================
TRACK ENTRY SOURCE
===================================================== */

function trackEntrySource(){

    /* ensure default value */

    if(!sessionStorage.getItem("quote_source")){
        sessionStorage.setItem("quote_source","single");
    }

    document.addEventListener("click", function(e){

        const quoteBtn = e.target.closest("#drawer-quote-btn");

        if(quoteBtn){

            sessionStorage.setItem("quote_source","drawer");

            window.location.href = "/larger-quantity";

            return;
        }

        const largerBtn = e.target.closest('a[href="/larger-quantity"]');

        if(largerBtn){

            sessionStorage.setItem("quote_source","single");

        }

    });

}

/* =====================================================
SCROLL TO TOP HELPER
===================================================== */

function scrollToTop(){

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });

}


/* =====================================================
PRODUCT PAGE LOGIC
===================================================== */

function initProductPage() {

    document.addEventListener("click", function (e) {

        /* TIER SELECTION */

        const tier = e.target.closest(".tier-card");

        if (tier) {

            document.querySelectorAll(".tier-card").forEach(el=>{
                el.classList.remove("active");
            });

            tier.classList.add("active");

            lastQtySource = "tier";

            return;
        }


        /* COUNTER BUTTONS */

        const counterBtn = e.target.closest(".qty-plus, .qty-minus");

        if (counterBtn) {
            lastQtySource = "manual";
        }


        /* NAVIGATION TO LARGE QUANTITY PAGE */

        const link = e.target.closest('a[href="/larger-quantity"]');

        if (link) {

            const qty = getSelectedQty();

            sessionStorage.setItem("selected_large_qty", qty);

        }

    });


    /* MANUAL INPUT TYPING */

    document.addEventListener("input", function (e) {

        const input = e.target.closest(".custom-qty input");

        if (!input) return;

        lastQtySource = "manual";

    });

}


/* =====================================================
LARGER QUANTITY PAGE - PRODUCT PREVIEW
===================================================== */

function updateQuotePreview(){

    if(!window.QuoteCart) return;

    const cart = QuoteCart.getCart();

    if(!cart || !cart.length) return;

    const container = document.querySelector(".product-summary-list");

    if(!container) return;

    const source = sessionStorage.getItem("quote_source");

    container.innerHTML = "";

    /* SINGLE PRODUCT MODE */

    if(source === "single"){

        const item = cart[cart.length - 1];

        container.innerHTML = `
            <div class="product-summary-item">
                <img src="${item.image}" />
                <div>
                    <strong>${item.name}</strong>
                    <p>${item.qty || 1} × £${item.price}</p>
                </div>
            </div>
        `;

        return;
    }

    /* CART MODE */

    if(source === "drawer"){

        cart.forEach(item => {

            container.innerHTML += `
                <div class="product-summary-item">
                    <img src="${item.image}" />
                    <div>
                        <strong>${item.name}</strong>
                        <p>${item.qty || 1} × £${item.price}</p>
                    </div>
                </div>
            `;

        });

    }

}


/* =====================================================
LOGO SECTION CONTROL
===================================================== */
function toggleLogoSection(){

    const source = sessionStorage.getItem("quote_source");

    const uploadSection = document.querySelector(".logo-upload-wrapper");

    const toggle = document.querySelector("#visual-toggle");

    if(!uploadSection || !toggle) return;

    if(source === "drawer"){

        uploadSection.style.display = "none";
        toggle.checked = false;

    } else {

        uploadSection.style.display = "block";
        toggle.checked = true;

    }

}


/* =====================================================
VISUAL TOGGLE
===================================================== */

function initVisualToggle(){

    const toggle = document.querySelector("#visual-toggle");

    const upload = document.querySelector(".logo-upload-wrapper");

    if(!toggle || !upload) return;

    toggle.addEventListener("change", function(){

        upload.style.display = toggle.checked ? "block" : "none";

    });

}

/* =====================================================
POPULATE PRODUCT DATA INTO FORM
===================================================== */

function populateProductInfo(){

    if(!window.QuoteCart) return;

    const cart = QuoteCart.getCart();

    if(!cart || !cart.length) return;

    const item = cart[cart.length-1];

    const id = document.querySelector("#product_id");
    const name = document.querySelector("#product_name");
    const image = document.querySelector("#product_image");
    const price = document.querySelector("#product_price");

    if(id) id.value = item.id || "";
    if(name) name.value = item.name || "";
    if(image) image.value = item.image || "";
    if(price) price.value = item.price || "";

}


/* =====================================================
FORM SUBMISSION
===================================================== */

function submitLargeQtyForm(){

    const form = document.querySelector(".larger-quantity-page");
    if (!form) return;

    const btn = document.querySelector(".lq-btn");
    if (!btn) return;

    btn.addEventListener("click", function(){

        const data = {

            company_name: form.querySelector('[name="company_name"]')?.value,

            first_name: form.querySelector('[name="first_name"]')?.value,
            last_name: form.querySelector('[name="last_name"]')?.value,

            email: form.querySelector('[name="email"]')?.value,

            phone: form.querySelector('[name="phone"]')?.value,
            postcode: form.querySelector('[name="postcode"]')?.value,

            quantity: form.querySelector(".qty-input")?.value,

            additional_information: form.querySelector('[name="additional_information"]')?.value,

            order_required_by: form.querySelector('[name="order_required_by"]')?.value,

           // product_name: document.querySelector(".product-summary strong")?.innerText
            products: window.QuoteCart ? QuoteCart.getCart() : []
        };


        /* VALIDATION */

        if(!data.first_name || !data.last_name || !data.email){

            alert("Please complete required fields");
            return;

        }


        /* SEND REQUEST */

        fetch("/larger-quantity/submit", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(data)

        })
        .then(response => {

            if (!response.ok) {
                throw new Error("Server error: " + response.status);
            }

            return response.json();

        })
        .then(res => {

            if (res.status === "success") {

                showQuoteConfirmation();
                showQuoteError();
                activateStep3();
                scrollToTop();   // 👈 scroll user to banner

            }

        })
        .catch(error => {

            console.error("Quote submission error:", error);

            alert("Something went wrong submitting the quote.");
            scrollToTop();   // 👈 bring user to top

        });

    });

}


/* =====================================================
PROGRESS BAR STEP 3
===================================================== */

function activateStep3(){

    const steps = document.querySelectorAll(".lq-progress .step");

    if(!steps.length || steps.length < 3) return;

    steps[0].classList.remove("active");
    steps[0].classList.add("done");

    steps[1].classList.remove("active");
    steps[1].classList.add("done");

    steps[2].classList.add("active");

}


/* =====================================================
QUOTE SUCCESS CONFIRMATION MESSAGE
===================================================== */

function showQuoteConfirmation(){

    const container = document.querySelector(".larger-quantity-page");

    if(!container) return;

    const msg = document.createElement("div");

    msg.className = "quote-success-message";

    msg.innerHTML = `
        <div class="alert alert-success mt-4">
            Your quote request has been submitted successfully.
            Our team will contact you shortly.
        </div>
    `;

    container.prepend(msg);

}

/* =====================================================
QUOTE ERROR CONFIRMATION MESSAGE
===================================================== */

function showQuoteError(){

    const container = document.querySelector(".larger-quantity-page");

    if(!container) return;

    const msg = document.createElement("div");

    msg.className = "quote-error-message";

    msg.innerHTML = `
        <div class="alert alert-danger mt-4">
            Something went wrong submitting the quote. Please try again.
        </div>
    `;

    container.prepend(msg);

}


/* =====================================================
INIT
===================================================== */

document.addEventListener("DOMContentLoaded", function () {

    trackEntrySource();

    if (isProductPage()) {
        initProductPage();
    }

    if (isLargeQtyPage()) {

        updateQuotePreview();

        toggleLogoSection();

        initVisualToggle();

        populateProductInfo();

        submitLargeQtyForm();

    }

});

})();