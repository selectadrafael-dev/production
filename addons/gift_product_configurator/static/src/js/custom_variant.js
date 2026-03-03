/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";
import "@website_sale/js/website_sale"; // Ensure original logic is loaded

publicWidget.registry.GiftCustomProduct = publicWidget.Widget.extend({
    selector: '.oe_website_sale',
    events: {
        'change .js_variant_change': '_onVariantChange',
    },

    _onVariantChange: function (ev) {
        const $parent = $(ev.currentTarget).closest('.config-block');
        const selectedName = $(ev.currentTarget).parent().find('span').text();
        
        // Update the "Selected Value" text in your custom header
        $parent.find('.selected-value').text(selectedName);

        // Odoo 18 triggers a 'variant_change' event on the form.
        // The standard 'website_sale' JS will handle the image and price
        // IF the classes like 'oe_variant_img_main' are present.
    },
});
