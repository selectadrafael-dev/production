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
  return window.innerWidth <= 768;
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
    p.classList.toggle('active', active);
  });

  items.forEach(i => {
    i.classList.toggle('active', i.dataset.catId === id);
  });
}

  /* =========================
     CATEGORY BUTTON
  ========================= */

  document.addEventListener('click', function (e) {

const trigger = safeClosest(e.target, '[data-cat-toggle="1"]');
if (!trigger) return;

/* 🔥 MOBILE FIRST */
if (window.innerWidth <= 768) {
  e.preventDefault();

  const drawer = document.querySelector('.mobile-cat-drawer');

  // RESET PANELS
  document.querySelectorAll('.mobile-panel')
    .forEach(p => p.classList.remove('active'));

  document.querySelector('[data-level="1"]')
    ?.classList.add('active');

  drawer?.classList.add('active');
  document.body.style.overflow = 'hidden';

  return; // 🔥 STOP DESKTOP LOGIC
}

/* DESKTOP CONTINUES BELOW */

  /* ================= DESKTOP LOGIC ================= */

  const menu = getCatMenu();
  if (!menu) return;

  e.preventDefault();

  const isOpen = menu.classList.contains('is-open');

  if (!isOpen) {
    console.log('📂 Open Mega Menu');

    menu.classList.add('is-open');

    resetMegaMenu(menu);
    initMegaHover(menu);

  } else {
    console.log('📁 Close Mega Menu');

    menu.classList.remove('is-open');

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

      resetMegaMenu(menu);
    }

  });

  /* =========================
     DESKTOP HOVER
  ========================= */
function initMegaHover(menu) {
  const left = menu?.querySelector('.mega-left');
  if (!left) return;

  // 🔥 remove old listeners (prevents stacking)
  left.onmouseover = null;

  left.onmouseover = function (e) {

    if (isMobile()) return;

    const item = safeClosest(e.target, '.mega-left-item');
    if (!item) return;

    showPanel(menu, item.dataset.catId);
  };
}
 

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


//mobile drawer closing
// CLOSE DRAWER
//mobile drawer closing
document.addEventListener('click', function (e) {
  if (e.target.closest('.drawer-close')) {
    const drawer = document.querySelector('.mobile-cat-drawer');

    if (drawer) {
      drawer.classList.remove('active');

      // 🔥 RESET PANELS (ADD HERE)
      document.querySelectorAll('.mobile-panel')
        .forEach(p => p.classList.remove('active'));

      document.querySelector('[data-level="1"]')
        ?.classList.add('active');

      // 🔥 RESTORE SCROLL (ADD HERE)
      document.body.style.overflow = '';
    }
  }
});

//========================contact us=======================
document.addEventListener("click", function (e) {
  const trigger = e.target.closest(".contact-trigger");
  const dropdown = document.querySelector(".contact-dropdown");

  if (!dropdown) return;

  if (trigger) {
    dropdown.classList.toggle("active");
  } else {
    dropdown.classList.remove("active");
  }
});

//========mobile==========
document.addEventListener('click', function(e){

  if (!isMobile()) return;

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


const back = e.target.closest('.mobile-back');

if (back) {
  const current = e.target.closest('.mobile-panel');
  if (!current) return;

  // 🔥 find previous panel (level 1 OR parent)
  let prev;

  if (current.dataset.level === "1") {
    return; // already at root
  }

  // if level 2 or 3 → always go back to level 1 (your structure)
  prev = document.querySelector('[data-level="1"]');

  // 🔥 clean state
  document.querySelectorAll('.mobile-panel')
    .forEach(p => {
      p.classList.remove('active', 'forward', 'backward');
    });

  // 🔥 show previous panel cleanly
  if (prev) {
    prev.classList.add('active');
  }
}

});

})();