(function () {
  'use strict';

 //controling toggle middle contents
  document.addEventListener('DOMContentLoaded', function () {

    const printMethod = document.getElementById('print_method_select');
    if (!printMethod) return;

    const brandingBlocks = document.querySelectorAll('.branding-fields');

    function toggleBranding() {

      const value = printMethod.value.toLowerCase();

      if (value === 'non-branded') {

        // hide branding fields
        brandingBlocks.forEach(el => {
          el.classList.add('branding-hidden');
        });

      } else {

        // restore layout properly
        brandingBlocks.forEach(el => {
          el.classList.remove('branding-hidden');
        });

        // refresh ONLY when returning to branded
        setTimeout(() => {
          window.location.reload();
        }, 150);

      }

    }

    printMethod.addEventListener('change', toggleBranding);

  });


  //product quantity price update
  //==========================================================
  // Dynamic Quantity Pricing - Odoo 18
  //==========================================================

  document.addEventListener("DOMContentLoaded", function () {

      const tierCards = document.querySelectorAll("#qty_tiers .tier-card");
      const mainPrice = document.querySelector(".price-display .price");

      if (!tierCards.length || !mainPrice) {
          return;
      }

      //--------------------------------------------------
      // Store original Odoo price
      //--------------------------------------------------

      const defaultPriceHTML = mainPrice.innerHTML;

      //--------------------------------------------------
      // Get numeric base price
      //--------------------------------------------------

      function getBasePrice() {

          // First try data attribute
          if (mainPrice.dataset.basePrice) {

              const value = parseFloat(mainPrice.dataset.basePrice);

              if (!isNaN(value)) {
                  return value;
              }

          }

          // Fallback: extract from displayed text
          const text = mainPrice.textContent
              .replace(/[^0-9.,]/g, "")
              .replace(",", "");

          const value = parseFloat(text);

          return isNaN(value) ? 0 : value;

      }

      //--------------------------------------------------
      // Detect currency symbol
      //--------------------------------------------------

      function getCurrencySymbol() {

          const txt = mainPrice.textContent.trim();

          const match = txt.match(/[^\d.,\s]+/);

          return match ? match[0] : "$";

      }

      //--------------------------------------------------
      // Build quantity prices
      //--------------------------------------------------

      function buildTierPrices() {

            tierCards.forEach(card => {

                const priceSpan = card.querySelector(".price");

                if (!priceSpan) {
                    return;
                }

                const tier = JSON.parse(card.dataset.tier);

                priceSpan.textContent = tier.formatted_price;

            });

      }

      //--------------------------------------------------
      // Initial calculation
      //--------------------------------------------------

      buildTierPrices();

      //--------------------------------------------------
      // Click behaviour (same logic as original JS)
      //--------------------------------------------------


        tierCards.forEach(card => {

            card.addEventListener("click", function () {

                tierCards.forEach(c =>
                    c.classList.remove("active")
                );

                this.classList.add("active");

                const tierData = this.dataset.tier;

                if (!tierData) {
                    return;
                }

                const tier = JSON.parse(tierData);

                if (tier.discount === 0) {

                    mainPrice.innerHTML = defaultPriceHTML;

                    return;

                }

                mainPrice.textContent = tier.formatted_price;

            });

        });

   });

})();