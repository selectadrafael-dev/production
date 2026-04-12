(function () {
  'use strict';

  console.log('✅ Gifting Header JS Loaded');

  /* =========================
     SAFE HELPER
  ========================= */
  function safeClosest(target, selector) {
    if (!target || target.nodeType !== 1) return null;
    return target.closest(selector);
  }

  /* =========================
     HELPERS
  ========================= */
  function getCatMenu() {
    return document.querySelector('[data-cat-menu="1"]');
  }

  function getRightPanel(menu) {
    return menu?.querySelector('.mega-right');
  }

  function getMobileMenu() {
    return document.querySelector('.gifting-nav-bottom');
  }

  function getOverlay() {
    return document.querySelector('.mobile-overlay');
  }

  function isMobile() {
    return window.innerWidth <= 992;
  }

  /* =========================
     MOBILE NAV (CLEAN SYSTEM)
  ========================= */
  document.addEventListener('click', function (e) {

    const toggle = safeClosest(e.target, '.mobile-toggle');
    const closeBtn = safeClosest(e.target, '.mobile-close');
    const overlay = safeClosest(e.target, '.mobile-overlay');
    const link = safeClosest(e.target, '.gifting-nav-bottom a');

    const menu = getMobileMenu();
    const overlayEl = getOverlay();

    // OPEN MENU
    if (toggle) {
      console.log('📱 Opening mobile menu');
      menu?.classList.add('open');
      overlayEl?.classList.add('active');
      return;
    }

    // CLOSE MENU (button)
    if (closeBtn) {
      console.log('❌ Closing mobile menu');
      menu?.classList.remove('open');
      overlayEl?.classList.remove('active');
      return;
    }

    // CLOSE MENU (overlay)
    if (overlay) {
      console.log('🟥 Overlay clicked');
      menu?.classList.remove('open');
      overlayEl?.classList.remove('active');
      return;
    }

    // CLOSE MENU (link click)
    if (link) {
      console.log('🔗 Mobile link click');
      menu?.classList.remove('open');
      overlayEl?.classList.remove('active');
    }

  });

  /* =========================
     MEGA MENU CORE
  ========================= */

  function resetMegaMenu(menu) {
    if (!menu) return;

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

    const panels = menu.querySelectorAll('.mega-panel');
    const items = menu.querySelectorAll('.mega-left-item');
    const right = getRightPanel(menu);

    if (!isMobile() && right) {
      right.classList.add('active');
    }

    panels.forEach(p => {
      const active = String(p.dataset.panelId) === String(id);
      p.style.display = active ? 'block' : 'none';
      p.classList.toggle('active', active);
    });

    items.forEach(i => {
      i.classList.toggle('active', i.dataset.catId === id);
    });
  }

  /* =========================
     CATEGORY BUTTON
  ========================= */

  let allowHover = false;

  document.addEventListener('click', function (e) {

    const trigger = safeClosest(e.target, '[data-cat-toggle="1"]');
    const menu = getCatMenu();

    if (!trigger) return;

    e.preventDefault();

    if (!menu) return;

    const isOpen = menu.classList.contains('is-open');

    if (!isOpen) {
      console.log('📂 Open Mega Menu');

      menu.classList.add('is-open');
      menu.removeAttribute('hidden');

      allowHover = false;

      setTimeout(() => {
        allowHover = true;
      }, 150);

      resetMegaMenu(menu);
      initMegaHover(menu);

    } else {
      console.log('📁 Close Mega Menu');

      menu.classList.remove('is-open');
      menu.setAttribute('hidden', 'hidden');

      resetMegaMenu(menu);
    }

  });

  /* =========================
     CLICK OUTSIDE CLOSE
  ========================= */

  document.addEventListener('click', function (e) {

    const menu = getCatMenu();
    if (!menu || !menu.classList.contains('is-open')) return;

    if (
      !safeClosest(e.target, '[data-cat-menu="1"]') &&
      !safeClosest(e.target, '[data-cat-toggle="1"]')
    ) {
      console.log('🟥 Outside click → close');

      menu.classList.remove('is-open');
      menu.setAttribute('hidden', 'hidden');

      resetMegaMenu(menu);
    }

  });

  /* =========================
     DESKTOP HOVER
  ========================= */

  function initMegaHover(menu) {
    const left = menu?.querySelector('.mega-left');
    if (!left) return;

    left.addEventListener('mouseover', function (e) {

      if (isMobile() || !allowHover) return;

      const item = safeClosest(e.target, '.mega-left-item');
      if (!item) return;

      showPanel(menu, item.dataset.catId);
    });
  }

  /* =========================
     MOBILE CATEGORY CLICK
  ========================= */

  document.addEventListener('click', function (e) {

    if (!isMobile()) return;

    const item = safeClosest(e.target, '.mega-left-item');
    const menu = getCatMenu();

    if (!item || !menu || !menu.classList.contains('is-open')) return;

    e.preventDefault();

    showPanel(menu, item.dataset.catId);

  });

  /* =========================
     RESET ON LEAVE (STABLE)
  ========================= */

  document.addEventListener('mouseout', function (e) {

    const menu = getCatMenu();
    if (!menu || !menu.classList.contains('is-open')) return;

    if (menu.contains(e.relatedTarget)) return;

    console.log('🟡 Mouse left mega');

    resetMegaMenu(menu);

  });

  document.addEventListener('click', function (e) {
  const dropdown = e.target.closest('.account-dropdown');

  document.querySelectorAll('.account-dropdown').forEach(d => {
    if (d !== dropdown) d.classList.remove('open');
  });

  if (dropdown) {
    dropdown.classList.toggle('open');
  }
});

//mobile category js
document.addEventListener('click', function(e){

  const drawer = document.querySelector('.mobile-cat-drawer');
  const toggle = e.target.closest('[data-cat-toggle="1"]');

  /* OPEN DRAWER (MOBILE ONLY) */
  if (toggle && window.innerWidth < 768) {
    e.preventDefault();
    drawer?.classList.add('active');
    drawer?.removeAttribute('hidden');
    return;
  }

  /* CLOSE ON OUTSIDE CLICK */
  if (drawer && !e.target.closest('.mobile-cat-drawer') && !toggle) {
    drawer.classList.remove('active');
    drawer.setAttribute('hidden', 'hidden');
  }

  /* NAVIGATION */
  const item = e.target.closest('.mobile-item');
  if (item) {
    const target = item.dataset.target;
    const next = document.querySelector(`[data-panel="${target}"]`);

    if (next) {
      document.querySelectorAll('.mobile-panel')
        .forEach(p => p.classList.remove('active'));

      next.classList.add('active');
    }
  }

  /* BACK */
  const back = e.target.closest('.mobile-back');
  if (back) {
    document.querySelectorAll('.mobile-panel')
      .forEach(p => p.classList.remove('active'));

    document.querySelector('[data-level="1"]')
      ?.classList.add('active');
  }

});

//mobile drawer closing
/* CLOSE BUTTON */
const closeBtn = e.target.closest('.drawer-close');
if (closeBtn) {
  document.querySelector('.mobile-cat-drawer')?.classList.remove('active');
}

})();