(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {

    /* SECURITY CHECKS */
    const quoteBtn = document.querySelector('.js-add-quote');
    const sampleBtn = document.querySelector('.js-add-sample');

    if (!quoteBtn && !sampleBtn) return;

    if (typeof QuoteCart === 'undefined') {
      console.warn('QuoteCart not loaded');
      return;
    }

    /* Ensure drawer mode object exists */
    window.QuoteDrawerMode = window.QuoteDrawerMode || { type: 'quote' };

    /* ===============================
       CREATE / ADD QUOTE BUTTON
    =============================== */

    if (quoteBtn) {

      const id = parseInt(quoteBtn.dataset.productId || 0);
      const name = quoteBtn.dataset.productName || '';
      const image = quoteBtn.dataset.productImage || '';
      const price = parseFloat(quoteBtn.dataset.productPrice || 0);

      function updateText() {
        quoteBtn.textContent = QuoteCart.isEmpty()
          ? 'Create Quote'
          : 'Add To Quote';
      }

      updateText();

      quoteBtn.addEventListener('click', function (e) {
        e.preventDefault();

        if (!id) return;

        const exists = QuoteCart.exists(id);

        /* add product only if not already present */
        if (!exists) {
          QuoteCart.add({
            id: id,
            name: name,
            image: image,
            price: price,
            qty: 1
          });
        }

        /* set drawer mode */
        QuoteDrawerMode.type = 'quote';

        /* update UI */
        document.dispatchEvent(new Event('quoteCartUpdated'));
        document.dispatchEvent(new Event('openQuoteDrawer'));

        updateText();
      });
    }

    /* ===============================
       SAMPLE BUTTON
    =============================== */

    if (sampleBtn) {

      sampleBtn.addEventListener('click', function (e) {

        e.preventDefault();

        const id = parseInt(sampleBtn.dataset.productId || 0);
        if (!id) return;

        const product = {
          id: id,
          name: sampleBtn.dataset.productName || '',
          image: sampleBtn.dataset.productImage || '',
          price: parseFloat(sampleBtn.dataset.productPrice || 0),
          qty: 1
        };

        /* clear cart and insert only sample product */
        localStorage.setItem('quote_cart', JSON.stringify([product]));

        /* switch drawer mode */
        QuoteDrawerMode.type = 'sample';

        /* update drawer */
        document.dispatchEvent(new Event('quoteCartUpdated'));
        document.dispatchEvent(new Event('openQuoteDrawer'));

      });

    }

  });

})();