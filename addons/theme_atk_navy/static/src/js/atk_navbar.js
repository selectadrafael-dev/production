document.addEventListener('DOMContentLoaded', function () {

    const toggle = document.querySelector('.atk-nav-toggle');
    const links = document.querySelector('.atk-nav-links');

    if (!toggle || !links) return;

    toggle.addEventListener('click', function () {
        document.body.classList.toggle('atk-nav-open');
    });

    //Close menu when clicking a link (mobile UX)
    links.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            document.body.classList.remove('atk-nav-open');
        });
    });
});
