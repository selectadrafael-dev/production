(function () {
  'use strict';

 //controling toggle middle contents
  document.addEventListener('DOMContentLoaded', function () {

    const printMethod = document.getElementById('print_method_select');
    if (!printMethod) return;

    const brandingFields = document.querySelectorAll('.branding-fields');

    function toggleBranding() {

      const value = printMethod.value.toLowerCase();

      if (value === 'non-branded') {

        /* Hide fields */
        brandingFields.forEach(el => {
          el.style.display = 'none';
        });

      } else {

        /* Show fields */
        brandingFields.forEach(el => {
          el.style.display = '';
        });

        /* Refresh only when returning to branded */
        setTimeout(() => {
          window.location.reload();
        }, 150);

      }

    }

    printMethod.addEventListener('change', toggleBranding);

  });


  //product quantity price update
   document.addEventListener('DOMContentLoaded', function () {

    const tierCards = document.querySelectorAll('#qty_tiers .tier-card');
    const mainPrice = document.querySelector('.price-display .price');

    if (!tierCards.length || !mainPrice) return;

    /* store original QWeb price */
    const defaultPriceHTML = mainPrice.innerHTML;

    tierCards.forEach(card => {

      card.addEventListener('click', function () {

        /* remove active state */
        tierCards.forEach(c => c.classList.remove('active'));
        this.classList.add('active');

        /* detect if default tier */
        const qwebPrice = this.querySelector('#actual_price');

        if (qwebPrice) {

          /* restore original QWeb price */
          mainPrice.innerHTML = defaultPriceHTML;
          return;

        }

        /* other tiers */
        const priceElement = this.querySelector('.price');
        if (!priceElement) return;

        let priceText = priceElement.textContent
          .replace('each', '')
          .trim();

        mainPrice.textContent = priceText;

      });

    });

  });
    
})();