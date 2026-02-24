(function () {
  'use strict';

  async function updateCartCount() {

    try {

      const res = await fetch('/shop/cart/update_json', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: '{}'
      });

      const data = await res.json();

      const qty = data.cart_quantity || 0;

      document.querySelectorAll('.cart-count')
        .forEach(el => el.textContent = qty);

    } catch (err) {
      console.error('Cart count error:', err);
    }
  }


  // Run when page loads
  document.addEventListener('DOMContentLoaded', updateCartCount);


  // Optional: refresh when returning to tab
  document.addEventListener('visibilitychange', function () {
    if (!document.hidden) updateCartCount();
  });

})();