(function () {

    "use strict";

    //--------------------------------------------------
    // Pricing Snapshot Helper
    //--------------------------------------------------

    function getPricing(item) {

        const pricing =

            item.pricing_snapshot || {};

        return {

            id:

                pricing.id ||

                item.pricing_tier_id ||

                0,

            qty:

                pricing.qty ||

                item.tier_quantity ||

                item.quantity ||

                1,

            discount:

                pricing.discount ||

                item.discount ||

                0,

            price:

                Number(

                    pricing.price ||

                    item.unit_price ||

                    0

                ),

            currency:

                pricing.currency ||

                item.currency ||

                "AZN",

            tier:

                pricing.tier ||

                item.tier_name ||

                "",

            subtotal:

                Number(

                    item.subtotal ||

                    (

                        (

                            pricing.price ||

                            item.unit_price ||

                            0

                        )

                        *

                        (

                            pricing.qty ||

                            item.quantity ||

                            1

                        )

                    )

                ),

            discount_amount:

                Number(

                    item.discount_amount ||

                    0

                ),

        };

    }

    //--------------------------------------------------
    // Format Currency
    //--------------------------------------------------

    function formatPrice(

        amount,

        currency

    ) {

        return `${currency} ${Number(amount).toFixed(2)}`;

    }

    //--------------------------------------------------
    // Export
    //--------------------------------------------------

    window.PricingUtils = {

        getPricing: getPricing,

        formatPrice: formatPrice,

    };

})();