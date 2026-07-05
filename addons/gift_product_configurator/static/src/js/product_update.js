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
  document.addEventListener("DOMContentLoaded", function () {

    const tierCards = document.querySelectorAll(".tier-card");

    const mainPrice = document.querySelector("#dynamic_main_price");

    if (!mainPrice)
        return;

    const basePrice = parseFloat(
        mainPrice.dataset.basePrice || 0
    );

    if (!basePrice)
        return;

    //--------------------------------------------------
    // Build prices for every tier
    //--------------------------------------------------

    tierCards.forEach(card => {

        const discount =
            parseFloat(card.dataset.discount || 0);

        const tierPrice =
            basePrice * (1 - discount / 100);

        const priceSpan =
            card.querySelector(".dynamic-tier-price");

        if (priceSpan) {

            priceSpan.textContent =
                "$" + tierPrice.toFixed(2) + " each";

        }

    });

    //--------------------------------------------------
    // Click behaviour
    //--------------------------------------------------

    tierCards.forEach(card => {

        card.addEventListener("click", function () {

            tierCards.forEach(c =>
                c.classList.remove("active")
            );

            this.classList.add("active");

            const discount =
                parseFloat(this.dataset.discount || 0);

            const newPrice =
                basePrice * (1 - discount / 100);

            mainPrice.innerHTML =
                "$" + newPrice.toFixed(2);

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