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

    if (!drawer || !overlay) {
      console.warn('Quote drawer not found');
      return;
    }

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

  // GLOBAL CLICK HANDLER (no DOMContentLoaded)
  document.addEventListener('click', function (ev) {

    const target = ev.target;

    // OPEN DRAWER
    if (
      target.closest('.js-open-quote') ||
      target.closest('.js-add-quote')
    ) {
      ev.preventDefault();
      openDrawer();
      return;
    }

    // CLOSE BUTTON
    if (target.closest('.js-close-quote')) {
      ev.preventDefault();
      closeDrawer();
      return;
    }

    // OVERLAY CLICK
    if (target.id === 'quoteDrawerOverlay') {
      closeDrawer();
      return;
    }

  });

  // ESC KEY CLOSE
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      closeDrawer();
    }
  });

})();