(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {

    const btn = document.querySelector('.js-add-quote');
    if (!btn) return;

    const id = parseInt(btn.dataset.productId);
    const name = btn.dataset.productName;
    const image = btn.dataset.productImage;
    const price = parseFloat(btn.dataset.productPrice || 0);

    function updateText() {
      btn.textContent = QuoteCart.isEmpty()
        ? 'Create Quote'
        : 'Add To Quote';
    }

    updateText();

    btn.addEventListener('click', function (e) {
      e.preventDefault();

      if (QuoteCart.exists(id)) {
        document.dispatchEvent(new Event('openQuoteDrawer'));
        return;
      }

      QuoteCart.add({
        id,
        name,
        image,
        price,
        qty: 1
      });

      document.dispatchEvent(new Event('quoteCartUpdated'));
      document.dispatchEvent(new Event('openQuoteDrawer'));

      updateText();
    });

  });

})();