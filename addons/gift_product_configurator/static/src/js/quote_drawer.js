(function () {
  'use strict';

  function openDrawer() {
    document
      .getElementById('quoteDrawer')
      .classList.add('is-open');

    document
      .getElementById('quoteDrawerOverlay')
      .classList.add('is-open');
  }

  function closeDrawer() {
    document
      .getElementById('quoteDrawer')
      .classList.remove('is-open');

    document
      .getElementById('quoteDrawerOverlay')
      .classList.remove('is-open');
  }

  document.addEventListener('click', function (ev) {

    // OPEN FROM ANY TRIGGER
    if (
      ev.target.closest('.js-open-quote') ||
      ev.target.closest('.js-add-quote')
    ) {
      ev.preventDefault();
      openDrawer();
    }

    // CLOSE BUTTON
    if (ev.target.closest('.js-close-quote')) {
      closeDrawer();
    }

    // CLOSE ON OVERLAY CLICK
    if (ev.target.id === 'quoteDrawerOverlay') {
      closeDrawer();
    }

  });

})();