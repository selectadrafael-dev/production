(function () {
    'use strict';
    var sync = function () {
        var carousel = document.getElementById('o-carousel-product');
        var variants = document.querySelector('.js_add_cart_variants');
        var gHook = document.getElementById('gift_gallery_hook');
        var vHook = document.getElementById('gift_variant_hook');

        if (carousel && gHook && !gHook.contains(carousel)) gHook.appendChild(carousel);
        if (variants && vHook && !vHook.contains(variants)) vHook.appendChild(variants);
    };

    document.addEventListener('DOMContentLoaded', sync);
    var observer = new MutationObserver(sync);
    observer.observe(document.body, { childList: true, subtree: true });
})();
