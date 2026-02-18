(function () {
  'use strict';

  /* ======================================================
     UTIL: GET SELECT BOOKING MODAL
     ====================================================== */
  function getBookingModal() {
    return document.querySelector('[data-atk-track-modal]');
  }

  /* ======================================================
     OPEN SELECT BOOKING MODAL
     ====================================================== */
  document.addEventListener('click', function (e) {
    const trigger = e.target.closest('[data-open-booking-track]');
    if (!trigger) return;

      //BLOCK if URL reset is active
      if (window.ATK_STATE?.urlResetActive) {
        console.log('[ATK] Booking modal suppressed due to URL reset');
        return;
      }

          e.preventDefault();

          const modal = getBookingModal();
          if (!modal) {
            console.error('[ATK] Select Booking modal not found in DOM');
            return;
          }

          modal.hidden = false;

          console.log('[ATK] Select Booking modal OPENED');
  });


  /* ======================================================
   OPEN SELECT BOOKING MODAL FROM URL (SAFE EXTENSION)
   ====================================================== */
(function openBookingTrackModalFromUrlSafe() {

  const params = new URLSearchParams(window.location.search);
  if (params.get('reset') !== 'open_booking_track_modal') return;

  console.log('[ATK] URL reset detected → waiting for booking track modal');

  let attempts = 0;
  const maxAttempts = 40;

  const interval = setInterval(() => {
    attempts++;

    const modal = getBookingModal();
    if (modal) {
      modal.hidden = false;

      console.log('[ATK] Select Booking modal OPENED via URL');

      // Clean URL (remove reset only)
      const cleanUrl = new URL(window.location.href);
      cleanUrl.searchParams.delete('reset');
      window.history.replaceState(
        {},
        document.title,
        cleanUrl.pathname + cleanUrl.search
      );

      clearInterval(interval);

      //========Release URL lock AFTER modal is open & URL cleaned============
      setTimeout(() => {
        if (window.ATK_STATE) {
          window.ATK_STATE.urlResetActive = false;
          console.log('[ATK] URL reset released → homepage buttons active');
        }
      }, 0);
    }

    if (attempts >= maxAttempts) {
      clearInterval(interval);
      console.error('[ATK ERROR] Booking track modal never appeared in DOM');
    }
  }, 100);
})();


  /* ======================================================
     CLOSE SELECT BOOKING MODAL (BACK BUTTON)
    ================================================== */
  document.addEventListener('click', function (e) {
    const closeBtn = e.target.closest('[data-atk-track-close]');
    if (!closeBtn) return;

    const modal = getBookingModal();
    if (modal) {
      modal.hidden = true;
      console.log('[ATK] Select Booking modal CLOSED (Back button)');
    }
  });

})();
