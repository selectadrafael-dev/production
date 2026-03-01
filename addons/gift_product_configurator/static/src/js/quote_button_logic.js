(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {

    const btn = document.querySelector('.js-quote-button');
    if (!btn) return;

    const productId = parseInt(btn.dataset.productId);
    const productName = btn.dataset.productName;
    const variant = btn.dataset.variant || '';
    const price = parseFloat(btn.dataset.price || 0);
    const image = btn.dataset.image || '';

    function updateButton() {
      if (QuoteCart.isEmpty()) {
        btn.textContent = 'Create Quote';
      } else {
        btn.textContent = 'Add To Quote';
      }
    }

    updateButton();

    btn.addEventListener('click', function (e) {
      e.preventDefault();

      if (QuoteCart.exists(productId)) {
        document.dispatchEvent(new Event('openQuoteDrawer'));
        return;
      }

      QuoteCart.add({
        id: productId,
        name: productName,
        variant: variant,
        price: price,
        qty: 1,
        image: image
      });

      document.dispatchEvent(new Event('quoteCartUpdated'));
      document.dispatchEvent(new Event('openQuoteDrawer'));

      updateButton();
    });

  });

})();