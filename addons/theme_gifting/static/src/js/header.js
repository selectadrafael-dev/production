(function () {
  'use strict';

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

let justOpenedMega = false;
let allowHover = false;

  function getCatMenu() {
    return document.querySelector('[data-cat-menu="1"]');
  }

  function getRightPanel(menu) {
    return menu?.querySelector('.mega-right');
  }

  function isMobile() {
    return window.innerWidth <= 992;
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

    console.log('👉 Show category:', id);

    const panels = menu.querySelectorAll('.mega-panel');
    const items = menu.querySelectorAll('.mega-left-item');
    const right = getRightPanel(menu);

    // DESKTOP ONLY → show right panel
   
    if (!isMobile()) {
      if (right) right.classList.add('active');
    }

    panels.forEach(p => {
      // const active = p.dataset.panelId === id;
      const active = String(p.dataset.panelId) === String(id);

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

  const trigger = e.target.closest('[data-cat-toggle="1"]');
  const menu = getCatMenu();

  // CLICK BUTTON
  if (trigger) {
    e.preventDefault();

    console.log('🟢 Category button clicked');

    if (!menu) {
      console.warn('❌ Menu not found');
      return;
    }

    const isOpen = menu.classList.contains('is-open');

    if (!isOpen) {
      console.log('📂 Opening Mega Menu');

      menu.classList.add('is-open');
      menu.removeAttribute('hidden');

      // 🔥 block first hover trigger
      //justOpenedMega = true;
      allowHover = false;

      // allow hover only after real mouse movement
      setTimeout(() => {
        allowHover = true;
      }, 150);

      // 🔥 FULL HARD RESET (CRITICAL FIX)
      const panels = menu.querySelectorAll('.mega-panel');
      const items = menu.querySelectorAll('.mega-left-item');
      const right = getRightPanel(menu);

      // hide all panels
      panels.forEach(p => {
        p.style.display = 'none';
        p.classList.remove('active');
      });

      // remove active from all categories
      items.forEach(i => i.classList.remove('active'));

      // hide right panel completely
      if (right) right.classList.remove('active');
      initMegaHover(menu);

      // 🔍 DEBUG (you can remove later)
      console.log('🧼 Reset complete → panels visible:',
        [...panels].filter(p => p.style.display === 'block').length
      );

    } else {
      console.log('📁 Closing Mega Menu');

      menu.classList.remove('is-open');
      menu.setAttribute('hidden', 'hidden');

      resetMegaMenu(menu);
    }

    return;
  }

  // CLICK OUTSIDE
  if (menu && menu.classList.contains('is-open')) {
    if (!e.target.closest('[data-cat-menu="1"]') &&
        !e.target.closest('[data-cat-toggle="1"]')) {

      console.log('🟥 Click outside → closing menu');

      menu.classList.remove('is-open');
      menu.setAttribute('hidden', 'hidden');

      resetMegaMenu(menu);
    }
  }

});

  /* =========================
     DESKTOP HOVER
  ========================= */
function initMegaHover(menu) {
  // const left = menu?.querySelector('.mega-left');

  // if (!left) {
  //   console.warn('❌ .mega-left not found');
  //   return;
  // }

  // console.log('✅ Mega hover initialized');

  // left.addEventListener('mouseenter', function () {
  //   console.log('🟡 Entered left panel (no action yet)');
  // });

  // left.addEventListener('mouseover', function (e) {
  //   if (isMobile()) return;

  //   const item = e.target.closest('.mega-left-item');
  //   if (!item) return;

  //   console.log('👉 Hover category (controlled):', item.dataset.catId);

  //   showPanel(menu, item.dataset.catId);
  // });
}

  /* =========================
     MOBILE CATEGORY CLICK
  ========================= */

  document.addEventListener('click', function (e) {

    if (!isMobile()) return;

    const item = e.target.closest('.mega-left-item');
    const menu = getCatMenu();

    if (!item || !menu || !menu.classList.contains('is-open')) return;

    e.preventDefault();

    console.log('📱 Mobile category clicked:', item.dataset.catId);

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
