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

    
    //close btn
    document.addEventListener('click', function (e) {

        const menu = document.querySelector('.gifting-nav-bottom');

        /* CLOSE ONLY */
        if (e.target.closest('.mobile-close')) {
          if (menu) menu.classList.remove('open');
        }

      });

/* =========================
   MEGA MENU HOVER SYSTEM
========================= */

  console.log('✅ Gifting Header JS Loaded');

  /* =========================
     HELPERS
  ========================= */

  function getCatMenu() {
    return document.querySelector('[data-cat-menu="1"]');
  }

  function getRightPanel(menu) {
    return menu?.querySelector('.mega-right');
  }

  function resetMegaMenu(menu) {
    if (!menu) return;

    console.log('🔄 Resetting Mega Menu');

    const panels = menu.querySelectorAll('.mega-panel');
    const items = menu.querySelectorAll('.mega-left-item');
    const right = getRightPanel(menu);

    panels.forEach(p => {
      p.style.display = 'none';
      p.classList.remove('active');
    });

    items.forEach(i => i.classList.remove('active'));

    if (right) right.classList.remove('active');
  }

  function showPanel(menu, id) {
    if (!menu) return;

    console.log('👉 Hover category:', id);

    const panels = menu.querySelectorAll('.mega-panel');
    const items = menu.querySelectorAll('.mega-left-item');
    const right = getRightPanel(menu);

    if (right) right.classList.add('active');

    panels.forEach(p => {
      const active = p.dataset.panelId === id;
      p.style.display = active ? 'block' : 'none';
      p.classList.toggle('active', active);
    });

    items.forEach(i => {
      i.classList.toggle('active', i.dataset.catId === id);
    });
  }

  /* =========================
     CATEGORY MENU CLICK
  ========================= */

  document.addEventListener('click', function (e) {

    const trigger = e.target.closest('[data-cat-toggle]');
    const menu = getCatMenu();

    // CLICK BUTTON
    if (trigger) {
      e.preventDefault();

      console.log('🟢 Category button clicked');

      if (!menu) {
        console.warn('❌ Menu not found');
        return;
      }

      const isHidden = menu.hasAttribute('hidden');

      if (isHidden) {
        console.log('📂 Opening Mega Menu');
        menu.removeAttribute('hidden');
      } else {
        console.log('📁 Closing Mega Menu');
        menu.setAttribute('hidden', 'hidden');
        resetMegaMenu(menu);
      }

      return;
    }

    // CLICK OUTSIDE
    if (menu && !menu.hasAttribute('hidden')) {
      if (!e.target.closest('[data-cat-menu="1"]') &&
          !e.target.closest('[data-cat-toggle]')) {

        console.log('🟥 Click outside → closing menu');

        menu.setAttribute('hidden', 'hidden');
        resetMegaMenu(menu);
      }
    }

  });

  /* =========================
     HOVER SYSTEM
  ========================= */

  document.addEventListener('mouseover', function (e) {

    const item = e.target.closest('.mega-left-item');
    const menu = getCatMenu();

    if (!item || !menu || menu.hasAttribute('hidden')) return;

    showPanel(menu, item.dataset.catId);

  });

  /* =========================
     MOBILE NAV (UNCHANGED)
  ========================= */

  document.addEventListener('click', function (e) {

    const toggle = e.target.closest('.mobile-toggle');
    if (toggle) {
      console.log('📱 Mobile toggle clicked');

      document
        .querySelector('.gifting-nav-links')
        ?.classList.toggle('open');
    }

  });

  document.addEventListener('click', function (e) {

    const toggle = e.target.closest('.mobile-toggle');
    if (!toggle) return;

    const menu = document.querySelector('.gifting-nav-bottom');
    menu?.classList.toggle('open');

  });

  document.addEventListener('click', function (e) {

    const link = e.target.closest('.gifting-nav-bottom a');
    if (!link) return;

    console.log('🔗 Mobile link clicked → closing');

    document
      .querySelector('.gifting-nav-bottom')
      ?.classList.remove('open');

  });

  document.addEventListener('click', function (e) {

    const menu = document.querySelector('.gifting-nav-bottom');

    if (e.target.closest('.mobile-close')) {
      console.log('❌ Mobile close clicked');

      if (menu) menu.classList.remove('open');
    }

  });

/* =========================
   MEGA MENU HOVER SYSTEM
========================= */


})();
