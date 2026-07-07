/** @odoo-module **/

document.addEventListener("DOMContentLoaded", function () {

    const summary = document.querySelector(".product-summary-list");

    if (!summary) {
        return;
    }

    //--------------------------------------------------
    // Read Quote Cart
    //--------------------------------------------------

    let cart = [];

    try {

        cart = JSON.parse(
            localStorage.getItem("quote_cart") || "[]"
        );

    }
    catch {

        cart = [];

    }

    if (!cart.length) {

        summary.innerHTML = `

            <div class="alert alert-warning">

                No products selected.

            </div>

        `;

        return;

    }

    //--------------------------------------------------
    // Clear placeholder
    //--------------------------------------------------

    summary.innerHTML = "";

    //--------------------------------------------------
    // Build Summary
    //--------------------------------------------------

    cart.forEach(function (item) {

        summary.insertAdjacentHTML(

            "beforeend",

            `

            <div class="product-summary-item">

                <img src="${item.image || '/website/static/src/img/product_placeholder.png'}"/>

                <div>

                    <strong>

                        ${item.product_name}

                    </strong>

                    <p>

                        Variant:
                        ${item.variant_name || "-"}

                    </p>

                    <p>

                        Colour:
                        ${item.colour || "-"}

                    </p>

                    <p>

                        Print:
                        ${item.print_method || "-"}

                    </p>

                    <p>

                        Logo:
                        ${item.logo_colours || "-"}

                    </p>

                    <p>

                        Quantity:
                        ${item.quantity}

                    </p>

                    <p>

                        Unit Price:

                        ${item.unit_price}

                    </p>

                    <p>

                        Discount:

                        ${item.discount || 0}%

                    </p>

                </div>

            </div>

            `

        );

    });

    //--------------------------------------------------
    // Populate Hidden Fields (Totals)
    //--------------------------------------------------

    let subtotal = 0;

    let discountSaving = 0;

    cart.forEach(function (item) {

        const qty =
            parseFloat(item.quantity || 0);

        const unit =
            parseFloat(item.unit_price || 0);

        const discount =
            parseFloat(item.discount || 0);

        const original =
            unit / (1 - discount / 100 || 1);

        subtotal += qty * unit;

        discountSaving +=
            qty * (original - unit);

    });

    document.getElementById("quote_subtotal").textContent =
        "£" + subtotal.toFixed(2);

    document.getElementById("quote_discount").textContent =
        "- £" + discountSaving.toFixed(2);

    const includeVat =
        localStorage.getItem("include_vat") === "true";

    let total = subtotal;

    if (includeVat) {

        const vat = subtotal * 0.20;

        // const vatRate =

        //     parseFloat(

        //         document
        //         .getElementById("vat_rate")
        //         ?.value || 20

        //     );

        // const vat =

        //     subtotal *

        //     vatRate /

        //     100;

        document.getElementById("quote_vat").textContent =
            "£" + vat.toFixed(2);

        total += vat;

    }
    else {

        document.getElementById("quote_vat").textContent =
            "Excluded";

    }

    document.getElementById("quote_total").textContent =
        "£" + total.toFixed(2);

    const first = cart[0];

    if (!first) {
        return;
    }

    document.getElementById("product_id").value =
        first.product_id || "";

    document.getElementById("product_name").value =
        first.product_name || "";

    document.getElementById("product_image").value =
        first.image || "";

    document.getElementById("product_price").value =
        first.unit_price || "";

});