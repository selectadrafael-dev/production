/** @odoo-module **/

document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("large-quote-form");

    if (!form) {
        return;
    }

    const submitButton = document.querySelector(".lq-btn");

    if (!submitButton) {
        return;
    }

    submitButton.addEventListener("click", async function () {

        //--------------------------------------------------
        // HTML5 Validation
        //--------------------------------------------------

        if (!form.reportValidity()) {
            return;
        }

        submitButton.disabled = true;
        submitButton.innerHTML = "Submitting...";

        //--------------------------------------------------
        // Build FormData
        //--------------------------------------------------

        const data = new FormData(form);

        //--------------------------------------------------
        // Quote Cart
        //--------------------------------------------------

        let cart = [];

        try {
            cart = JSON.parse(
                localStorage.getItem("quote_cart") || "[]"
            );
        }
        catch (e) {
            cart = [];
        }

        data.append(
            "cart",
            JSON.stringify(cart)
        );

        //--------------------------------------------------
        // VAT
        //--------------------------------------------------

        const vat = localStorage.getItem("include_vat");

        data.append(
            "include_vat",
            vat === "true"
        );

        //--------------------------------------------------
        // Free Visual
        //--------------------------------------------------

        const visual = document.getElementById("visual-toggle");

        data.append(
            "need_visual",
            visual && visual.checked
        );

        //--------------------------------------------------
        // Submit
        //--------------------------------------------------

        fetch("/website/quote/submit", {

            method: "POST",

            body: data,

            credentials: "same-origin",

        })

        .then(function (response) {

            if (response.redirected) {

                //--------------------------------------------------
                // Quote completed
                //--------------------------------------------------

                localStorage.removeItem("quote_cart");

                window.location.href = response.url;

                return;
            }

            throw "Submission failed";

        })

        .catch(function (error) {

            console.error(error);

            alert(
                "Unable to submit your quotation. Please try again."
            );

            submitButton.disabled = false;

            submitButton.innerHTML =
                "Get an express quote";

        });

    });

});