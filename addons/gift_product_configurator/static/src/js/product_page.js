(function () {
    'use strict';
    var relocate = function () {
        var carousel = document.getElementById('o-carousel-product');
        var variants = document.querySelector('.js_add_cart_variants');
        var galleryHook = document.getElementById('gift_gallery_hook');
        var variantHook = document.getElementById('gift_variant_hook');

        if (carousel && galleryHook && !galleryHook.contains(carousel)) {
            galleryHook.appendChild(carousel);
        }
        if (variants && variantHook && !variantHook.contains(variants)) {
            variantHook.appendChild(variants);
        }
    };

    document.addEventListener('DOMContentLoaded', relocate);
    var observer = new MutationObserver(relocate);
    observer.observe(document.body, { childList: true, subtree: true });
})();
