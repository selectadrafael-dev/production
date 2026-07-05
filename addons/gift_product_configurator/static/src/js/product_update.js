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

    const mainPrice = document.querySelector("#dynamic_main_price");
    const tierCards = document.querySelectorAll("#qty_tiers .tier-card");

    if (!mainPrice || !tierCards.length) {
        return;
    }

    //------------------------------------------------------
    // Currency Symbol
    //------------------------------------------------------

    function getCurrencySymbol() {

        const txt = mainPrice.textContent.trim();

        const match = txt.match(/[^\d.,\s-]+/);

        return match ? match[0] : "$";

    }

    //------------------------------------------------------
    // Base Price
    //------------------------------------------------------

    function getBasePrice() {

        let price = parseFloat(mainPrice.dataset.basePrice);

        if (!isNaN(price)) {
            return price;
        }

        const txt = mainPrice.textContent
            .replace(/[^0-9.,]/g, "")
            .replace(",", "");

        price = parseFloat(txt);

        return isNaN(price) ? 0 : price;

    }

    //------------------------------------------------------
    // Format Price
    //------------------------------------------------------

    function formatPrice(price) {

        return getCurrencySymbol() + price.toFixed(2);

    }

    //------------------------------------------------------
    // Build All Tier Prices
    //------------------------------------------------------

    function updateTierPrices() {

        const basePrice = getBasePrice();

        if (!basePrice) {
            return;
        }

        tierCards.forEach(card => {

            const discount = parseFloat(card.dataset.discount || 0);

            const tierPrice =
                basePrice * (1 - discount / 100);

            card.dataset.calculatedPrice = tierPrice;

            const span = card.querySelector(".price");

            if (span) {

                span.textContent =
                    formatPrice(tierPrice);

            }

        });

        //--------------------------------------------------
        // Keep selected card synced
        //--------------------------------------------------

        const activeCard = document.querySelector(
            "#qty_tiers .tier-card.active"
        );

        if (activeCard) {

            updateMainPrice(activeCard);

        }

    }

    //------------------------------------------------------
    // Update Main Price
    //------------------------------------------------------

    function updateMainPrice(card) {

        const price = parseFloat(
            card.dataset.calculatedPrice || 0
        );

        if (!price) {
            return;
        }

        mainPrice.innerHTML = formatPrice(price);

    }

    //------------------------------------------------------
    // Quantity Click
    //------------------------------------------------------

    tierCards.forEach(card => {

        card.addEventListener("click", function () {

            tierCards.forEach(c => c.classList.remove("active"));

            this.classList.add("active");

            updateMainPrice(this);

        });

    });

    //------------------------------------------------------
    // Initial Calculation
    //------------------------------------------------------

    updateTierPrices();

    //------------------------------------------------------
    // Watch for Odoo Price Updates
    //------------------------------------------------------

    const observer = new MutationObserver(function () {

            updateTierPrices();

        });

        observer.observe(mainPrice, {

            childList: true,
            subtree: true,
            characterData: true

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