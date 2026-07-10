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
function updateQuotePreview(cart) {

    if (!window.QuoteCart) return;

    if (!cart || !cart.length) return;

    const container =
        document.querySelector(".product-summary-list");

    if (!container) return;

    container.innerHTML = "";

    cart.forEach(item => {

        //--------------------------------------------------
        // Pricing Snapshot
        //--------------------------------------------------

        const pricing =

        PricingUtils.getPricing(item);


        const qty =

            pricing.qty ||

            item.quantity ||

            1;

        const unitPrice =

            Number(

                pricing.price ||

                item.unit_price ||

                0

            );

        const currency =

            pricing.currency ||

            item.currency ||

            "AZN";

        const discount =

            pricing.discount ||

            item.discount ||

            0;

        const subtotal =

            Number(

                item.subtotal ||

                (unitPrice * qty)

            );

        container.innerHTML += `

            <div class="product-summary-item">

                <img src="${item.image}" />

                <div>

                    <strong>

                        ${item.product_name}

                    </strong>

                    <div>

                        Qty:
                        ${qty}

                    </div>

                    <div>

                        Unit Price:
                        ${currency} ${unitPrice.toFixed(2)}

                    </div>

                    ${
                        discount > 0

                        ?

                        `<div>

                            Discount:
                            ${discount}%

                        </div>`

                        :

                        ""

                    }

                    ${
                        item.print_method

                        ?

                        `<div>

                            Print:
                            ${item.print_method}

                        </div>`

                        :

                        ""

                    }

                    ${
                        item.logo_colours

                        ?

                        `<div>

                            Colours:
                            ${item.logo_colours}

                        </div>`

                        :

                        ""

                    }

                    <div>

                        <strong>

                            Estimated:

                            ${currency}

                            ${subtotal.toFixed(2)}

                        </strong>

                    </div>

                </div>

            </div>

        `;

    });

}


/* =====================================================
SUMMARY TOTALS
===================================================== */

