(function () {
  'use strict';

  function getDrawer() {
    return document.getElementById('quoteDrawer');
  }

  function getOverlay() {
    return document.getElementById('quoteDrawerOverlay');
  }

  function openDrawer() {

    const drawer = getDrawer();
    const overlay = getOverlay();

    if (!drawer || !overlay) return;

    drawer.classList.add('is-open');
    overlay.classList.add('is-open');
  }

  function closeDrawer() {

    const drawer = getDrawer();
    const overlay = getOverlay();

    if (!drawer || !overlay) return;

    drawer.classList.remove('is-open');
    overlay.classList.remove('is-open');
  }

  /* Ensure drawer mode exists */
  window.QuoteDrawerMode = window.QuoteDrawerMode || { type: 'quote' };

  /* GLOBAL CLICK HANDLER */
  document.addEventListener('click', function (ev) {

    const target = ev.target;

    /* OPEN DRAWER */
    if (
      target.closest('.js-open-quote') ||
      target.closest('.js-add-quote')
    ) {
      ev.preventDefault();
      openDrawer();
      return;
    }

    /* CLOSE BUTTON */
    if (target.closest('.js-close-quote')) {
      ev.preventDefault();
      closeDrawer();
      return;
    }

    /* OVERLAY CLICK */
    if (target.id === 'quoteDrawerOverlay') {
      closeDrawer();
      return;
    }

  });

  /* ESC CLOSE */
  document.addEventListener('keydown', function (e) {

    if (e.key === 'Escape') {
      closeDrawer();
    }

  });

  /* OPEN DRAWER EVENT (used by other scripts) */
  document.addEventListener('openQuoteDrawer', function () {

    openDrawer();

    const quoteBtn = document.querySelector('.js-quote-submit');
    const sampleBtn = document.querySelector('.js-sample-checkout');

    if (!quoteBtn || !sampleBtn) return;

    if (QuoteDrawerMode.type === 'sample') {

      quoteBtn.style.display = 'none';
      sampleBtn.style.display = 'block';

    } else {

      quoteBtn.style.display = 'block';
      sampleBtn.style.display = 'none';

    }

  });

  /* TAB SWITCHING */
  document.addEventListener('click', function (ev) {

    const tab = ev.target.closest('.drawer-tab');
    if (!tab) return;

    const target = tab.dataset.target;

    document.querySelectorAll('.drawer-tab')
      .forEach(t => t.classList.remove('is-active'));

    tab.classList.add('is-active');

    document.querySelectorAll('.drawer-panel')
      .forEach(p => p.classList.remove('is-active'));

    const panel = document.querySelector(
      `.drawer-panel[data-panel="${target}"]`
    );

    if (panel) panel.classList.add('is-active');

  });

  /* FREE VISUAL SWITCH */
  document.addEventListener('change', function (ev) {

    if (ev.target.id !== 'freeVisualSwitch') return;

    const upload = document.getElementById('visualUploadArea');
    if (!upload) return;

    if (ev.target.checked) {
      upload.classList.add('show');
    } else {
      upload.classList.remove('show');
    }

  });

  /* SAMPLE CHECKOUT REDIRECT */
 document.addEventListener('click', async function(e){

  const btn = e.target.closest('.js-sample-checkout');
  if(!btn) return;

  const cart = QuoteCart.getCart();

  if(!cart.length){
    window.location.href = '/shop/checkout';
    return;
  }

  for(const item of cart){

    await fetch('/shop/cart/update', {
      method: 'POST',
      headers: {
        'Content-Type':'application/json'
      },
      body: JSON.stringify({
        product_id: item.id,
        add_qty: item.qty || 1
      })
    });

  }

  window.location.href = '/shop/checkout';

});

})();