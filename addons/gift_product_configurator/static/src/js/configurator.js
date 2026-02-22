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
        'change input': '_updatePrice',
    },

    _plus: function () {
        const input = this.$('input')[0];
        const value = parseInt(input.value) || 0;
        input.value = value + 1;
        this._updatePrice();
    },

    _minus: function () {
        const input = this.$('input')[0];
        const value = parseInt(input.value) || 1;
        if (value > 1) input.value = value - 1;
        this._updatePrice();
    },

    _updatePrice: function () {

        const qty = parseInt(this.$('input').val());

        // Simple demo pricing logic
        let price = 7.86;

        if (qty >= 500) price = 5.75;
        else if (qty >= 250) price = 6.01;
        else if (qty >= 100) price = 6.76;

        $('#dynamic_price span').text('£' + price.toFixed(2));
    }
});


/* =====================================================
   Tier Card Selection → Set Quantity
===================================================== */
publicWidget.registry.TierSelect = publicWidget.Widget.extend({

    selector: '#qty_tiers',

    events: {
        'click .tier-card': '_selectTier',
    },

    _selectTier: function (ev) {

        const $card = $(ev.currentTarget);

        // Highlight selected tier
        this.$('.tier-card').removeClass('active');
        $card.addClass('active');

        // Extract quantity from card text
        const qty = parseInt($card.find('strong').text());

        // Update quantity input
        const input = $('.custom-qty input')[0];
        if (input) input.value = qty;
    }
});

});
