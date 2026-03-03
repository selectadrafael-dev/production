/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.GiftProductRestructure = publicWidget.Widget.extend({
    selector: '#product_detail',
    
    start: function () {
        // Relocate Odoo's functional parts into your custom layout
        this.$('#o-carousel-product').appendTo(this.$('#gift_gallery_hook'));
        this.$('.js_add_cart_variants').appendTo(this.$('#gift_variant_hook'));
        
        return this._super.apply(this, arguments);
    }
});
