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

      setTimeout(updateUIFromNativeState, 200);

    });

    function updateUIFromNativeState() {

      const productIdInput = form.querySelector('input[name="product_id"]');
      if (!productIdInput) {
        console.error('[GIFT CONFIGURATOR] product_id input missing');
        return;
      }

      const newProductId = productIdInput.value;
      console.log('[GIFT CONFIGURATOR] Resolved variant ID:', newProductId);

      // Update Image
      const mainImage = document.querySelector('.main-product-image');
      if (mainImage) {
        mainImage.src =
          '/web/image/product.product/' +
          newProductId +
          '/image_1024';
        console.log('[GIFT CONFIGURATOR] Image updated.');
      }

      // Update Price
      const nativePrice = document.querySelector('.oe_price .oe_currency_value');
      const customPrice = document.querySelector('.price');

      if (nativePrice && customPrice) {
        const symbolMatch = customPrice.textContent.trim().match(/^\D+/);
        const symbol = symbolMatch ? symbolMatch[0] : '';

        const newPrice =
          symbol + parseFloat(nativePrice.textContent).toFixed(2);

        customPrice.textContent = newPrice;
        console.log('[GIFT CONFIGURATOR] Price updated.');
      }

      // Update Quote Button
      const quoteBtn = document.querySelector('.js-add-quote');
      if (quoteBtn) {
        quoteBtn.dataset.productId = newProductId;
        console.log('[GIFT CONFIGURATOR] Quote button synced.');
      }

    }

  });

})();