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
      console.warn('Quote drawer not found');
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

  // GLOBAL CLICK HANDLER (no DOMContentLoaded)
  document.addEventListener('click', function (ev) {

    const target = ev.target;

    // OPEN DRAWER
    if (
      target.closest('.js-open-quote') ||
      target.closest('.js-add-quote')
    ) {
      ev.preventDefault();
      openDrawer();
      return;
    }

    // CLOSE BUTTON
    if (target.closest('.js-close-quote')) {
      ev.preventDefault();
      closeDrawer();
      return;
    }

    // OVERLAY CLICK
    if (target.id === 'quoteDrawerOverlay') {
      closeDrawer();
      return;
    }

  });

  // ESC KEY CLOSE
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      closeDrawer();
    }
  });

  // TAB SWITCHING
document.addEventListener('click', function (ev) {

  const tab = ev.target.closest('.drawer-tab');
  if (!tab) return;

  const target = tab.dataset.target;

  //Activate tab
  document.querySelectorAll('.drawer-tab')
    .forEach(t => t.classList.remove('is-active'));

  tab.classList.add('is-active');

  //Show panel
  document.querySelectorAll('.drawer-panel')
    .forEach(p => p.classList.remove('is-active'));

  const panel = document.querySelector(
    `.drawer-panel[data-panel="${target}"]`
  );

  if (panel) panel.classList.add('is-active');

});

// FREE VISUAL TOGGLE
document.addEventListener('change', function (ev) {

  if (ev.target.id !== 'freeVisualSwitch') return;

  const upload = document.getElementById('visualUploadArea');

  if (!upload) return;

  if (ev.target.checked) {
    upload.classList.add('show');
  } else {
    upload.classList.remove('show');
  }

});

// ===============================
// FREE VISUAL TOGGLE (DEBUG MODE)
// ===============================
document.addEventListener('change', function (ev) {

  console.log('CHANGE event detected:', ev.target);

  if (ev.target.id !== 'freeVisualSwitch') return;

  console.log('Free visual switch toggled');

  const upload = document.getElementById('visualUploadArea');

  console.log('Upload area element:', upload);

  if (!upload) {
    console.error('❌ Upload area NOT FOUND in DOM');
    return;
  }

  if (ev.target.checked) {
    console.log('Switch is ON → showing upload area');
    upload.classList.add('show');
  } else {
    console.log('Switch is OFF → hiding upload area');
    upload.classList.remove('show');
  }

});

document.addEventListener('click', function (ev) {
  if (ev.target.closest('.switch')) {
    console.log('Switch label clicked');
  }
});

})();