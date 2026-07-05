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

          const basePrice = getBasePrice();

          if (!basePrice) {
              return;
          }

          const currency = getCurrencySymbol();

          tierCards.forEach(card => {

              const discount =
                  parseFloat(card.dataset.discount || 0);

              const newPrice =
                  basePrice * (1 - discount / 100);

              const priceSpan =
                  card.querySelector(".price");

              if (!priceSpan) {
                  return;
              }

              priceSpan.textContent =
                  currency +
                  newPrice.toFixed(2);

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

              // First/default tier restores original Odoo price
              if (
                  parseFloat(this.dataset.discount || 0) === 0
              ) {

                  mainPrice.innerHTML = defaultPriceHTML;
                  return;

              }

              // Copy displayed price
              const priceElement =
                  this.querySelector(".price");

              if (!priceElement) {
                  return;
              }

              mainPrice.textContent =
                  priceElement.textContent.trim();

          });

      });

  });

  //  document.addEventListener('DOMContentLoaded', function () {

  //   const tierCards = document.querySelectorAll('#qty_tiers .tier-card');
  //   const mainPrice = document.querySelector('.price-display .price');

  //   if (!tierCards.length || !mainPrice) return;

  //   /* store original QWeb price */
  //   const defaultPriceHTML = mainPrice.innerHTML;

  //   tierCards.forEach(card => {

  //     card.addEventListener('click', function () {

  //       /* remove active state */
  //       tierCards.forEach(c => c.classList.remove('active'));
  //       this.classList.add('active');

  //       /* detect if default tier */
  //       const qwebPrice = this.querySelector('#actual_price');

  //       if (qwebPrice) {

  //         /* restore original QWeb price */
  //         mainPrice.innerHTML = defaultPriceHTML;
  //         return;

  //       }

  //       /* other tiers */
  //       const priceElement = this.querySelector('.price');
  //       if (!priceElement) return;

  //       let priceText = priceElement.textContent
  //         .replace('each', '')
  //         .trim();

  //       mainPrice.textContent = priceText;

  //     });

  //   });

  // });
    
})();