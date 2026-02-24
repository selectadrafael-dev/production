(function () {
'use strict';

/* =============================
SAFE DOM HELPERS
============================= */

function qs(id) {
return document.getElementById(id);
}

function rpc(route, params) {
return odoo.rpc(route, params || {});
}

/* =============================
ELEMENTS
============================= */

const drawer = qs('quote_drawer');
const overlay = qs('drawer_overlay');
const itemsBox = qs('quoteItems');

if (!drawer) return; // Safe exit if drawer not on page

/* =============================
DRAWER OPEN / CLOSE
============================= */

function openDrawer() {
drawer.classList.add('open');
if (overlay) overlay.classList.add('show');
loadQuote();
}

function closeDrawer() {
drawer.classList.remove('open');
if (overlay) overlay.classList.remove('show');
}

/* =============================
LOAD QUOTE DATA
============================= */

async function loadQuote() {

const data = await rpc('/quote/data');

if (!itemsBox) return;

const lines = data.lines || [];

itemsBox.innerHTML = '';

if (!lines.length) {
  itemsBox.innerHTML =
    '<div class="empty">Your quote is empty.</div>';
  return;
}

lines.forEach(line => {

  const el = document.createElement('div');
  el.className = 'quote-item';

  el.innerHTML = `
    <img src="${line.image}">
    <div class="info">
      <div class="name">${line.name}</div>
      <div>${line.qty} × ${line.price}</div>
    </div>
    <button class="remove" data-id="${line.id}">✕</button>
  `;

  itemsBox.appendChild(el);
});

}

/* =============================
GLOBAL CLICK HANDLER
============================= */

document.addEventListener('click', async function (e) {

/* OPEN FROM HEADER CART ICON */
if (e.target.closest('.cart-icon')) {
  e.preventDefault();
  openDrawer();
  return;
}

/* OPEN FROM ANY BUTTON */
if (e.target.closest('.js-open-quote')) {
  e.preventDefault();
  openDrawer();
  return;
}

/* CLOSE DRAWER */
if (e.target.id === 'close_drawer' ||
    e.target.id === 'drawer_overlay') {
  closeDrawer();
  return;
}

/* ADD PRODUCT TO QUOTE */
const addBtn = e.target.closest('.js-add-quote');
if (addBtn) {

  await rpc('/quote/add', {
    product_id: addBtn.dataset.productId,
    qty: 1
  });

  openDrawer();
  return;
}

/* REMOVE LINE */
const removeBtn = e.target.closest('.remove');
if (removeBtn) {

  await rpc('/quote/remove', {
    line_id: removeBtn.dataset.id
  });

  loadQuote();
  return;
}

/* SUBMIT QUOTE */
if (e.target.id === 'submitQuote') {

  await rpc('/quote/submit');

  alert('Quote submitted!');
  loadQuote();
  return;
}

});

/* =============================
VISUAL TOGGLE + UPLOAD
============================= */

document.addEventListener('change', function (e) {

if (e.target.id !== 'visual_toggle') return;

const checked = e.target.checked;

rpc('/quote/toggle_visual', { value: checked });

const uploadBox = qs('visual_upload');
if (uploadBox) {
  uploadBox.style.display = checked ? 'block' : 'none';
}

});

})();