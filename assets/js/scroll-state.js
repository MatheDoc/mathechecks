(function () {
    "use strict";

    const STORAGE_PREFIX = "page-scroll-v1";
    const MAX_RESTORE_ATTEMPTS = 60;
    const RESTORE_INTERVAL_MS = 100;
    const SAVE_THROTTLE_MS = 150;

    let lastSaveAt = 0;
    let hasRestored = false;

    function getPageKey() {
        const path = (window.location.pathname || "").toLowerCase();
        const search = window.location.search || "";
        return `${path}${search}`;
    }

    function getStorageKey() {
        const lernbereich = window.lernbereich || "global";
        return `${STORAGE_PREFIX}:${lernbereich}:${getPageKey()}`;
    }

    function saveScrollPosition(force = false) {
        const now = Date.now();
        if (!force && now - lastSaveAt < SAVE_THROTTLE_MS) {
            return;
        }

        lastSaveAt = now;

        try {
            localStorage.setItem(
                getStorageKey(),
                JSON.stringify({
                    y: window.scrollY || window.pageYOffset || 0,
                    ts: now,
                })
            );
        } catch (err) {
            console.warn("Scroll-State konnte nicht gespeichert werden", err);
        }
    }

    function loadStoredY() {
        try {
            const raw = localStorage.getItem(getStorageKey());
            if (!raw) return null;
            const parsed = JSON.parse(raw);
            const y = Number(parsed?.y);
            if (!Number.isFinite(y) || y < 0) return null;
            return y;
        } catch {
            return null;
        }
    }

    function canRestore(y) {
        const doc = document.documentElement;
        const body = document.body;
        const maxScroll = Math.max(
            (doc?.scrollHeight || 0) - window.innerHeight,
            (body?.scrollHeight || 0) - window.innerHeight,
            0
        );
        return maxScroll >= y;
    }

    function restoreScrollPosition() {
        if (hasRestored) return;
        if (window.location.hash) return;

        const y = loadStoredY();
        if (y === null) return;

        let attempts = 0;

        const tryRestore = () => {
            attempts += 1;

            if (canRestore(y) || attempts >= MAX_RESTORE_ATTEMPTS) {
                window.scrollTo({ top: y, behavior: "auto" });
                hasRestored = true;
                return;
            }

            setTimeout(tryRestore, RESTORE_INTERVAL_MS);
        };

        setTimeout(tryRestore, 0);
    }

    function setup() {
        if ("scrollRestoration" in history) {
            history.scrollRestoration = "manual";
        }

        document.addEventListener(
            "scroll",
            () => {
                saveScrollPosition(false);
            },
            { passive: true }
        );

        window.addEventListener("pagehide", () => saveScrollPosition(true));
        window.addEventListener("beforeunload", () => saveScrollPosition(true));
        document.addEventListener("visibilitychange", () => {
            if (document.visibilityState === "hidden") {
                saveScrollPosition(true);
            }
        });

        restoreScrollPosition();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", setup, { once: true });
    } else {
        setup();
    }
})();
