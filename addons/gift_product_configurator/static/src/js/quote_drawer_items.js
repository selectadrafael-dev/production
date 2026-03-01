(function () {
  'use strict';

  function render() {

    const panel = document.querySelector('[data-panel="quote"]');
    if (!panel) return;

    const container = panel.querySelector('.quote-items');
    if (!container) return;

    const cart = QuoteCart.getCart();

    if (cart.length === 0) {
      container.innerHTML = `
        <div class="quote-empty">
          <p>Your quote is empty.</p>
        </div>
      `;
      return;
    }


        container.innerHTML = cart.map(item => `
    <div class="quote-item">

        <!-- DELETE -->
        <button class="quote-remove"
                data-id="${item.id}">
        🗑
        </button>

        <!-- TOP ROW -->
        <div class="quote-item__top">

        <img src="${item.image || '/web/static/img/placeholder.png'}"
            class="quote-item__image"/>

        <div class="quote-item__info">
            <div class="quote-item__name">${item.name}</div>
            <div class="quote-item__meta">${item.code || ''}</div>
        </div>

        </div>

        <!-- DIVIDER -->
        <div class="quote-item__divider"></div>

        <!-- BOTTOM ROW -->
        <div class="quote-item__bottom">

        <input type="number"
                class="quote-item__qty"
                value="${item.qty || 1}"
                min="1">

        <div class="quote-item__price">
            £${item.price}
            <span>per unit</span>
        </div>

        </div>

    </div>
    `).join('');
  }

  document.addEventListener('quoteCartUpdated', render);

  document.addEventListener('click', function (e) {

    const btn = e.target.closest('.quote-remove');
    if (!btn) return;

    QuoteCart.remove(parseInt(btn.dataset.id));

    document.dispatchEvent(new Event('quoteCartUpdated'));
  });

})();