(function () {
  'use strict';

  const STORAGE_KEY = 'gifting_quote_cart';

  function getCart() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
    } catch (e) {
      return [];
    }
  }

  function saveCart(cart) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(cart));
  }

  function findItem(productId) {
    return getCart().find(p => p.product_id === productId);
  }

  function addItem(item) {
    const cart = getCart();

    if (!cart.some(p => p.product_id === item.product_id)) {
      cart.push(item);
      saveCart(cart);
    }

    return cart;
  }

  function removeItem(productId) {
    const cart = getCart().filter(p => p.product_id !== productId);
    saveCart(cart);
    return cart;
  }

  function clearCart() {
    localStorage.removeItem(STORAGE_KEY);
  }

  window.QuoteCart = {
    getCart,
    addItem,
    removeItem,
    findItem,
    clearCart
  };

})();