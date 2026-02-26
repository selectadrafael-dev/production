(function () {
  'use strict';

  const icon = document.querySelector('.cart-icon');
  if (!icon) return;

  const countEl = icon.querySelector('.cart-count');

  async function updateCartCount() {

    try {
      const res = await fetch('/shop/cart', {
        method: 'GET'
      });

      const html = await res.text();

      // Parse returned page to extract quantity
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');

      const qty = doc.querySelector('.my_cart_quantity');

      countEl.textContent = qty ? qty.textContent : 0;

    } catch (e) {
      console.error('Cart count failed:', e);
    }
  }

  updateCartCount();

})();