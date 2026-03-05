document.addEventListener("DOMContentLoaded", function () {

    const productSection = document.querySelector("section#product_detail.oe_website_sale");

    if (!productSection) return;

    /* -------------------------------------------------
       1. ENSURE BANNER IS FIRST ELEMENT
    ------------------------------------------------- */

    const banner = productSection.querySelector(".gift-top-banner");

    if (banner) {
        productSection.insertBefore(banner, productSection.firstElementChild);
    }

    /* -------------------------------------------------
       2. GET MAIN PRODUCT ROW
    ------------------------------------------------- */

    const mainRow = document.querySelector("#product_detail_main");

    if (!mainRow) return;

    /* -------------------------------------------------
       3. CREATE 3 COLUMN WRAPPERS
    ------------------------------------------------- */

    const leftCol = document.createElement("div");
    const middleCol = document.createElement("div");
    const rightCol = document.createElement("div");

    leftCol.setAttribute("id", "gift-product-left");
    middleCol.setAttribute("id", "gift-product-middle");
    rightCol.setAttribute("id", "gift-product-right");

    leftCol.className = "gift-product-column";
    middleCol.className = "gift-product-column";
    rightCol.className = "gift-product-column";

    /* -------------------------------------------------
       4. TARGET EXISTING ODOO BLOCKS
    ------------------------------------------------- */

    const images = mainRow.querySelector(".o_wsale_product_images");
    const details = mainRow.querySelector("#product_details");
    const quoteDeal = document.querySelector("#add-to-quote-deal");

    /* -------------------------------------------------
       5. MOVE ELEMENTS INTO NEW COLUMNS
    ------------------------------------------------- */

    if (images) leftCol.appendChild(images);

    if (details) middleCol.appendChild(details);

    if (quoteDeal) rightCol.appendChild(quoteDeal);

    /* -------------------------------------------------
       6. CLEAN ORIGINAL ROW
    ------------------------------------------------- */

    mainRow.innerHTML = "";

    mainRow.appendChild(leftCol);
    mainRow.appendChild(middleCol);
    mainRow.appendChild(rightCol);

    /* -------------------------------------------------
       7. INSERT MIDDLE CONTENT CONTAINER
    ------------------------------------------------- */

    const ctaWrapper = document.querySelector("#o_wsale_cta_wrapper");

    if (ctaWrapper && !document.querySelector("#middle-content-container-main")) {

        const middleContainer = document.createElement("div");

        middleContainer.setAttribute("id", "middle-content-container-main");

        ctaWrapper.insertBefore(middleContainer, ctaWrapper.firstChild);

    }

});