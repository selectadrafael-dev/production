(function () {
  'use strict';

  /* SECURITY: ensure browser environment */
  if (typeof window === 'undefined' || typeof localStorage === 'undefined') {
    return;
  }

  /* prevent overwriting if already loaded */
  if (window.QuoteCart) {
    return;
  }

  const KEY = 'quote_cart';

  function getCart() {
    try {
      const data = localStorage.getItem(KEY);
      return data ? JSON.parse(data) : [];
    } catch (e) {
      console.warn('QuoteCart corrupted data, resetting cart');
      localStorage.removeItem(KEY);
      return [];
    }
  }

  function save(cart) {
    try {
      localStorage.setItem(KEY, JSON.stringify(cart || []));
    } catch (e) {
      console.warn('QuoteCart save failed', e);
    }
  }

  function isEmpty() {
    return getCart().length === 0;
  }

  function exists(id) {
    if (!id) return false;
    return getCart().some(function (p) {
      return p.id === id;
    });
  }

  function add(product) {
    if (!product || !product.id) return;

    const cart = getCart();

    if (!exists(product.id)) {
      cart.push(product);
      save(cart);
    }
  }

  function remove(id) {
    if (!id) return;

    const cart = getCart().filter(function (p) {
      return p.id !== id;
    });

    save(cart);
  }

  window.QuoteCart = {
    getCart: getCart,
    add: add,
    remove: remove,
    exists: exists,
    isEmpty: isEmpty
  };

})();