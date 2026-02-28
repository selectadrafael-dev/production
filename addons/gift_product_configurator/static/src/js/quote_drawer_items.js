(function () {
  'use strict';

  function renderDrawer() {
    const container = document.querySelector('.drawer-panel[data-panel="quote"]');
    if (!container) return;

    const cart = QuoteCart.getCart();

    let html = '';

    if (cart.length === 0) {
      html = `
        <div class="empty-quote">
          <p>Your quote is empty.</p>
          <button class="drawer-secondary js-close-quote">
            Continue Shopping
          </button>
        </div>
      `;
    } else {
      html = cart.map(item => `
        <div class="quote-item">
          <img src="${item.image}" />
          <div>
            <strong>${item.name}</strong>
            <button class="js-remove-quote" data-id="${item.product_id}">
              🗑
            </button>
          </div>
        </div>
      `).join('');
    }

    container.insertAdjacentHTML('beforeend', html);
  }

  document.addEventListener('quote-cart-updated', renderDrawer);

  document.addEventListener('click', function (ev) {

    const btn = ev.target.closest('.js-remove-quote');
    if (!btn) return;

    const id = parseInt(btn.dataset.id);

    QuoteCart.removeItem(id);

    document.dispatchEvent(new CustomEvent('quote-cart-updated'));

  });

  document.addEventListener('DOMContentLoaded', function () {
    document.dispatchEvent(new CustomEvent('quote-cart-updated'));
  });

})();