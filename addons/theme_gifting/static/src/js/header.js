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

      //mobile nav
      document.addEventListener('click', function (e) {

        const toggle = e.target.closest('.mobile-toggle');
        if (toggle) {
          document
            .querySelector('.gifting-nav-links')
            ?.classList.toggle('open');
        }

      });

      //secondary menu
      document.addEventListener('click', function (e) {

        const toggle = e.target.closest('.mobile-toggle');
        if (!toggle) return;

        const menu = document.querySelector('.gifting-nav-bottom');
        menu?.classList.toggle('open');

      });

      //CLOSE MENU WHEN LINK CLICKED
      document.addEventListener('click', function (e) {

      const link = e.target.closest('.gifting-nav-bottom a');
      if (!link) return;

      document
        .querySelector('.gifting-nav-bottom')
        ?.classList.remove('open');

    });

    //category btn logic
    document.addEventListener('click', function (e) {

      const btn = e.target.closest('.mobile-cat-toggle');
      if (!btn) return;

      const mega = btn.nextElementSibling;
      mega?.classList.toggle('open');

    });

    //close btn
    document.addEventListener('click', function (e) {

        const menu = document.querySelector('.gifting-nav-bottom');

        /* CLOSE ONLY */
        if (e.target.closest('.mobile-close')) {
          if (menu) menu.classList.remove('open');
        }

      });

})();
