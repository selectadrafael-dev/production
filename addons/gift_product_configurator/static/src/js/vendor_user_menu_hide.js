(function () {

    'use strict';

    console.log('Vendor menu script loaded');

    document.addEventListener('DOMContentLoaded', function () {

        // Delay slightly to ensure menu renders
        setTimeout(function () {

            // Detect vendor by checking body data or visible UI
            const bodyText = document.body.innerText || '';

            // OPTIONAL:
            // Safer vendor detection can later be improved via backend variable

            const isVendor =
                bodyText.includes('Website') &&
                !bodyText.includes('Apps');

            console.log('Vendor detected:', isVendor);

            if (!isVendor) {
                return;
            }

            // Hide dropdown menu items
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