odoo.define('theme_atk_navy.countdown', [], function () {
    'use strict';
   
 //console.log('ATK COUNTDOWN SCRIPT EXECUTED');

    const LAUNCH_DATE = new Date('2026-01-19T00:01:00-05:00').getTime();

    function startCountdown() {
        //console.log('ATK COUNTDOWN STARTED');

        const timer = setInterval(() => {
            const now = Date.now();
            const distance = LAUNCH_DATE - now;

            if (distance <= 0) {
                clearInterval(timer);
                return;
            }

            const days = Math.floor(distance / (1000 * 60 * 60 * 24));
            const hours = Math.floor((distance / (1000 * 60 * 60)) % 24);
            const minutes = Math.floor((distance / (1000 * 60)) % 60);
            const seconds = Math.floor((distance / 1000) % 60);

            const map = {
                'atk-days': days,
                'atk-hours': hours,
                'atk-minutes': minutes,
                'atk-seconds': seconds,
            };

            Object.entries(map).forEach(([id, value]) => {
                const el = document.getElementById(id);
                if (el) {
                    el.textContent = String(value).padStart(2, '0');
                }
            });
        }, 1000);
    }

    // 🔑 ODOO-SAFE WAIT LOOP
    const waitForDom = setInterval(() => {
        if (document.getElementById('atk-days')) {
            clearInterval(waitForDom);
            startCountdown();
        }
    }, 100);
});
