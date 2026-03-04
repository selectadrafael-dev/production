(function () {
    'use strict';

    var relocateElements = function () {
        var carousel = document.getElementById('o-carousel-product');
        var variants = document.querySelector('.js_add_cart_variants');
        var galleryHook = document.getElementById('gift_gallery_hook');
        var variantHook = document.getElementById('gift_variant_hook');

        // ONLY move if they aren't already in the right spot (STOPS THE LOOP)
        if (carousel && galleryHook && carousel.parentElement !== galleryHook) {
            galleryHook.appendChild(carousel);
        }
        if (variants && variantHook && variants.parentElement !== variantHook) {
            variantHook.appendChild(variants);
        }
    };

    // Run on load
    window.addEventListener('load', relocateElements);

    // Watch for Odoo's AJAX updates (Variant Change)
    // We observe the main container instead of the whole body to stay safe
    var observer = new MutationObserver(function (mutations) {
        relocateElements();
    });

    var target = document.getElementById('product_detail');
    if (target) {
        observer.observe(target, { childList: true, subtree: true });
    }
})();
