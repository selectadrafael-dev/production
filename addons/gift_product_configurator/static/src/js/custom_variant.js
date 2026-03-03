/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc_service";

publicWidget.registry.GiftVariantUpdate = publicWidget.Widget.extend({
    selector: '#gift_product_detail',
    events: {
        'change .js_gift_variant_change': '_onVariantChange',
    },

    _onVariantChange: async function (ev) {
        const $input = $(ev.currentTarget);
        const $block = $input.closest('.config-block');
        
        // 1. Update UI Labels
        $block.find('.selected-value').text($input.data('value_name'));
        $block.find('.variant-btn').removeClass('active');
        $input.closest('.variant-btn').addClass('active');

        // 2. Collect selected values
        const combination = this.$('.js_gift_variant_change:checked').map((i, el) => parseInt($(el).val())).get();
        const productTemplateId = parseInt(this.$('.o_gift_variant_form').data('product-template-id'));

        // 3. Fetch data from Odoo
        const data = await rpc('/website_sale/get_combination_info', {
            product_template_id: productTemplateId,
            combination: combination,
        });

        // 4. Update Image and Price
        if (data.product_id) {
            this.$('#gift_main_image').attr('src', `/web/image/product.product/${data.product_id}/image_1024`);
        }
        if (data.price) {
            this.$('#gift_price_container').html(data.price);
        }
    },
});
