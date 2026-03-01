(function () {
  'use strict';

  const KEY = 'quote_cart';

  function getCart() {
    return JSON.parse(localStorage.getItem(KEY) || '[]');
  }

  function save(cart) {
    localStorage.setItem(KEY, JSON.stringify(cart));
  }

  function isEmpty() {
    return getCart().length === 0;
  }

  function exists(id) {
    return getCart().some(p => p.id === id);
  }

  function add(product) {
    const cart = getCart();
    if (!exists(product.id)) {
      cart.push(product);
      save(cart);
    }
  }

  function remove(id) {
    const cart = getCart().filter(p => p.id !== id);
    save(cart);
  }

  window.QuoteCart = {
    getCart,
    add,
    remove,
    exists,
    isEmpty
  };

})();