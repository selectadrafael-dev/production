(function () {
  'use strict';

  function render() {

    /* Ensure drawer exists on page */
    const panel = document.querySelector('[data-panel="quote"]');
    if (!panel) return;

    const container = panel.querySelector('.quote-items');
    if (!container) return;

    /* Ensure QuoteCart exists */
    if (typeof QuoteCart === 'undefined') {
      console.warn('QuoteCart not loaded');
      return;
    }

    const cart = QuoteCart.getCart();

    /* Empty cart */
    if (!Array.isArray(cart) || cart.length === 0) {

      container.innerHTML = `
        <div class="quote-empty">
          <p>Your quote is empty.</p>
        </div>
      `;

      return;
    }

    /* Render items */
    container.innerHTML = cart.map(function (item) {

      const image = item.image && item.image !== 'undefined'
        ? item.image
       : '/web/static/img/placeholder.png';

      // const qty = item.qty && item.qty > 0 ? item.qty : 1;

      // const price = item.price ? item.price : 0;

      const qty =
      item.quantity && item.quantity > 0
          ? item.quantity
          : 1;

      const price =
          Number(item.unit_price || 0);

      const currency =
          item.currency || "";

      const name =
          item.product_name || "";

      const sku =
          item.sku || "";

      return `
        <div class="quote-item">

          <!-- DELETE -->
          <button class="quote-remove"
                  data-id="${item.id}">
            🗑
          </button>

          <!-- TOP -->
          <div class="quote-item__top">

            <img src="${image}"
                 class="quote-item__image"/>

            <div class="quote-item__info">

              <div class="quote-item__name">
                ${item.name || ''}
              </div>

              <div class="quote-item__meta">
                ${item.code || ''}
              </div>

            </div>

          </div>

          <!-- DIVIDER -->
          <div class="quote-item__divider"></div>

          <!-- BOTTOM -->
          <div class="quote-item__bottom">

            <input type="number"
                   class="quote-item__qty"
                   value="${qty}"
                   min="1">

            <div class="quote-item__price">
              <span>$</span>${price}
              <span>per unit</span>
            </div>

          </div>

        </div>
      `;

    }).join('');
  }

  /* Ensure DOM ready before binding */
  document.addEventListener('DOMContentLoaded', function () {

    /* Render when cart updates */
    document.addEventListener('quoteCartUpdated', render);

    /* Render when drawer opens */
    document.addEventListener('openQuoteDrawer', render);

  });

  /* Remove item */
  document.addEventListener('click', function (e) {

    const btn = e.target.closest('.quote-remove');
    if (!btn) return;

    if (typeof QuoteCart === 'undefined') return;

    const id = parseInt(btn.dataset.id);
    if (!id) return;

    QuoteCart.remove(id);

    document.dispatchEvent(new Event('quoteCartUpdated'));

  });

})();