odoo.define('gift_product_configurator.vendor_user_menu_hide', function (require) {
    'use strict';

    const session = require('web.session');
    const registry = require('@web/core/registry');

    const userMenuRegistry = registry.registry.category('user_menuitems');

    session.user_has_group(
        'gift_product_configurator.group_product_vendor'
    ).then(function (isVendor) {

        if (!isVendor) {
            return;
        }

        // Remove menu items
        userMenuRegistry.remove('documentation');
        userMenuRegistry.remove('support');
        userMenuRegistry.remove('shortcuts');
        userMenuRegistry.remove('odoo_account');
        userMenuRegistry.remove('account');
        userMenuRegistry.remove('preferences');
        userMenuRegistry.remove('onboarding');

    });

});