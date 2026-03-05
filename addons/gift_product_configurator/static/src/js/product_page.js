document.addEventListener("DOMContentLoaded", function () {

    const productSection = document.querySelector("section#product_detail.oe_website_sale");
    if (!productSection) return;

    /* -------------------------------------------------
       1. ENSURE BANNER IS FIRST ELEMENT
    ------------------------------------------------- */

    const banner = productSection.querySelector(".gift-top-banner");

    if (banner && productSection.firstElementChild !== banner) {
        productSection.insertBefore(banner, productSection.firstElementChild);
    }

    /* -------------------------------------------------
       2. GET MAIN PRODUCT ROW
    ------------------------------------------------- */

    const mainRow = document.querySelector("#product_detail_main");
    if (!mainRow) return;

    /* -------------------------------------------------
       3. SAVE EXISTING NODES BEFORE CHANGING DOM
    ------------------------------------------------- */

    const images = mainRow.querySelector(".o_wsale_product_images");
    const details = mainRow.querySelector("#product_details");
    const quoteDeal = document.querySelector("#add-to-quote-deal");
    const middleContainer = document.querySelector("#middle_content_container_main");

    /* -------------------------------------------------
       4. CREATE 3 COLUMN WRAPPERS
    ------------------------------------------------- */

    const leftCol = document.createElement("div");
    const middleCol = document.createElement("div");
    const rightCol = document.createElement("div");

    leftCol.id = "gift-product-left";
    middleCol.id = "gift-product-middle";
    rightCol.id = "gift-product-right";

    leftCol.className = "gift-product-column";
    middleCol.className = "gift-product-column";
    rightCol.className = "gift-product-column";

    /* -------------------------------------------------
       5. CLEAR ORIGINAL ROW
    ------------------------------------------------- */

    mainRow.innerHTML = "";

    /* -------------------------------------------------
       6. BUILD NEW STRUCTURE
    ------------------------------------------------- */

    if (images) leftCol.appendChild(images);

    if (details) middleCol.appendChild(details);

    if (middleContainer) middleCol.appendChild(middleContainer);

    if (quoteDeal) rightCol.appendChild(quoteDeal);

    mainRow.appendChild(leftCol);
    mainRow.appendChild(middleCol);
    mainRow.appendChild(rightCol);

    /* -------------------------------------------------
       7. PLACE CONTAINER INSIDE CTA WRAPPER
    ------------------------------------------------- */

    const ctaWrapper = document.querySelector("#o_wsale_cta_wrapper");

    if (ctaWrapper && middleContainer) {

        if (ctaWrapper.firstElementChild !== middleContainer) {
            ctaWrapper.prepend(middleContainer);
        }

    }

});