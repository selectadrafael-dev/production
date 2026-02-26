(function () {
  'use strict';

  function openDrawer() {
    const drawer = document.getElementById('quoteDrawer');
    const overlay = document.getElementById('quoteDrawerOverlay');

    if (!drawer || !overlay) return;

    drawer.classList.add('is-open');
    overlay.classList.add('is-open');
  }

  function closeDrawer() {
    const drawer = document.getElementById('quoteDrawer');
    const overlay = document.getElementById('quoteDrawerOverlay');

    if (!drawer || !overlay) return;

    drawer.classList.remove('is-open');
    overlay.classList.remove('is-open');
  }

  document.addEventListener('DOMContentLoaded', function () {

    document.addEventListener('click', function (ev) {

      // OPEN
      if (
        ev.target.closest('.js-open-quote') ||
        ev.target.closest('.js-add-quote')
      ) {
        ev.preventDefault();
        openDrawer();
      }

      // CLOSE BUTTON
      if (ev.target.closest('.js-close-quote')) {
        ev.preventDefault();
        closeDrawer();
      }

      // OVERLAY CLOSE
      if (ev.target.id === 'quoteDrawerOverlay') {
        closeDrawer();
      }

    });

  });


  document.addEventListener('keydown', function (e) {
  if (e.key === 'Escape') {
    closeDrawer();
  }
});

})();