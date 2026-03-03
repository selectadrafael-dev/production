/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.GiftVariantUpdate = publicWidget.Widget.extend({
    selector: '.oe_website_sale',
    
    start: function () {
        // Force-disable zoom data to stop the calculation script
        const $carousel = this.$('#o-carousel-product');
        if ($carousel.length) {
            $carousel.data('zoom', 0);
            $carousel.attr('data-zoom', '0');
        }
        return this._super.apply(this, arguments);
    },

    events: {
        'change .js_variant_change': '_onVariantChange',
    },

    _onVariantChange: function (ev) {
        const $input = $(ev.currentTarget);
        const $block = $input.closest('.config-block');
        
        // 1. Update text label (e.g., Color: Red)
        const valName = $input.data('value_name');
        if (valName) {
            $block.find('.selected-value').text(valName);
        }

        // 2. Visual active state for buttons
        $block.find('.variant-btn').removeClass('active');
        $input.closest('.variant-btn').addClass('active');
    },
});
