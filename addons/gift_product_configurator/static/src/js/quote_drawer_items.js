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

      const qty =
      item.quantity && item.quantity > 0
          ? item.quantity
          : 1;

      //--------------------------------------------------
      // Pricing Snapshot
      //--------------------------------------------------
      const price =
        Number(item.unit_price || 0);

      const currency =
          item.currency_symbol ||
          item.currency ||
          "AZN";

      const name =
          item.product_name || "";

      const sku =
          item.sku || "";

      return `
        <div class="quote-item">

          <!-- DELETE -->
          <button class="quote-remove"
                  data-fingerprint="${item.fingerprint}">
            🗑
          </button>

          <!-- TOP -->
          <div class="quote-item__top">

            <img src="${image}"
                 class="quote-item__image"/>

            <div class="quote-item__info">

              <div class="quote-item__name">
                ${name || ''}
              </div>

              <div class="quote-item__meta">
                ${sku || ''}
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

                ${currency}${price.toFixed(2)}

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
  document.addEventListener("click", function (e) {

      const btn = e.target.closest(".quote-remove");
      if (!btn) return;

      if (typeof QuoteCart === "undefined") return;

      const fingerprint = btn.dataset.fingerprint;
      if (!fingerprint) return;

      QuoteCart.remove(fingerprint);

      document.dispatchEvent(
          new Event("quoteCartUpdated")
      );

  });

})();