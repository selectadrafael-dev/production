/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";

publicWidget.registry.GiftVariantUpdate = publicWidget.Widget.extend({
    selector: '#custom_product_detail', // Target our new custom ID
    events: {
        'change .js_custom_variant_change': '_onVariantChange',
    },

    _onVariantChange: function (ev) {
        const $input = $(ev.currentTarget);
        const $parent = this.$el;
        
        // 1. UI Updates (Text/Labels)
        $input.closest('.config-block').find('.selected-value').text($input.data('value_name'));
        $input.closest('.config-block').find('.variant-btn').removeClass('active');
        $input.closest('label').addClass('active');

        // 2. Fetch Variant Data (Price/Image) via RPC
        const productTemplateId = parseInt($('.o_custom_variant_form').data('product-template-id'));
        const variantValues = this.$('.js_custom_variant_change:checked').map((i, el) => parseInt($(el).val())).get();

        jsonrpc('/website_sale/get_combination_info', {
            product_template_id: productTemplateId,
            combination: variantValues,
        }).then((data) => {
            // Update Image
            if (data.display_image) {
                this.$('.js_variant_img_target').attr('src', '/web/image/product.product/' + data.product_id + '/image_1024');
            }
            // Update Price
            if (data.price) {
                this.$('.js_custom_price_wrapper').html(data.price);
            }
        });
    },
});
