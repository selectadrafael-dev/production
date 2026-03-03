/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.GiftVariantUpdate = publicWidget.Widget.extend({
    selector: '.oe_website_sale',
    
    start: function () {
        // Kill the zoom feature for this page to prevent the 'dataset' crash
        if (this.$('#o-carousel-product').length) {
            this.$('#o-carousel-product').data('zoom', 0);
        }
        return this._super.apply(this, arguments);
    },

    events: {
        'change .js_variant_change': '_onVariantChange',
    },

    _onVariantChange: function (ev) {
        const $input = $(ev.currentTarget);
        const $block = $input.closest('.config-block');
        
        // Update Label Text
        const valName = $input.data('value_name');
        if (valName) {
            $block.find('.selected-value').text(valName);
        }

        // Update Active Class
        $block.find('.variant-btn').removeClass('active');
        $input.closest('.variant-btn').addClass('active');
    },
});
