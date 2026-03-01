(function () {
  'use strict';

  const KEY = 'quote_cart';

  function getCart() {
    return JSON.parse(localStorage.getItem(KEY) || '[]');
  }

  function saveCart(cart) {
    localStorage.setItem(KEY, JSON.stringify(cart));
  }

  function isEmpty() {
    return getCart().length === 0;
  }

  function exists(productId) {
    return getCart().some(p => p.id === productId);
  }

  function add(product) {
    const cart = getCart();

    if (!exists(product.id)) {
      cart.push(product);
      saveCart(cart);
    }
  }

  function remove(productId) {
    const cart = getCart().filter(p => p.id !== productId);
    saveCart(cart);
  }

  window.QuoteCart = {
    getCart,
    add,
    remove,
    exists,
    isEmpty
  };

})();