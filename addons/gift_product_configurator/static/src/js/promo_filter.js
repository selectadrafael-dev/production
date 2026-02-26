(function () {
  'use strict';

  document.addEventListener('change', function (e) {

    if (!e.target.classList.contains('variant-filter')) return;

    const selected = [...document.querySelectorAll('.variant-filter:checked')]
      .map(el => el.dataset.value);

    fetch(window.location.pathname + '?attrs=' + selected.join(','))
      .then(res => res.text())
      .then(html => {
        const doc = new DOMParser().parseFromString(html, 'text/html');
        const newProducts = doc.querySelector('#promo-products');
        document.querySelector('#promo-products').innerHTML =
          newProducts.innerHTML;
      });

  });

})();