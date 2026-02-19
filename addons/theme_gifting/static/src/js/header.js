(function () {
  'use strict';

  function getCatMenu() {
    return document.querySelector('[data-cat-menu]');
  }

  document.addEventListener('click', function (e) {

    const trigger = e.target.closest('[data-cat-toggle]');
    const menu = getCatMenu();

    /* OPEN / CLOSE */
    if (trigger) {

      e.preventDefault();

      if (!menu) {
        console.error('[CAT] Menu not found');
        return;
      }

      menu.hidden = !menu.hidden;

      return;
    }

    /* CLOSE OUTSIDE */
    if (menu && !menu.hidden) {
      if (!e.target.closest('[data-cat-menu]')) {
        menu.hidden = true;
      }
    }

  });

})();
