//console.log('[ATK] Booking modal JS FILE LOADED');

(function () {

  const modal = document.querySelector('[data-atk-track-modal]');
  if (!modal) return;

  const standardBtn = modal.querySelector('[data-track="standard"]');

  const priorityBtn = modal.querySelector('[data-track="priority"]');

  if (!standardBtn || !priorityBtn) return;

  function getUSTime() {
    const now = new Date();
    return new Date(
      now.toLocaleString('en-US', { timeZone: 'America/New_York' })
    );
  }

  function applyTrackTimeLogic() {
    const usNow = getUSTime();

    const day = usNow.getDay();     // 0=Sun … 6=Sat
    const hour = usNow.getHours();
    const minute = usNow.getMinutes();

    let standardActive = false;
    let priorityActive = false;

    /* STANDARD BOOKING */
    if (
      (day === 0 && hour >= 18) || // Sunday 18:00+
      (day >= 1 && day <= 4)       // Mon–Thu
    ) {
      standardActive = true;
    }

    /* SKIP-THE-LINE */
    if (
      (day === 5 && hour === 0 && minute >= 1) ||
      (day === 5 && hour > 0) ||
      day === 6 ||
      (day === 0 && hour < 18)
    ) {
      priorityActive = true;
    }

    /* MUTUAL EXCLUSIVITY */
    if (standardActive) priorityActive = false;
    if (priorityActive) standardActive = false;

    standardBtn.disabled = !standardActive;
    priorityBtn.disabled = !priorityActive;

    console.log('[ATK DEBUG]', {
      standardDisabled: standardBtn.disabled,
      priorityDisabled: priorityBtn.disabled,
      time: new Date().toISOString()
    });

  }

  /*======================================================
     SINGLE, AUTHORITATIVE CLICK HANDLER (FIX) - A
     ======================================================*/

 document.addEventListener('click', function (e) {
    const trigger = e.target.closest('[data-open-booking-track]');
    if (!trigger) return;

    e.preventDefault();
    modal.hidden = false;
    applyTrackTimeLogic();
  });

  //booking page button link activation (B)
 document.addEventListener('click', function (e) {

    const link = e.target.closest('[data-atk-booking-page-open]');
    if (!link) return;

    // BLOCK DEFAULT <a href>
    e.preventDefault();
    e.stopPropagation();

    console.log('[ATK] Services link intercepted by JS');

    // run your logic
    applyTrackTimeLogic();

    // navigate manually
    window.location.href = '/atk-booking?page=services';

  }, true); // capture phase = stronger than theme JS
})();