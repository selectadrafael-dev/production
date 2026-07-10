(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {

    /* SECURITY CHECKS */
    const quoteBtn = document.querySelector('.js-add-quote');
    const sampleBtn = document.querySelector('.js-add-sample');

    if (!quoteBtn && !sampleBtn) return;

    if (typeof QuoteCart === 'undefined') {
      console.warn('QuoteCart not loaded');
      return;
    }

    /* Ensure drawer mode object exists */
    window.QuoteDrawerMode = window.QuoteDrawerMode || { type: 'quote' };

    /* ===============================
       CREATE / ADD QUOTE BUTTON
    =============================== */

    if (quoteBtn) {

      function updateText() {
        quoteBtn.textContent = QuoteCart.isEmpty()
          ? 'Create Quote'
          : 'Add To Quote';
      }

      updateText();

      quoteBtn.addEventListener('click', function (e) {
        e.preventDefault();

        const id =
            parseInt(
                quoteBtn.dataset.productId || 0
            );

        if (!id) {
            return;
        }
        const name = quoteBtn.dataset.productName || '';
        const image = quoteBtn.dataset.productImage || '';
        const price = parseFloat(quoteBtn.dataset.productPrice || 0);


        //--------------------------------------------------
        // Selected Quantity Tier
        //--------------------------------------------------

        const activeTier =
            document.querySelector(
                "#qty_tiers .qty_tiers_card.active"
            );

        const tierQty =
            activeTier
                ? parseInt(activeTier.dataset.qty || 1)
                : 1;

        const tierDiscount =
            activeTier
                ? parseFloat(activeTier.dataset.discount || 0)
                : 0;

        const tierName =
            activeTier
                ? activeTier.dataset.tier || ""
                : "";

        const tierId =
            activeTier
                ? parseInt(activeTier.dataset.tierId || 0)
                : 0;

        //--------------------------------------------------
        // Manual Quantity
        //--------------------------------------------------

        const qtyInput =
            document.querySelector(".custom-qty input");

        const manualQty =
            qtyInput
                ? parseInt(qtyInput.value || tierQty)
                : tierQty;

        const finalQty =
            manualQty > 0
                ? manualQty
                : tierQty;

        //--------------------------------------------------
        // Branding
        //--------------------------------------------------

        const printMethod =
            document
                .getElementById("print_method_select")
                ?.value || "";

        const logoColours =
            document
                .getElementById("logo_colours_select")
                ?.value || "";

        //--------------------------------------------------
        // Current Price
        //--------------------------------------------------

        const displayedPrice =
            parseFloat(

                document
                    .getElementById("dynamic_main_price")
                    ?.innerText
                    .replace(/[^\d.]/g, "")

                    || price

            );

        //--------------------------------------------------
        // Currency
        //--------------------------------------------------
        const currencyText =
            activeTier
                ? tier.currency
                : (
                    document
                        .querySelector(
                            "#qty_tiers .qty_tiers_card"
                        )
                        ?.dataset
                        ?.currency || "AZN"
                );


        //--------------------------------------------------
        // Pricing Snapshot
        //--------------------------------------------------

        const originalPrice = displayedPrice;

        const discountAmount = 0;

        const tier =
        JSON.parse(
            activeTier.dataset.tier
        );

        const productSnapshot = {

        //--------------------------------------------------
        // Identity
        //--------------------------------------------------

            id: id,

            product_id: id,

            pricing_tier_id: tierId,

            product_name: name,

            sku:
                quoteBtn.dataset.productSku || "",

            product_url:
                quoteBtn.dataset.productUrl || window.location.href,

            image: image,

            //--------------------------------------------------
            // Quantity
            //--------------------------------------------------

            quantity: finalQty,

            tier_quantity: tierQty,

            tier_name: tierName,

            //--------------------------------------------------
            // Pricing
            //--------------------------------------------------

            unit_price: displayedPrice,

            original_price: originalPrice,
              
            discount: tierDiscount,

            discount_amount: discountAmount,

            subtotal:
              Number(
                  (displayedPrice * finalQty)
                      .toFixed(2)
              ),

            currency:
                currencyText.trim(),
            
            pricing_snapshot: tier,

            include_vat: false,

            //--------------------------------------------------
            // Branding
            //--------------------------------------------------

            print_method:
                printMethod,

            logo_colours:
                logoColours,

            artwork_required: false,

            //--------------------------------------------------
            // Audit
            //--------------------------------------------------

            added_at:
                new Date().toISOString(),

            source:
                "website",
            fingerprint:

            [
                id,
                printMethod,
                logoColours,
                tierQty,
                finalQty
            ].join("|"),

        };
            
            
        /* add product only if not already present */
        if (!QuoteCart.exists(productSnapshot)) {

            QuoteCart.add(productSnapshot);

        }


        /* set drawer mode */
        QuoteDrawerMode.type = 'quote';

        /* update UI */
        document.dispatchEvent(new Event('quoteCartUpdated'));
        document.dispatchEvent(new Event('openQuoteDrawer'));

        updateText();
      });
    }

    /* ===============================
       SAMPLE BUTTON
    =============================== */

    if (sampleBtn) {

      sampleBtn.addEventListener('click', function (e) {

        e.preventDefault();

        const id = parseInt(sampleBtn.dataset.productId || 0);
        if (!id) return;

        const product = {

              id: id,

              product_id: id,

              product_name:
                  sampleBtn.dataset.productName || "",

              image:
                  sampleBtn.dataset.productImage || "",

              quantity: 1,

              tier_quantity: 1,

              tier_name: "Sample",

              unit_price:
                  parseFloat(
                      sampleBtn.dataset.productPrice || 0
                  ),

              subtotal:
                  parseFloat(
                      sampleBtn.dataset.productPrice || 0
                  ),

              original_price:
                  parseFloat(
                      sampleBtn.dataset.productPrice || 0
                  ),

              discount: 0,

              discount_amount: 0,

              currency: "",

              include_vat: false,

              print_method: "",

              logo_colours: "",

              artwork_required: false,

              source: "sample",

              fingerprint:

                  [
                      id,
                      "sample"
                  ].join("|")

          };
        /* clear cart and insert only sample product */
        //localStorage.setItem('quote_cart', JSON.stringify([product]));

        /* clear existing quote cart */
        QuoteCart.clear();

        /* insert sample product */
        QuoteCart.add(product);

        /* switch drawer mode */
        QuoteDrawerMode.type = 'sample';

        /* update drawer */
        document.dispatchEvent(new Event('quoteCartUpdated'));
        document.dispatchEvent(new Event('openQuoteDrawer'));

      });

    }

  });

})();