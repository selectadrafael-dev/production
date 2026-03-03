/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.GiftVariantUpdate = publicWidget.Widget.extend({
    selector: '.oe_website_sale',
    events: {
        'change .js_variant_change': '_onVariantChange',
    },

    /**
     * Handles visual updates when a radio button is clicked
     */
    _onVariantChange: function (ev) {
        const $input = $(ev.currentTarget);
        const $block = $input.closest('.config-block');
        
        // 1. Update the "Selected Value" text header
        const valName = $input.data('value_name');
        if (valName) {
            $block.find('.selected-value').text(valName);
        }

        // 2. Manage visual 'active' classes for your custom buttons
        $block.find('.variant-btn').removeClass('active');
        $input.closest('.variant-btn').addClass('active');

        // 3. Update 'Product Code' if it's visible
        // Odoo's core JS handles price/image, but we help it find our custom spans
    },
});
