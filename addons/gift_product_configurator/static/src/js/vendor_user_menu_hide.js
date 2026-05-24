(function () {

    'use strict';

    console.log('Vendor menu script loaded');

    document.addEventListener('DOMContentLoaded', function () {

        setTimeout(function () {

            const isVendor =
                document.body.classList.contains('vendor-user');

            console.log('Vendor detected:', isVendor);

            if (!isVendor) {
                return;
            }

            document.querySelectorAll('.dropdown-item').forEach(function (item) {

                const text = item.innerText.trim();

                if (
                    text === 'Documentation' ||
                    text === 'Support' ||
                    text === 'Onboarding' ||
                    text === 'Preferences' ||
                    text === 'My Odoo.com account' ||
                    text === 'Shortcuts'
                ) {
                    item.style.display = 'none';
                }

            });

            console.log('Vendor menu items hidden');

        }, 1000);

    });

})();