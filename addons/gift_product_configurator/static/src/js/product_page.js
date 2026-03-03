(function () {
    'use strict';
    
    var syncLayout = function () {
        // Target native Odoo elements
        var carousel = document.getElementById('o-carousel-product');
        var variants = document.querySelector('.js_add_cart_variants');
        
        // Target your custom hooks
        var galleryHook = document.getElementById('gift_gallery_hook');
        var variantHook = document.getElementById('gift_variant_hook');

        // Relocate elements if they exist
        if (carousel && galleryHook) {
            galleryHook.appendChild(carousel);
        }
        if (variants && variantHook) {
            variantHook.appendChild(variants);
        }
    };

    // Run on load and after Odoo's internal AJAX updates
    document.addEventListener('DOMContentLoaded', syncLayout);
    
    // Safety check for Odoo's variant change events
    $(document).on('variant_info_full', function() {
        syncLayout();
    });
})();
