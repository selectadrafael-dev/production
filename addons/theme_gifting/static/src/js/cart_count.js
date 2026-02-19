odoo.define('theme_gifting.cart_count', function (require) {
    "use strict";

    const publicWidget = require('web.public.widget');

    publicWidget.registry.GiftingCartCount = publicWidget.Widget.extend({
        selector: '.cart-icon',

        start: function () {
            fetch('/shop/cart/update_json', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({})
            })
            .then(res => res.json())
            .then(data => {
                const qty = data.cart_quantity || 0;
                const badge = this.el.querySelector('.cart-count');

                if (qty > 0) {
                    badge.textContent = qty;
                    badge.style.display = 'inline-block';
                }
            });

            return this._super(...arguments);
        },
    });
});
