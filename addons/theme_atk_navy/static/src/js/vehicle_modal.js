console.log('[ATK] Vehicle modal JS FILE LOADED');

(function () {
  'use strict';

  const ALLOWED_MODAL_PATHS = ['/', '/atk-booking'];

function isVehicleModalAllowedPage() {
  const path = window.location.pathname.replace(/\/+$/, '');
  return ALLOWED_MODAL_PATHS.includes(path) || path === '';
}

console.log('[ATK] Vehicle modal JS FILE LOADED');

window.ATK_STATE = window.ATK_STATE || {};


  /* ======================================================
     HELPERS
     ====================================================== */

  function qs(id) {
    return document.getElementById(id);
  }

  function getVehicleModal() {
    return document.querySelector('[data-atk-vehicle-modal]');
  }

  function applyBookingTrackToForm(track) {
    if (!track) return;

    let attempts = 0;
    const maxAttempts = 30;

    const interval = setInterval(function () {
      attempts++;

      const form = qs('atk_vehicle_form');
      if (form) {
        let input = qs('booking_track');

        if (!input) {
          input = document.createElement('input');
          input.type = 'hidden';
          input.id = 'booking_track';
          input.name = 'booking_track';
          form.appendChild(input);
        }

        input.value = track;
        console.log('[ATK] Booking track injected into form →', track);
        clearInterval(interval);
      }

      if (attempts >= maxAttempts) {
        clearInterval(interval);
        console.error('[ATK ERROR] Vehicle form never appeared, track not injected');
      }
    }, 100);
  }


  /* ======================================================
     CLOSE VEHICLE MODAL
     ====================================================== */
    //function closeModal (){}

  document.addEventListener('click', function (e) {
    const closeBtn = e.target.closest('[data-atk-vehicle-close]');
    if (!closeBtn) return;

    const modal = getVehicleModal();
    if (modal) {
      modal.hidden = true;
      console.log('[ATK] Vehicle Identification modal CLOSED');
    }
  });

  /* ======================================================
     OPEN MODAL FROM URL (NO FLICKER, SINGLE RUN)
     ====================================================== */
(function openVehicleModalFromUrlSafe() {
  if (!isVehicleModalAllowedPage()) {
    console.log('[ATK] Vehicle modal blocked on this page:', window.location.pathname);
    return;
  }

  const params = new URLSearchParams(window.location.search);
  if (params.get('reset') !== 'open_vehicle_modal') return;

  console.log('[ATK] URL reset detected → waiting for vehicle modal');

  const track = params.get('track') || 'standard';

  let attempts = 0;
  const maxAttempts = 40;

  const interval = setInterval(() => {
    attempts++;

    const modal = document.querySelector('[data-atk-vehicle-modal]');
    const form  = document.getElementById('atk_vehicle_form');

    if (modal && form) {
      modal.hidden = false;

      console.log('[ATK] Vehicle modal OPENED via URL');
      console.log('[ATK] Track source:', track);

      applyBookingTrackToForm(track);

      // CLEAN URL
      const cleanUrl = new URL(window.location.href);
      cleanUrl.searchParams.delete('reset');
      window.history.replaceState({}, document.title, cleanUrl.pathname + cleanUrl.search);

      clearInterval(interval);
    }

    if (attempts >= maxAttempts) {
      clearInterval(interval);
      console.error('[ATK ERROR] Vehicle modal never appeared in DOM');
    }
  }, 100);
})();


  /* ======================================================
     RESET BUTTON (FORM ONLY)
     ====================================================== */

  const resetBtn = qs('vehicle_reset_btn');
  if (resetBtn) {
    resetBtn.addEventListener('click', function () {
      const url = new URL(window.location.href);

      url.searchParams.set('reset', 'open_vehicle_modal');

      const track = new URLSearchParams(window.location.search).get('track');
      if (track) {
        url.searchParams.set('track', track);
      }

      console.log('[ATK] Reset triggered → reload');
      window.location.href = url.toString();
    });
  }

  /*report and payment processing */
  /*************************************************
 * ATK VEHICLE FLOW – SINGLE CONSOLIDATED FILE
 * Safe for Odoo 18, theme activation, editor iframe
 *************************************************/

console.log('[ATK] vehicle.js loaded');

/* ===============================================
   COLLECT VEHICLE DATA FROM FORM
================================================ */
function collectVehicleData() {
  const val = id => qs(id)?.value || '';
  const chk = id => qs(id)?.checked ? 'Yes' : 'No';

  return {
    track: val('booking_track'),
    key_type: val('key_type'),
    make: val('vehicle_make'),
    model: val('vehicle_model_wrapper'),
    year: val('vehicle_year_wrapper'),
    price: val('price'),
    vehicle_type: val('vehicle_type'),
    battery: chk('battery'),
    vehicle_info: chk('vehicle_info'),
    others: val('others')
  };
}

/* ===============================================
   BUSINESS LOGIC (STANDARD vs PRIORITY)
================================================ */
function computeReport(data) {
  const isPriority = data.track === 'priority';
  const isOthers = data.others === 'others';

  let finalPrice = 'To be determined';

  if (!isOthers) {
    if (isPriority) {
      finalPrice = `$${Number(data.price || 0) + 120}`;
    } else {
      finalPrice = `$${Number(data.price || 0)}`;
    }
  }

  return {
    status: isPriority ? 'Skip-The-Line' : 'Standard',
    key_type: data.key_type,
    make: data.make,
    model: data.model,
    year: data.year,
    vehicle_type: data.vehicle_type,
    price: finalPrice,
    battery: data.battery,
    vehicle_info: data.vehicle_info,
    donation: '$5 (Non-refundable)'
  };
}


/* ===============================================
   RENDER REPORT SUMMARY (SAFE)
================================================ */
function renderReport(report) {
  const body = document.getElementById('atk_report_body');
  const hiddenContainer = document.getElementById('atk_report_hidden_inputs');
  if (!body || !hiddenContainer) return;

  // 1. Render Visible Summary for the User
  body.innerHTML = `
    <ul class="atk-report-list">
      <li><strong>Key Type:</strong> ${report.key_type}</li>
      <li><strong>Make:</strong> ${report.make}</li>
      <li><strong>Model:</strong> ${report.model}</li>
      <li><strong>Year:</strong> ${report.year}</li>
      <li><strong>Vehicle Type:</strong> ${report.vehicle_type}</li>
      <li><strong>Price:</strong> $${report.price}</li>
      <li><strong>Battery:</strong> ${report.battery}</li>
      <li><strong>Info:</strong> ${report.vehicle_info}</li>
      <li><strong>Donation:</strong> $${report.donation}</li>
    </ul>
  `;

  //get status

    const trackStatus = new URLSearchParams(window.location.search).get('track');
    let status = '';    
    if (trackStatus === 'priority') {
        status = 'Skip-The-Line';
      }else{
        status = 'Standard';
      }

  // 2. Render Hidden Inputs for Odoo Controller (name attributes must match Python fields)
  hiddenContainer.innerHTML = `
    <input type="hidden" name="status" value="${status}">
    <input type="hidden" name="key_type" value="${report.key_type}">
    <input type="hidden" name="make" value="${report.make}">
    <input type="hidden" name="model" value="${report.model}">
    <input type="hidden" name="year" value="${report.year}">
    <input type="hidden" name="vehicle_type" value="${report.vehicle_type}">
    <input type="hidden" name="price" value="${report.price}">
    <input type="hidden" name="battery" value="${report.battery}">
    <input type="hidden" name="vehicle_info" value="${report.vehicle_info}">
    <input type="hidden" name="donation" value="${report.donation}">
  `;
}


/* ===============================================
   REPORT MODAL CONTROL (OVERLAY-SAFE)
================================================ */
function openReportModal() {
  const overlay = qs('atk_report_overlay');
  if (!overlay) return;

  overlay.classList.remove('hidden');
  document.body.classList.add('atk-modal-open');
}

function closeReportModal() {
  const overlay = qs('atk_report_overlay');
  if (!overlay) return;

  overlay.classList.add('hidden');
  document.body.classList.remove('atk-modal-open');
}

/* ===============================================
   Proceed to Checkout
================================================ */

(function bindAtkCheckoutProceed() {
  const proceedBtn = document.getElementById('atk_report_proceed');
  if (!proceedBtn) return;
   console.log('You can book now');

  const urlTrack = new URLSearchParams(window.location.search).get('track');

  if (urlTrack) {
    localStorage.setItem('track', urlTrack);
    console.log('[ATK] Track:', urlTrack);
  }

})();


//=========close vehicle modal on login clicked============
(function bindAtkLoginProceed() {
  document.addEventListener('click', function (e) {
    //const authLink = e.target.closest('a[href^="/web/login"]');
    //if (!authLink) return;

      const authLink = e.target.closest('[data-atk-login-redirect]');
    if (!authLink) return;

    const modal = getVehicleModal();
    if (modal) {
      modal.hidden = true;
      console.log('[ATK] Vehicle Identification modal CLOSED before login redirect');
    }
  });
})();


//=============continue booking logic================

(function bindAtkContinueToBooking() {
  const continueBtn = document.getElementById('atk_continue_btn');
  if (!continueBtn) return;

  continueBtn.addEventListener('click', function () {
    const raw = collectVehicleData();

    console.log('[ATK] Continue clicked, raw data:', raw);

    const report = computeReport(raw); // must already exist

    renderReport(report);
    openReportModal();
  });
})();


//============cancel report=======================
(function bindAtkReportCancel() {
  const cancelBtn = document.getElementById('atk_report_cancel');
  if (!cancelBtn) return;

  cancelBtn.addEventListener('click', closeReportModal);
})();

 /* =====================================================
   CAPTURE BOOKING TRACK FROM BUTTON CLICK
   ===================================================== */
document.addEventListener('click', function (e) {
  const trigger = e.target.closest('[data-open-vehicle-modal]');
  if (!trigger) return;

  const track = trigger.dataset.track || 'standard';

  console.log('[ATK] Booking track captured:', track);

  const url = new URL(window.location.href);

  //THESE TWO PARAMS ARE THE CONTRACT
  url.searchParams.set('reset', 'open_vehicle_modal');
  url.searchParams.set('track', track);

  console.log('[ATK] Redirecting →', url.toString());

  //HARD reload so Odoo cannot block it
  window.location.href = url.toString();
});


})();
