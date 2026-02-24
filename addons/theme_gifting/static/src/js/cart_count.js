(function () {
  'use strict';

  async function updateCartCount() {

    try {

      const res = await fetch('/shop/cart', {
        method: 'GET'
      });

      const html = await res.text();

      // Create temp DOM
      const temp = document.createElement('div');
      temp.innerHTML = html;

      // Odoo cart quantity element
      const qtyEl = temp.querySelector('.my_cart_quantity');

      const qty = qtyEl ? parseInt(qtyEl.textContent) || 0 : 0;

      document.querySelectorAll('.cart-count')
        .forEach(el => el.textContent = qty);

    } catch (err) {
      console.error('Cart count error:', err);
    }
  }

  document.addEventListener('DOMContentLoaded', updateCartCount);

})();