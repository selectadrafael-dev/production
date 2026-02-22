odoo.define('gift_product_configurator.frontend', function (require) {

'use strict';

const publicWidget = require('web.public.widget');

/* =====================================================
Variant Selection (highlight active)
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
}

});

/* =====================================================
Quantity Stepper (+ / −)
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
    if (value > 1) input.value = value - 1;
}

});

/* =====================================================
Tier Selection → Sets Quantity
===================================================== */
publicWidget.registry.TierSelect = publicWidget.Widget.extend({

selector: '#qty_tiers',

events: {
    'click .tier-card': '_selectTier',
},

_selectTier: function (ev) {

    const $card = $(ev.currentTarget);

    // Highlight active tier
    this.$('.tier-card').removeClass('active');
    $card.addClass('active');

    // Extract quantity from card
    const qty = parseInt($card.find('strong').text());

    // Update quantity input
    const input = document.querySelector('.custom-qty input');
    if (input) input.value = qty;
}

});

/* =====================================================
Quote Drawer (slide panel)
===================================================== */
publicWidget.registry.QuoteDrawer = publicWidget.Widget.extend({

selector: 'body',

events: {
    'click #openQuote': '_open',
    'click .drawer-close': '_close',
},

_open: function () {
    const drawer = document.getElementById('quoteDrawer');
    if (drawer) drawer.classList.add('active');
},

_close: function () {
    const drawer = document.getElementById('quoteDrawer');
    if (drawer) drawer.classList.remove('active');
}

});

});
