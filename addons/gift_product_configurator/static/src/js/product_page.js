(function () {
    'use strict';

    /**
     * Relocates Odoo's functional elements into your custom 3-column hooks
     * and updates the "Selected Value" text labels.
     */
    var syncProductLayout = function () {
        // 1. Relocate native Odoo elements into your custom hooks
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

        // 2. Update the "Selected Value" labels (e.g., Color: Blue)
        var variantInputs = document.querySelectorAll('.js_variant_change:checked');
        variantInputs.forEach(function (input) {
            var container = input.closest('.variant_attribute');
            var labelSpan = container ? container.querySelector('.selected-value') : null;
            var valName = input.getAttribute('data-value_name');
            
            if (labelSpan && valName) {
                labelSpan.innerText = valName;
            }

            // Sync visual active state for custom box buttons
            var label = input.closest('label');
            if (label) {
                var allLabels = label.closest('.variant-options').querySelectorAll('label');
                allLabels.forEach(function (l) { l.classList.remove('active'); });
                label.classList.add('active');
            }
        });
    };

    // Run on initial load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', syncProductLayout);
    } else {
        syncProductLayout();
    }

    // Listen for manual changes on the variant radio buttons
    document.addEventListener('change', function (e) {
        if (e.target.classList.contains('js_variant_change')) {
            syncProductLayout();
        }
    });

    /**
     * Watch for Odoo's AJAX updates. When Odoo replaces the variant form 
     * during a selection, this observer puts it back into your hook instantly.
     */
    var observer = new MutationObserver(function (mutations) {
        syncProductLayout();
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

})();
