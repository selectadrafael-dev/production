odoo.define('gift_product_configurator.vendor_user_menu_hide', function (require) {
    'use strict';

    console.log('Vendor menu JS loaded');

    const session = require('web.session');

    session.user_has_group(
        'gift_product_configurator.group_product_vendor'
    ).then(function (isVendor) {

        console.log('Is Vendor:', isVendor);

        if (!isVendor) {
            return;
        }

        // Hide menu items
        setTimeout(function () {

            $('div[data-menu="documentation"]').hide();
            $('div[data-menu="support"]').hide();
            $('div[data-menu="onboarding"]').hide();
            $('div[data-menu="odoo_account"]').hide();
            $('div[data-menu="preferences"]').hide();

            console.log('Vendor dropdown menus hidden');

        }, 1000);

    });

});