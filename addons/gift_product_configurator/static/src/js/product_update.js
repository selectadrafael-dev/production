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

        brandingFields.forEach(el => {
          el.style.display = 'none';
        });

      } else {

        brandingFields.forEach(el => {
          el.style.display = '';
        });

      }

      // refresh page (like reference site)
      setTimeout(() => {
        window.location.reload();
      }, 200);

    }

    printMethod.addEventListener('change', toggleBranding);

  });

  //product quantity price update
  document.addEventListener('DOMContentLoaded', function () {

    const tierCards = document.querySelectorAll('#qty_tiers .tier-card');
    const mainPrice = document.getElementById('dynamic_main_price');

    if (!tierCards.length || !mainPrice) return;

    tierCards.forEach(card => {

      card.addEventListener('click', function () {

        /* remove active state */
        tierCards.forEach(c => c.classList.remove('active'));

        /* activate clicked card */
        this.classList.add('active');

        /* get price from clicked tier */
        const priceElement = this.querySelector('.price');
        if (!priceElement) return;

        let priceText = priceElement.textContent;

        /* remove "each" if present */
        priceText = priceText.replace('each', '').trim();

        /* update top product price */
        mainPrice.textContent = priceText;

      });

    });

  });
    
})();