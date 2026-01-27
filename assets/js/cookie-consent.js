
(function () {
    const GA_ID = 'G-Q9748DKYP4';

    function loadAnalytics() {
        if (window.gaLoaded) return;
        window.gaLoaded = true;

        const gtagScript = document.createElement('script');
        gtagScript.async = true;
        gtagScript.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
        document.head.appendChild(gtagScript);

        window.dataLayer = window.dataLayer || [];
        function gtag() { dataLayer.push(arguments); }
        window.gtag = gtag;

        gtag('js', new Date());
        gtag('config', GA_ID, { anonymize_ip: true });
    }

    function createBanner() {
        const overlay = document.createElement('div');
        overlay.id = 'cookie-overlay';

        const banner = document.createElement('div');
        banner.id = 'cookie-banner';

        banner.innerHTML =
            '<h2>Cookie-Einstellungen</h2>' +
            '<p>Diese Website verwendet Google Analytics zur anonymisierten Auswertung von Zugriffen. ' +
            'Die Verarbeitung erfolgt nur nach Ihrer Einwilligung.</p>' +
            '<div class="buttons">' +
            '<button class="decline" id="cookie-decline">Ablehnen</button>' +
            '<button class="accept" id="cookie-accept">Zustimmen</button>' +
            '</div>';

        overlay.appendChild(banner);
        document.body.appendChild(overlay);

        document.getElementById('cookie-accept').onclick = function () {
            localStorage.setItem('ga-consent', 'true');
            loadAnalytics();
            overlay.remove();
        };

        document.getElementById('cookie-decline').onclick = function () {
            localStorage.setItem('ga-consent', 'false');
            overlay.remove();
        };
    }

    document.addEventListener('DOMContentLoaded', function () {
        const consent = localStorage.getItem('ga-consent');
        if (consent === 'true') {
            loadAnalytics();
        } else if (consent === null) {
            createBanner();
        }
    });
})();
