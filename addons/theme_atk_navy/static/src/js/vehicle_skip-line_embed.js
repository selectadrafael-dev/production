(function () {
  'use strict';

  console.log('[ATK] Phase 2 Vehicle Logic INITIALIZED');

  /*=====================================================
     HELPERS
     =====================================================*/

  function qs(id) {
    return document.getElementById(id);
  }

  function clearSelect(select, placeholder) {
    if (!select) return;
    select.innerHTML = '';
    const opt = document.createElement('option');
    opt.value = '';
    opt.textContent = placeholder;
    select.appendChild(opt);
  }

  function unique(arr) {
    return [...new Set(arr)];
  }

  function showHiddenContents() {
    const hidden = qs('hidden-contents');
    if (hidden) {
      hidden.style.display = 'block';
      console.log('[ATK] Hidden contents SHOWN');
    }
  }

  function hideHiddenContents() {
    const hidden = qs('hidden-contents');
    if (hidden) {
      hidden.style.display = 'none';
      console.log('[ATK] Hidden contents HIDDEN');
    }
  }

  function allRequiredFilled() {
    return (
      qs('vehicle_make')?.value &&
      qs('vehicle_model')?.value &&
      qs('vehicle_year')?.value
    );
  }

  function debugState(label) {
    console.log(`[ATK DEBUG] ${label}`, {
      key_type: qs('key_type')?.value,
      make: qs('vehicle_make')?.value,
      model: qs('vehicle_model')?.value,
      year: qs('vehicle_year')?.value,
      price: qs('price')?.value,
      vehicle_type: qs('vehicle_type')?.value
    });
  }

  function replaceSelectWithInput(id) {
    const old = qs(id);
    if (!old || old.tagName === 'INPUT') return;

    const input = document.createElement('input');
    input.type = 'text';
    input.id = old.id;
    input.name = old.name;
    input.className = old.className;
    input.placeholder = old.previousElementSibling?.textContent || '';
    input.required = true;

    old.replaceWith(input);
  }

  function setPriceAndType(records) {
    if (!records.length) return;

    const price = records[0].price || '';
    const type  = records[0].type  || '';

    if (priceEl) priceEl.value = price;
    if (vehicleTypeEl) vehicleTypeEl.value = type;

    console.log('[ATK DEBUG] Price & Vehicle Type SET', { price, type });
  }

  /* =====================================================
     ELEMENT REFERENCES
     ===================================================== */

  let makeEl      = qs('vehicle_make');
  let modelEl     = qs('vehicle_model');
  let modelWrapEl = qs('vehicle_model_wrapper');
  let yearEl      = qs('vehicle_year');
  let yearWrapEl  = qs('vehicle_year_wrapper');

  const priceEl       = qs('price');
  const vehicleTypeEl = qs('vehicle_type');
  const priceLabelEl  = qs('price_label');
  const vehicleTypeLabelEl = qs('vehicle_type_label');

  if (!makeEl || !modelEl || !yearEl) {
    console.warn('[ATK] Vehicle inputs not found');
    return;
  }

  /*=====================================================
     DATASET SELECTOR (KEY FIX)
     =====================================================*/

  function getVehicleDatasetByKeyType() {
    const keyType = qs('key_type')?.value;

    if (keyType === 'smart_key') {
        return window.ATK_VEHICLE_DATA || [];
    }

    if (keyType === 'transponder') {
        if (!window.ATK_VEHICLE_TRANSPONDER_DATA) {
            console.warn('[ATK] Transponder dataset not loaded yet');
            return null;
        }
        return window.ATK_VEHICLE_TRANSPONDER_DATA;
    }

    return [];
}


  hideHiddenContents();

  /*=====================================================
     HANDLE KEY TYPE CHANGE (POPULATE MAKE)
     =====================================================*/

 qs('key_type')?.addEventListener('change', function () {

    debugState('Key Type changed');

    clearSelect(makeEl, 'Select a make');
    clearSelect(modelEl, '');
    clearSelect(yearEl, '');
    hideHiddenContents();

    function tryPopulate() {
        const RAW_DATA = getVehicleDatasetByKeyType();

        // ⛔ Dataset not loaded yet → retry
        if (RAW_DATA === null) {
            setTimeout(tryPopulate, 200);
            return;
        }

        const DATA = RAW_DATA;

        if (!DATA.length) {
            console.warn('[ATK] Dataset resolved but empty');
            return;
        }

        const makes = unique(DATA.map(d => d.make));
        makes.forEach(m => makeEl.appendChild(new Option(m, m)));
        makeEl.appendChild(new Option('Others', 'Others'));

        console.log('[ATK] Makes populated:', makes);
    }

    tryPopulate();
});


  /*=====================================================
     HANDLE MAKE CHANGE
     =====================================================*/

  makeEl.addEventListener('change', function () {

    const RAW_DATA = getVehicleDatasetByKeyType();
    if (RAW_DATA === null) return;

    const DATA = RAW_DATA;
    const make = this.value;

    debugState('Make changed');

    clearSelect(modelEl, '');
    clearSelect(yearEl, '');

    if (!make || !DATA.length) {
      hideHiddenContents();
      return;
    }

    /* -------- OTHERS MODE -------- */
    if (make === 'Others') {

        /*Append hideen input element to track others*/
            const othersWrapper = qs('others_wrapper');

            if (othersWrapper && !qs('others')) {
              const hiddenInput = document.createElement('input');
              hiddenInput.type = 'hidden';
              hiddenInput.id = 'others';
              hiddenInput.name = 'others';
              hiddenInput.value = 'others';

              othersWrapper.appendChild(hiddenInput);

              console.log('[ATK DEBUG] Hidden others input appended');
            }

        /*Append hideen input element to track others*/

      ['vehicle_make', 'vehicle_model_wrapper', 'vehicle_year_wrapper'].forEach(id => {
        replaceSelectWithInput(id);
      });

      makeEl      = qs('vehicle_make');
      modelWrapEl = qs('vehicle_model_wrapper');
      yearWrapEl  = qs('vehicle_year_wrapper');

      if (priceEl) priceEl.style.display = 'none';
      if (vehicleTypeEl) vehicleTypeEl.style.display = 'none';
      if (priceLabelEl) priceLabelEl.style.display = 'none';
      if (vehicleTypeLabelEl) vehicleTypeLabelEl.style.display = 'none';

      qs('vehicle_reset_btn')?.style.setProperty('display', 'flex');

      console.log('[ATK DEBUG] Others mode activated');
      showHiddenContents();
      return;
    }

    /* -------- NORMAL FLOW -------- */

    const filtered = DATA.filter(d => d.make === make);

    setPriceAndType(filtered);

    const models = unique(
      filtered
        .map(d => d.model)
        .join(',')
        .split(',')
        .map(m => m.trim())
        .filter(Boolean)
    );

    models.forEach(m => modelEl.appendChild(new Option(m, m)));

    const years = unique(
      filtered
        .map(d => String(d.year).trim())
        .filter(Boolean)
    );

    years.forEach(y => yearEl.appendChild(new Option(y, y)));

    debugState('After dependent population');

    allRequiredFilled() ? showHiddenContents() : hideHiddenContents();
  });

  /*=====================================================
     HANDLE MODEL / YEAR CHANGE
     =====================================================*/

  [modelEl, yearEl].forEach(el => {
    el.addEventListener('change', function () {
      debugState('Model/Year changed');
      if (allRequiredFilled()) {
        showHiddenContents();
      }
    });
  });

})();
