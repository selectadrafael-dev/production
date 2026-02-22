odoo.define('gift_product_configurator.frontend', function (require) {

'use strict';

const publicWidget = require('web.public.widget');

/* =====================================================
   Quantity Tier Cards
===================================================== */
publicWidget.registry.QtyTiers = publicWidget.Widget.extend({

    selector: '#qty_tiers',

    start: function () {

        const tiers = [
            { qty: 50,  price: "£7.86" },
            { qty: 100, price: "£6.76" },
            { qty: 250, price: "£6.01" },
            { qty: 500, price: "£5.75" },
        ];

        let html = '';

        tiers.forEach(t => {
            html += `
                <div class="tier-card">
                    <strong>${t.qty}+</strong>
                    <span>${t.price} each</span>
                </div>
            `;
        });

        this.$el.html(html);
    }
});


/* =====================================================
   Variant Selection
===================================================== */
publicWidget.registry.VariantSelect = publicWidget.Widget.extend({

    selector: '.variant-section',

    events: {
        'click .variant-option': '_onSelect',
    },

    _onSelect: function (ev) {

        const $btn = $(ev.currentTarget);

        $btn
            .closest('.variant-options')
            .find('.variant-option')
            .removeClass('active');

        $btn.addClass('active');

        // Future: trigger price recalculation
    }
});


/* =====================================================
   Quantity Input Control
===================================================== */
publicWidget.registry.QuantityControl = publicWidget.Widget.extend({

    selector: '.custom-qty',

    events: {
        'click .qty-plus': '_plus',
        'click .qty-minus': '_minus',
    },

    _plus: function () {

        const input = this.$('input')[0];
        const value = parseInt(input.value) || 0;

        input.value = value + 1;
    },

    _minus: function () {

        const input = this.$('input')[0];
        const value = parseInt(input.value) || 1;

        if (value > 1) {
            input.value = value - 1;
        }
    }
});

});
