(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {

    const form = document.querySelector('.o_custom_variant_form');
    if (!form) return;

    const templateId = form.dataset.productTemplateId;

    form.addEventListener('change', async function (e) {

      if (!e.target.classList.contains('variant-radio')) return;

      updateSelectedLabels();

      const checked = form.querySelectorAll('.variant-radio:checked');
      if (!checked.length) return;

      const combination = Array.from(checked).map(r => parseInt(r.value));

      // ===== CALL ODOO VARIANT API =====
      const response = await fetch('/website_sale/get_combination_info', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_template_id: parseInt(templateId),
          combination: combination,
          add_qty: 1,
        }),
      });

      const result = await response.json();
      const data = result.result;

      if (!data || !data.product_id) return;

      // ===== UPDATE IMAGE =====
      const mainImage = document.querySelector('.main-product-image');
      if (mainImage) {
        mainImage.src =
          '/web/image/product.product/' +
          data.product_id +
          '/image_1024';
      }

      // ===== UPDATE PRICE (KEEP SYMBOL) =====
      const priceEl = document.querySelector('.price');
      if (priceEl) {
        const symbol = priceEl.textContent.trim().charAt(0);
        priceEl.textContent =
          symbol + parseFloat(data.price).toFixed(2);
      }

      // ===== UPDATE QUOTE BUTTON =====
      const quoteBtn = document.querySelector('.js-add-quote');
      if (quoteBtn) {
        quoteBtn.dataset.productId = data.product_id;
        quoteBtn.dataset.productImage =
          '/web/image/product.product/' +
          data.product_id +
          '/image_1920';
        quoteBtn.dataset.productPrice = data.price;
      }

    });

    //======================================
    // UPDATE "Colour: Navy", "Size: 2XS"
    //======================================
    function updateSelectedLabels() {

      const blocks = form.querySelectorAll('.config-block');

      blocks.forEach(block => {

        const selected = block.querySelector('.variant-radio:checked');
        if (!selected) return;

        const name = selected.dataset.valueName;

        const label = block.querySelector('.selected-value');
        if (label) label.textContent = name;

      });

    }

  });

})();