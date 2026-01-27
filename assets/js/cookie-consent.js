
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
        const banner = document.createElement('div');
        banner.id = 'cookie-banner';
        banner.innerHTML = `
      <div style="max-width:800px;margin:auto;">
        Diese Website verwendet Google Analytics zur anonymisierten Auswertung von Zugriffen.
        <button id="cookie-accept">Zustimmen</button>
        <button id="cookie-decline">Ablehnen</button>
      </div>
    `;
        document.body.appendChild(banner);

        document.getElementById('cookie-accept').onclick = function () {
            localStorage.setItem('ga-consent', 'true');
            loadAnalytics();
            banner.remove();
        };

        document.getElementById('cookie-decline').onclick = function () {
            localStorage.setItem('ga-consent', 'false');
            banner.remove();
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
