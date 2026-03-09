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
UTILITY
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

    /* TIER SELECTION */

    document.addEventListener("click", function (e) {

        const tier = e.target.closest(".tier-card");

        if (tier){

            document.querySelectorAll(".tier-card").forEach(el=>{
                el.classList.remove("active");
            });

            tier.classList.add("active");

            lastQtySource = "tier";

            return;
        }


        /* COUNTER BUTTONS */

        const counterBtn = e.target.closest(".qty-plus, .qty-minus");

        if (counterBtn){

            lastQtySource = "manual";

        }


        /* NAVIGATION TO LARGE QUANTITY PAGE */

        const link = e.target.closest('a[href="/larger-quantity"]');

        if (link){

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
LARGER QUANTITY PAGE LOGIC
===================================================== */

function initLargeQtyPage() {

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

    updateQuotePreview();

}


/* =====================================================
INIT
===================================================== */

document.addEventListener("DOMContentLoaded", function () {

    if (isProductPage()) {
        initProductPage();
    }

    if (isLargeQtyPage()) {
        initLargeQtyPage();
    }

});

})();