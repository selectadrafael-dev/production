/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.GiftProductRestructure = publicWidget.Widget.extend({
    selector: '#product_detail',
    
    start: function () {
        // Move native components into the custom containers
        this.$('#o-carousel-product').appendTo(this.$('#gift_gallery_placeholder'));
        this.$('.js_add_cart_variants').appendTo(this.$('#gift_variant_form_placeholder'));
        
        return this._super.apply(this, arguments);
    },

    events: {
        'change .js_variant_change': '_onUpdateHeader',
    },

    _onUpdateHeader: function (ev) {
        // Updates the "Attribute: Value" label in your custom headers
        const $input = $(ev.currentTarget);
        const $block = $input.closest('.variant_attribute');
        const valName = $input.parent().find('span').text();
        $block.find('.selected-value').text(valName);
    },
});
