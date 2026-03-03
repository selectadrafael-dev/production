(function () {
  'use strict';

  console.log('[GIFT CONFIGURATOR] Script Loaded');

  document.addEventListener('DOMContentLoaded', function () {

    console.log('[GIFT CONFIGURATOR] DOM Ready');

    const form = document.querySelector('.o_custom_variant_form');

    if (!form) {
      console.error('[GIFT CONFIGURATOR] Variant form not found.');
      return;
    }

    const templateId = parseInt(form.dataset.productTemplateId);

    if (!templateId) {
      console.error('[GIFT CONFIGURATOR] Missing product template ID.');
      return;
    }

    console.log('[GIFT CONFIGURATOR] Template ID:', templateId);

    form.addEventListener('change', function (e) {

      if (!e.target.classList.contains('variant-radio')) return;

      console.log('[GIFT CONFIGURATOR] Variant changed');

      handleVariantChange();

    });

    async function handleVariantChange() {

      try {

        const checked = form.querySelectorAll('.variant-radio:checked');

        if (!checked.length) {
          console.warn('[GIFT CONFIGURATOR] No variant selected.');
          return;
        }

        const combination = Array.from(checked).map(r =>
          parseInt(r.value)
        );

        console.log('[GIFT CONFIGURATOR] Selected combination:', combination);

        // ============================================
        // ODOO JSON-RPC REQUEST
        // ============================================

        const response = await fetch('/website_sale/get_combination_info', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            jsonrpc: "2.0",
            method: "call",
            params: {
              product_template_id: templateId,
              combination: combination,
              add_qty: 1,
              context: {}
            }
          }),
        });

        if (!response.ok) {
          console.error('[GIFT CONFIGURATOR] Network error:', response.status);
          return;
        }

        const result = await response.json();

        console.log('[GIFT CONFIGURATOR] RPC Response:', result);

        if (!result.result) {
          console.error('[GIFT CONFIGURATOR] Invalid RPC result format.');
          return;
        }

        const data = result.result;

        if (!data.product_id) {
          console.warn('[GIFT CONFIGURATOR] No matching variant found.');
          return;
        }

        console.log('[GIFT CONFIGURATOR] Resolved product ID:', data.product_id);
        console.log('[GIFT CONFIGURATOR] Variant price:', data.price);

        // ============================================
        // UPDATE IMAGE
        // ============================================

        const mainImage = document.querySelector('.main-product-image');

        if (mainImage) {
          const newSrc =
            '/web/image/product.product/' +
            data.product_id +
            '/image_1024';

          mainImage.src = newSrc;

          console.log('[GIFT CONFIGURATOR] Image updated:', newSrc);
        } else {
          console.warn('[GIFT CONFIGURATOR] Main image element not found.');
        }

        // ============================================
        // UPDATE PRICE (PRESERVE SYMBOL)
        // ============================================

        const priceEl = document.querySelector('.price');

        if (priceEl) {

          const currentText = priceEl.textContent.trim();
          const symbolMatch = currentText.match(/^\D+/);
          const symbol = symbolMatch ? symbolMatch[0] : '';

          const newPrice =
            symbol + parseFloat(data.price).toFixed(2);

          priceEl.textContent = newPrice;

          console.log('[GIFT CONFIGURATOR] Price updated:', newPrice);

        } else {
          console.warn('[GIFT CONFIGURATOR] Price element not found.');
        }

        // ============================================
        // UPDATE QUOTE BUTTON
        // ============================================

        const quoteBtn = document.querySelector('.js-add-quote');

        if (quoteBtn) {

          quoteBtn.dataset.productId = data.product_id;
          quoteBtn.dataset.productImage =
            '/web/image/product.product/' +
            data.product_id +
            '/image_1920';
          quoteBtn.dataset.productPrice = data.price;

          console.log('[GIFT CONFIGURATOR] Quote button updated.');

        } else {
          console.warn('[GIFT CONFIGURATOR] Quote button not found.');
        }

        // ============================================
        // UPDATE SELECTED LABELS
        // ============================================

        updateSelectedLabels();

      } catch (error) {
        console.error('[GIFT CONFIGURATOR] Fatal error:', error);
      }

    }

    function updateSelectedLabels() {

      const blocks = form.querySelectorAll('.config-block');

      blocks.forEach(block => {

        const selected = block.querySelector('.variant-radio:checked');
        if (!selected) return;

        const valueName = selected.dataset.valueName;

        const label = block.querySelector('.selected-value');

        if (label) {
          label.textContent = valueName;
          console.log('[GIFT CONFIGURATOR] Updated label:', valueName);
        }

      });

    }

  });

})();