function updateQuoteTotals(cart) {

    if (!window.QuoteCart) return;

    if (!cart || !cart.length) return;

    let subtotal = 0;
    let discount = 0;

    cart.forEach(item => {

        subtotal += Number(
            item.subtotal || 0
        );

        discount += Number(
            item.discount_amount || 0
        );

    });

    const estimatedTotal = subtotal;

    //--------------------------------------------------
    // Locate summary fields
    //--------------------------------------------------

    const subtotalEl =
        document.getElementById("quote_subtotal");

    const discountEl =
        document.getElementById("quote_discount");

    const vatEl =
        document.getElementById("quote_vat");

    const estimatedEl =
        document.getElementById("quote_total");

    //--------------------------------------------------
    // Currency (Pricing Engine First)
    //--------------------------------------------------

    const pricing =

        cart[0].pricing_snapshot || {};

    const currency =

        pricing.currency ||

        cart[0].currency ||

        "AZN";

    //--------------------------------------------------
    // Update UI
    //--------------------------------------------------

    if (subtotalEl) {

        subtotalEl.textContent =
            `${currency} ${subtotal.toFixed(2)}`;

    }

    if (discountEl) {

        discountEl.textContent =
            `${currency} ${discount.toFixed(2)}`;

    }

    if (vatEl) {

        vatEl.textContent =
            "Calculated Later";

    }

    if (estimatedEl) {

        estimatedEl.textContent =
            `${currency} ${estimatedTotal.toFixed(2)}`;

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

function populateProductInfo() {

    if (!window.QuoteCart) return;

    const cart = QuoteCart.getCart();

    if (!cart || !cart.length) return;

    /*
    ----------------------------------------------------
    We populate using the FIRST product.

    The controller already receives the full cart.

    Hidden fields are mainly for compatibility,
    display and future enhancements.
    ----------------------------------------------------
    */

    const primaryItem = cart[0];

    //--------------------------------------------------
    // Pricing Snapshot
    //--------------------------------------------------

    const pricing =

    PricingUtils.getPricing(primaryItem);

    const fields = {

        //--------------------------------------------------
        // Product
        //--------------------------------------------------

        product_id:
            primaryItem.product_id,

        product_name:
            primaryItem.product_name,

        product_image:
            primaryItem.image,

        product_url:
            primaryItem.product_url,

        sku:
            primaryItem.sku,

        //--------------------------------------------------
        // Pricing
        //--------------------------------------------------

        product_price:

            pricing.price ||

            primaryItem.unit_price,

        product_quantity:

            primaryItem.quantity,

        tier_quantity:

            pricing.qty ||

            primaryItem.tier_quantity,

        tier_name:

            pricing.tier ||

            primaryItem.tier_name,

        currency:

            pricing.currency ||

            primaryItem.currency,

        discount:

            pricing.discount ||

            primaryItem.discount,

        discount_amount:

            primaryItem.discount_amount,

        subtotal:

            primaryItem.subtotal,

        //--------------------------------------------------
        // Branding
        //--------------------------------------------------

        print_method:

            primaryItem.print_method,

        logo_colours:

            primaryItem.logo_colours,

        include_vat:

            primaryItem.include_vat,

        artwork_required:

            primaryItem.artwork_required

    };

    Object.keys(fields).forEach(function (name) {

        const input = document.querySelector(

            '[name="' + name + '"], #' + name

        );

        if (input) {

            input.value = fields[name];

        }

    });

}

/* =====================================================
FORM SUBMISSION
===================================================== */

function submitLargeQtyForm(){

    const form = document.querySelector(".larger-quantity-page");
    if (!form) return;

    const btn = document.querySelector(".lq-btn");
    if (!btn) return;

    let isSubmitting = false;

    const cart =
    window.QuoteCart
        ? QuoteCart.getCart()
        : [];

    btn.addEventListener("click", function(){

        if (isSubmitting) {
            return;
        }

        isSubmitting = true;

        btn.disabled = true;

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

            products:

                JSON.parse(

                    JSON.stringify(cart)

                ),

            submitted_from:
                "larger_quantity",

            submitted_at:
                new Date().toISOString(),

            quote_source:
                sessionStorage.getItem("quote_source") || "unknown",
        };

        if (!cart.length) {

            alert("Your quote cart is empty.");

            return;

        }


        /* VALIDATION */

        if(!data.first_name || !data.last_name || !data.email){

            alert("Please complete required fields");
            return;

        }

        const invalidItem = cart.find(item => !item.pricing_snapshot);

        if (invalidItem) {

            alert(

                "One or more products are missing pricing information. Please refresh the product page and try again."

            );

            isSubmitting = false;
            btn.disabled = false;

            return;

        }

        console.log("========== SUBMITTING QUOTE ==========");
        console.log("Payload:", data);
        console.log("About to call fetch()");

        /* SEND REQUEST */
       //fetch("/larger-quantity/submit", {
       fetch("/website/quote/submit", {

            method: "POST",

            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },

            body: JSON.stringify(data)

        })
        .then(response => {

            console.log("HTTP Status:", response.status);
            if (!response.ok) {
                throw new Error("Server error: " + response.status);
            }

            return response.json();

        })
        // .then(res => {
            .then(res => {
            console.log("Server Response:", res);

            //const result = res.result || {};
            const result = res.result || res;
            console.log("Actual Result:", result);
            // if (res.success) {
            if (result.success) {

                showQuoteConfirmation(res);

                activateStep3();

                scrollToTop();

                isSubmitting = false;
                btn.disabled = false;

                QuoteCart.clear();

            }
            else{

                showQuoteError(

                    res.message || "Quote submission failed."

                );

            }

        })

        .catch(error => {
            isSubmitting = false;
            btn.disabled = false;
            console.error("Quote submission error:", error);

            alert(error.message);

            showQuoteError(error.message);

            scrollToTop();

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

function showQuoteConfirmation(response){

    const container = document.querySelector(".larger-quantity-page");

    if(!container) return;

    const msg = document.createElement("div");

    msg.className = "quote-success-message";

    msg.innerHTML = `

        <div class="alert alert-success mt-4">

            <h4>

                ✓ Quote Submitted Successfully

            </h4>

            <p>

                Our sales team has received your quotation request.

            </p>

            <p>

                You will be contacted shortly.

            </p>

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

        const cart = QuoteCart.getCart();

        updateQuotePreview(cart);

        updateQuoteTotals(cart);

        toggleLogoSection();

        initVisualToggle();

        populateProductInfo();

        submitLargeQtyForm();

    }

});

})();