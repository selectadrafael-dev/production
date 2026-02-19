(function () {
  'use strict';

  /* =========================
     CATEGORY MENU
  ========================= */

  function getCatMenu() {
    return document.querySelector('[data-cat-menu]');
  }

  document.addEventListener('click', function (e) {

    const trigger = e.target.closest('[data-cat-toggle]');
    const menu = getCatMenu();

    if (trigger) {

      e.preventDefault();

      if (!menu) return;

      menu.hidden = !menu.hidden;
      return;
    }

    if (menu && !menu.hidden) {
      if (!e.target.closest('[data-cat-menu]')) {
        menu.hidden = true;
      }
    }

  });

})();
