(function () {
'use strict';

/* =========================================
VARIANT SELECTION (highlight active)
========================================= */

document.addEventListener('click', function (e) {

const option = e.target.closest('.variant-option');
if (!option) return;

const container = option.closest('.variant-options');
if (!container) return;

container
  .querySelectorAll('.variant-option')
  .forEach(btn => btn.classList.remove('active'));

option.classList.add('active');

});

/* =========================================
QUANTITY STEPPER (+ / −)
========================================= */

document.addEventListener('click', function (e) {

const plus = e.target.closest('.qty-plus');
const minus = e.target.closest('.qty-minus');

if (!plus && !minus) return;

const wrapper = e.target.closest('.custom-qty');
if (!wrapper) return;

const input = wrapper.querySelector('input');
if (!input) return;

let value = parseInt(input.value) || 0;

if (plus) value++;
if (minus && value > 1) value--;

input.value = value;

});

/* =========================================
TIER SELECTION → SET QUANTITY
========================================= */

document.addEventListener('click', function (e) {

const card = e.target.closest('.tier-card');
if (!card) return;

const container = card.closest('#qty_tiers');
if (!container) return;

container
  .querySelectorAll('.tier-card')
  .forEach(c => c.classList.remove('active'));

card.classList.add('active');

const qty = parseInt(
  card.querySelector('strong')?.textContent
);

const input = document.querySelector('.custom-qty input');
if (input && qty) input.value = qty;

});

/* =========================================
QUOTE DRAWER (DESKTOP + MOBILE)
========================================= */
/*
document.addEventListener('click', function (e) {

 OPEN DRAWER 
const openBtn = e.target.closest('#openQuote');
if (openBtn) {

  const drawer = document.getElementById('quoteDrawer');
  if (drawer) drawer.classList.add('active');
  return;
}

/* CLOSE BUTTON 
if (e.target.closest('.drawer-close')) {

  const drawer = document.getElementById('quoteDrawer');
  if (drawer) drawer.classList.remove('active');
  return;
}

/* CLICK OUTSIDE PANEL (overlay) 
const overlay = e.target.closest('.drawer-overlay');
if (overlay) {

  const drawer = document.getElementById('quoteDrawer');
  if (drawer) drawer.classList.remove('active');
  return;
}

});
*/

})();
