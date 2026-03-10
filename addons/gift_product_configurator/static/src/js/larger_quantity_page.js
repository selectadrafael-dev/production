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

function updateQuotePreview() {

    if (!window.QuoteCart) return;

    const cart = QuoteCart.getCart();

    if (!cart || cart.length === 0) return;

    const lastItem = cart[cart.length - 1];


    /* IMAGE */

    const img = document.querySelector(".product-summary img");

    if (img && lastItem.image) {
        img.src = lastItem.image;
    }


    /* PRODUCT NAME */

    const name = document.querySelector(".product-summary strong");

    if (name && lastItem.name) {
        name.textContent = lastItem.name;
    }


    /* QUANTITY */

    const qtyInput = document.querySelector(".qty-input");

    const storedQty = sessionStorage.getItem("selected_large_qty");

    if (qtyInput && storedQty) {
        qtyInput.value = storedQty;
    }

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

            product_name: document.querySelector(".product-summary strong")?.innerText

        };


        /* VALIDATION */

        if(!data.first_name || !data.last_name || !data.email){

            alert("Please complete required fields");

            return;

        }


        /* SEND TO SERVER */

        fetch("/larger-quantity/submit",{

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify(data)

        })
       .then(r => r.json())
        .then(res => {

            if(res.status === "success"){

                showQuoteConfirmation();

                activateStep3();

            }

        });

    });

}


/* =====================================================
PROGRESS BAR STEP 3
===================================================== */

function activateStep3(){

    const url = new URL(window.location.href);

    if(url.searchParams.get("submitted") !== "1") return;

    const steps = document.querySelectorAll(".lq-progress .step");

    if(steps.length >= 3){
        steps[2].classList.add("active");
    }

}


/* =====================================================
QUOTE CONFIRMATION MESSAGE
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
INIT
===================================================== */

document.addEventListener("DOMContentLoaded", function () {

    if (isProductPage()) {
        initProductPage();
    }

    if (isLargeQtyPage()) {

        updateQuotePreview();

        populateProductInfo();

        submitLargeQtyForm();

        activateStep3();

    }

});

})();