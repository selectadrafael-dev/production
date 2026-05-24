/** @odoo-module **/

import { registry } from "@web/core/registry";
import { session } from "@web/session";

console.log("Vendor menu JS loaded");

const userMenuRegistry = registry.category("user_menuitems");

async function hideVendorMenus() {

    const isVendor = await session.user_has_group(
        "gift_product_configurator.group_product_vendor"
    );

    console.log("Is Vendor:", isVendor);

    if (!isVendor) {
        return;
    }

    userMenuRegistry.remove("documentation");
    userMenuRegistry.remove("support");
    userMenuRegistry.remove("shortcuts");
    userMenuRegistry.remove("preferences");
    userMenuRegistry.remove("odoo_account");
    userMenuRegistry.remove("onboarding");

    console.log("Vendor menus removed");
}

hideVendorMenus();