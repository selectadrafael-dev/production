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

        <img src="${item.image}" width="60"/>

        <div class="quote-info">
          <strong>${item.name}</strong>
          <div>£${item.price}</div>
        </div>

        <button class="quote-remove"
                data-id="${item.id}">
          🗑
        </button>

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