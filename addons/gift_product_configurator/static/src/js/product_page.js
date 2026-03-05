(function () {
'use strict';

console.log('[GIFT CONFIGURATOR] Script Loaded');

document.addEventListener('DOMContentLoaded', function () {

    console.log('[GIFT CONFIGURATOR] DOM Ready');

    // ======================================
    // Find product container
    // ======================================

    const productContainer = document.querySelector('.js_product');

    if (!productContainer) {
        console.error('[GIFT CONFIGURATOR] js_product container not found');
        return;
    }

    console.log('[GIFT CONFIGURATOR] Product container detected');

    const form = productContainer.querySelector('form');

    if (!form) {
        console.error('[GIFT CONFIGURATOR] Product form not found');
        return;
    }

    console.log('[GIFT CONFIGURATOR] Product form detected');

    // ======================================
    // Listen for variant change
    // ======================================

    productContainer.addEventListener('change', function (e) {

        if (!e.target.classList.contains('js_variant_change')) {
            return;
        }

        console.log('[GIFT CONFIGURATOR] Variant change detected:', e.target.value);

        // allow Odoo VariantMixin to finish first
        setTimeout(updateUIFromNativeState, 200);

    });

    // ======================================
    // Sync custom UI with Odoo state
    // ======================================

    function updateUIFromNativeState() {

        console.log('[GIFT CONFIGURATOR] Syncing UI from native variant state');

        // 1️⃣ Get variant ID
        const productIdInput = form.querySelector('input[name="product_id"]');

        if (!productIdInput) {
            console.error('[GIFT CONFIGURATOR] product_id input missing');
            return;
        }

        const newProductId = productIdInput.value;

        console.log('[GIFT CONFIGURATOR] Active Variant ID:', newProductId);

        // 2️⃣ Update product image
        const mainImage = document.querySelector('.main-product-image');

        if (mainImage) {

            mainImage.src =
                '/web/image/product.product/' +
                newProductId +
                '/image_1024';

            console.log('[GIFT CONFIGURATOR] Image updated');

        } else {

            console.warn('[GIFT CONFIGURATOR] Main image not found');

        }

        // 3️⃣ Sync price
        const nativePriceEl = document.querySelector('.oe_price .oe_currency_value');
        const customPriceEl = document.querySelector('.price');

        if (nativePriceEl && customPriceEl) {

            const nativePrice = nativePriceEl.textContent.trim();

            const symbolMatch = customPriceEl.textContent.trim().match(/^\D+/);
            const symbol = symbolMatch ? symbolMatch[0] : '';

            const numericPrice = parseFloat(nativePrice.replace(/[^\d.]/g, ''));

            if (!isNaN(numericPrice)) {
                customPriceEl.textContent = symbol + numericPrice.toFixed(2);
                console.log('[GIFT CONFIGURATOR] Price updated:', numericPrice);
            }

        } else {

            console.warn('[GIFT CONFIGURATOR] Price elements missing');

        }

        // 4️⃣ Update quote button
        const quoteBtn = document.querySelector('.js-add-quote');

        if (quoteBtn) {
            quoteBtn.dataset.productId = newProductId;
            console.log('[GIFT CONFIGURATOR] Quote button updated');
        }

    }

});

})();