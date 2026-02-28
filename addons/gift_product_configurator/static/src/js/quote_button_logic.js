(function () {
  'use strict';

  function updateButton(btn) {
    const cart = QuoteCart.getCart();

    btn.textContent = cart.length === 0
      ? 'Create Quote'
      : 'Add To Quote';
  }

  document.addEventListener('DOMContentLoaded', function () {

    document.querySelectorAll('.js-add-quote').forEach(updateButton);

    document.addEventListener('click', function (ev) {

      const btn = ev.target.closest('.js-add-quote');
      if (!btn) return;

      ev.preventDefault();

      const productId = parseInt(btn.dataset.productId);

      if (QuoteCart.findItem(productId)) {
        // Already exists → open drawer only
        document.body.classList.add('quote-open');
        return;
      }

      const item = {
        product_id: productId,
        name: btn.dataset.productName,
        image: btn.dataset.productImage,
        quantity: 1
      };

      QuoteCart.addItem(item);

      // Update button state
      updateButton(btn);

      //Open drawer
      document.body.classList.add('quote-open');

      // Trigger drawer refresh
      document.dispatchEvent(new CustomEvent('quote-cart-updated'));

    });

  });

})();