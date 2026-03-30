(function () {
  'use strict';

  document.addEventListener('click', function (e) {

    if (e.target.closest('#openFilters')) {
      document
        .getElementById('filtersPanel')
        ?.classList.add('active');
    }

    if (e.target.closest('.filters')) return;

    if (!e.target.closest('#openFilters')) {
      document
        .getElementById('filtersPanel')
        ?.classList.remove('active');
    }

  });

})();