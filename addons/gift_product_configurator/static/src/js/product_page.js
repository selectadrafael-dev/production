(function () {
    'use strict';
    var sync = function () {
        var carousel = document.getElementById('o-carousel-product');
        var gHook = document.getElementById('gift_gallery_hook');

        if (carousel && gHook && !gHook.contains(carousel)) {
            gHook.appendChild(carousel);
        }
    };

    window.addEventListener('load', sync);
    var observer = new MutationObserver(sync);
    var target = document.getElementById('product_detail');
    if (target) {
        observer.observe(target, { childList: true, subtree: true });
    }
})();
