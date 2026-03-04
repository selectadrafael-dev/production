(function () {
  'use strict';

  console.log('[GIFT CONFIGURATOR] Variant Listener Loaded');

  document.addEventListener('DOMContentLoaded', function () {

    const form = document.querySelector('.oe_website_sale');
    if (!form) {
      console.error('[GIFT CONFIGURATOR] oe_website_sale form not found');
      return;
    }

    form.addEventListener('change', function (e) {

      if (!e.target.matches('input[name="product_template_attribute_value_ids"]')) {
        return;
      }

      console.log('[GIFT CONFIGURATOR] Native variant change detected');

      // Wait for Odoo to update internal state
      setTimeout(updateUIFromNativeState, 200);

    });

    function updateUIFromNativeState() {

      // ===============================
      // 1️⃣ GET RESOLVED VARIANT ID
      // ===============================

      const productIdInput = form.querySelector('input[name="product_id"]');
      if (!productIdInput) {
        console.error('[GIFT CONFIGURATOR] product_id input missing');
        return;
      }

      const newProductId = productIdInput.value;
      console.log('[GIFT CONFIGURATOR] Resolved variant ID:', newProductId);

      // ===============================
      // 2️⃣ UPDATE IMAGE
      // ===============================

      const mainImage = document.querySelector('.main-product-image');
      if (mainImage) {
        mainImage.src =
          '/web/image/product.product/' +
          newProductId +
          '/image_1024';

        console.log('[GIFT CONFIGURATOR] Image updated.');
      }

      // ===============================
      // 3️⃣ MIRROR NATIVE PRICE
      // ===============================

      const nativePriceEl = document.querySelector('.oe_price .oe_currency_value');
      const customPriceEl = document.querySelector('.price');

      if (nativePriceEl && customPriceEl) {

        const newPriceValue = nativePriceEl.textContent.trim();

        // Preserve your currency symbol
        const symbolMatch = customPriceEl.textContent.trim().match(/^\D+/);
        const symbol = symbolMatch ? symbolMatch[0] : '';

        customPriceEl.textContent =
          symbol + parseFloat(newPriceValue).toFixed(2);

        console.log('[GIFT CONFIGURATOR] Price mirrored:', newPriceValue);

      } else {
        console.warn('[GIFT CONFIGURATOR] Price elements missing.');
      }

      // ===============================
      // 4️⃣ UPDATE QUOTE BUTTON
      // ===============================

      const quoteBtn = document.querySelector('.js-add-quote');
      if (quoteBtn) {
        quoteBtn.dataset.productId = newProductId;
        console.log('[GIFT CONFIGURATOR] Quote button synced.');
      }

    }

  });

})();