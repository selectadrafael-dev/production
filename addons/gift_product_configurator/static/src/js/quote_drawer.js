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
      console.warn('Quote drawer not found in DOM');
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

  document.addEventListener('click', function (ev) {

    if (
      ev.target.closest('.js-open-quote') ||
      ev.target.closest('.js-add-quote')
    ) {
      ev.preventDefault();
      openDrawer();
    }

    if (ev.target.closest('.js-close-quote')) {
      closeDrawer();
    }

    if (ev.target.id === 'quoteDrawerOverlay') {
      closeDrawer();
    }

  });

})();