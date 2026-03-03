/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";
import { ProductConfiguratorWidget } from "@website_sale/js/website_sale_utils";

publicWidget.registry.GiftVariantUpdate = publicWidget.Widget.extend({
    selector: '.oe_website_sale',
    events: {
        'change .js_variant_change': '_onVariantChange',
    },

    _onVariantChange: function (ev) {
        const $input = $(ev.currentTarget);
        const $block = $input.closest('.config-block');
        
        // 1. Update the "Selected Value" text in the header
        const valName = $input.data('value_name');
        if (valName) {
            $block.find('.selected-value').text(valName);
        }

        // 2. Visual state for buttons
        $block.find('.variant-btn').removeClass('active');
        $input.closest('.variant-btn').addClass('active');

        // 3. Manually trigger Odoo's core variant logic
        // This ensures the price and image swap even if the standard carousel is missing
        this.trigger_up('variant_value_changed', {
            $parent: this.$el,
            variant_id: $input.val(),
        });
    },
});
