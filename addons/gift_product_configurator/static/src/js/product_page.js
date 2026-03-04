(function () {
    'use strict';
    var relocateElements = function () {
        var carousel = document.getElementById('o-carousel-product');
        var variants = document.querySelector('.js_add_cart_variants');
        var galleryHook = document.getElementById('gift_gallery_hook');
        var variantHook = document.getElementById('gift_variant_hook');

        if (carousel && galleryHook && carousel.parentElement !== galleryHook) {
            galleryHook.appendChild(carousel);
        }
        if (variants && variantHook && variants.parentElement !== variantHook) {
            variantHook.appendChild(variants);
        }
    };

    window.addEventListener('load', relocateElements);
    var observer = new MutationObserver(relocateElements);
    var target = document.getElementById('product_detail');
    if (target) {
        observer.observe(target, { childList: true, subtree: true });
    }
})();
