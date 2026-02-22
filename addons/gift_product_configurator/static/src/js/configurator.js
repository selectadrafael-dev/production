odoo.define('gift_product_configurator.qty_tiers', function (require) {
const publicWidget = require('web.public.widget');

publicWidget.registry.QtyTiers = publicWidget.Widget.extend({

    selector: '#qty_tiers',

    start: function () {

        const tiers = [
            {qty: 50, price: "£7.86"},
            {qty: 100, price: "£6.76"},
            {qty: 250, price: "£6.01"},
            {qty: 500, price: "£5.75"},
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

});
