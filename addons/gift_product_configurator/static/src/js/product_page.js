(function () {
    'use strict';

    /**
     * Relocates Odoo's native functional elements into the custom 3-column hooks.
     */
    var relocateElements = function () {
        var carousel = document.getElementById('o-carousel-product');
        var variants = document.querySelector('.js_add_cart_variants');
        
        var galleryHook = document.getElementById('gift_gallery_hook');
        var variantHook = document.getElementById('gift_variant_hook');

        // Move the Gallery/Carousel
        if (carousel && galleryHook && !galleryHook.contains(carousel)) {
            galleryHook.appendChild(carousel);
        }

        // Move the Variant Buttons/Form
        if (variants && variantHook && !variantHook.contains(variants)) {
            variantHook.appendChild(variants);
        }
    };

    // 1. Run immediately when the DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', relocateElements);
    } else {
        relocateElements();
    }

    // 2. Watch for Odoo's AJAX updates (Variant Change)
    // Odoo often re-renders the variant form; this observer puts it back if it resets.
    var observer = new MutationObserver(function (mutations) {
        relocateElements();
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    // 3. UI Helper: Manual toggle for active class on your custom buttons
    document.addEventListener('change', function (e) {
        if (e.target.classList.contains('js_variant_change')) {
            var label = e.target.closest('label');
            if (label) {
                var allLabels = label.closest('ul').querySelectorAll('label');
                allLabels.forEach(function (l) { l.classList.remove('active'); });
                label.classList.add('active');
            }
        }
    });

})();
