(function () {
  'use strict';

  function render() {
    const container = document.querySelector('[data-panel="quote"]');
    if (!container) return;

    const cart = QuoteCart.getCart();

    let html = '';

    if (cart.length === 0) {
      html = `
        <div class="quote-empty">
          <p>Your quote is empty.</p>
        </div>
      `;
    } else {
      html = cart.map(item => `
        <div class="quote-item">
          <img src="${item.image}" width="60"/>
          <div class="quote-info">
            <strong>${item.name}</strong>
            <div>${item.variant}</div>
            <div>£${item.price}</div>
          </div>

          <button class="quote-remove"
                  data-id="${item.id}">
            🗑
          </button>
        </div>
      `).join('');
    }

    const itemsArea = container.querySelector('.quote-items');
    if (itemsArea) itemsArea.innerHTML = html;
  }

  document.addEventListener('quoteCartUpdated', render);

  document.addEventListener('click', function (e) {
    const btn = e.target.closest('.quote-remove');
    if (!btn) return;

    QuoteCart.remove(parseInt(btn.dataset.id));
    document.dispatchEvent(new Event('quoteCartUpdated'));
  });

  document.addEventListener('openQuoteDrawer', function () {
  const drawer = document.getElementById('quoteDrawer');
  const overlay = document.getElementById('quoteDrawerOverlay');

  if (drawer && overlay) {
    drawer.classList.add('is-open');
    overlay.classList.add('is-open');
  }
});

})();