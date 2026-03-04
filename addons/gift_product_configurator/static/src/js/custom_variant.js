(function () {
    'use strict';
    var sync = function () {
        var carousel = document.getElementById('o-carousel-product');
        var gHook = document.getElementById('gift_gallery_hook');
        if (carousel && gHook && !gHook.contains(carousel)) { gHook.appendChild(carousel); }
    };

    document.addEventListener('DOMContentLoaded', sync);
    document.addEventListener('change', function (e) {
        if (e.target.classList.contains('js_variant_change')) {
            var block = e.target.closest('.variant_attribute');
            block.querySelector('.selected-value').innerText = e.target.getAttribute('data-value_name');
            // Toggle active classes
            var labels = block.querySelectorAll('label');
            labels.forEach(function(l) { l.classList.remove('active'); });
            e.target.closest('label').classList.add('active');
        }
    });

    var observer = new MutationObserver(sync);
    observer.observe(document.body, { childList: true, subtree: true });
})();
