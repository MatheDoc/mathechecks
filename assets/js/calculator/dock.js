// Taschenrechner-Fenster: Öffnen/Schließen, Andocken rechts (breite Viewports) bzw. Overlay, Breite per Griff.
(() => {
    const OPEN_STATE_KEY = 'calculator-overlay-open-v1';
    const WIDTH_KEY = 'calculator-dock-width-v1';
    // Muss mit dem Breakpoint in calculator.css übereinstimmen.
    const DOCK_MEDIA_QUERY = '(min-width: 800px)';
    const MIN_WIDTH = 320;
    const DEFAULT_MAX_WIDTH = 480;
    const MIN_CONTENT_WIDTH = 440;
    const KEY_STEP = 16;

    const root = document.documentElement;
    const overlay = document.getElementById('calculator-overlay');
    const resizer = document.getElementById('calculatorDockResizer');
    const topbar = document.querySelector('.shell > .topbar');
    const toggleButtons = Array.from(document.querySelectorAll('.calculator-toggle, #calculatorToggleMenu'));

    function readStorage(key) {
        try {
            return localStorage.getItem(key);
        } catch {
            return null;
        }
    }

    function writeStorage(key, value) {
        try {
            if (value === null) {
                localStorage.removeItem(key);
            } else {
                localStorage.setItem(key, value);
            }
        } catch {
            // Ignore storage errors.
        }
    }

    function clamp(value, min, max) {
        return Math.min(Math.max(value, min), max);
    }

    function isOpen() {
        return Boolean(overlay?.classList.contains('open'));
    }

    let pendingLayoutNotification = 0;

    // Inhalte mit eigener Resize-Logik (z. B. Plotly) reagieren nur auf window-resize.
    function notifyLayoutChange() {
        if (pendingLayoutNotification) return;
        pendingLayoutNotification = window.requestAnimationFrame(() => {
            pendingLayoutNotification = 0;
            window.dispatchEvent(new Event('resize'));
        });
    }

    // ── Breite ──

    let appliedWidth = null;
    let userWidth = Number.parseInt(readStorage(WIDTH_KEY), 10) || null;

    function getWidthBounds() {
        const viewportWidth = window.innerWidth;
        const max = Math.min(Math.round(viewportWidth * 0.6), viewportWidth - MIN_CONTENT_WIDTH);
        return { min: MIN_WIDTH, max: Math.max(MIN_WIDTH, max) };
    }

    function applyWidth(width) {
        const { min, max } = getWidthBounds();
        const nextWidth = clamp(Math.round(width), min, max);
        if (resizer) {
            resizer.setAttribute('aria-valuemin', String(min));
            resizer.setAttribute('aria-valuemax', String(max));
            resizer.setAttribute('aria-valuenow', String(nextWidth));
        }
        if (nextWidth === appliedWidth) return nextWidth;

        appliedWidth = nextWidth;
        root.style.setProperty('--calculator-dock-w', `${nextWidth}px`);
        if (isOpen() && window.matchMedia(DOCK_MEDIA_QUERY).matches) {
            notifyLayoutChange();
        }
        return nextWidth;
    }

    function syncWidth() {
        const defaultWidth = Math.min(Math.round(window.innerWidth / 3), DEFAULT_MAX_WIDTH);
        applyWidth(userWidth ?? defaultWidth);
    }

    function setUserWidth(width, { persist = true } = {}) {
        userWidth = width === null ? null : applyWidth(width);
        if (width === null) syncWidth();
        if (persist) writeStorage(WIDTH_KEY, userWidth === null ? null : String(userWidth));
    }

    function syncTop() {
        const bottom = topbar ? Math.max(0, Math.round(topbar.getBoundingClientRect().bottom)) : 0;
        root.style.setProperty('--calculator-dock-top', `${bottom}px`);
    }

    function bindResizer() {
        if (!resizer) return;
        let activePointerId = null;

        const finishResize = (event) => {
            if (event.pointerId !== activePointerId) return;
            activePointerId = null;
            root.classList.remove('calculator-resizing');
            writeStorage(WIDTH_KEY, String(userWidth));
        };

        resizer.addEventListener('pointerdown', (event) => {
            if (event.button !== 0) return;
            activePointerId = event.pointerId;
            resizer.setPointerCapture?.(event.pointerId);
            root.classList.add('calculator-resizing');
            event.preventDefault();
        });

        resizer.addEventListener('pointermove', (event) => {
            if (event.pointerId !== activePointerId) return;
            setUserWidth(window.innerWidth - event.clientX, { persist: false });
        });

        resizer.addEventListener('pointerup', finishResize);
        resizer.addEventListener('pointercancel', finishResize);
        resizer.addEventListener('dblclick', () => setUserWidth(null));

        resizer.addEventListener('keydown', (event) => {
            const step = event.shiftKey ? KEY_STEP * 4 : KEY_STEP;
            const { min, max } = getWidthBounds();
            const targets = {
                ArrowLeft: appliedWidth + step,
                ArrowRight: appliedWidth - step,
                Home: min,
                End: max,
            };
            if (!(event.key in targets)) return;
            event.preventDefault();
            setUserWidth(targets[event.key]);
        });
    }

    // ── Öffnen / Schließen ──

    function updateToggleButtons(open) {
        toggleButtons.forEach((button) => {
            button.classList.toggle('is-active', open);
            button.classList.toggle('active', open);
            button.setAttribute('aria-pressed', open ? 'true' : 'false');
        });
    }

    function toggleCalculatorOverlay(forceOpen) {
        if (!overlay) {
            root.classList.remove('calculator-open');
            return;
        }

        const wasOpen = isOpen();
        const shouldOpen = typeof forceOpen === 'boolean' ? forceOpen : !wasOpen;

        overlay.classList.toggle('open', shouldOpen);
        overlay.setAttribute('aria-hidden', shouldOpen ? 'false' : 'true');
        root.classList.toggle('calculator-open', shouldOpen);
        writeStorage(OPEN_STATE_KEY, shouldOpen ? '1' : '0');
        updateToggleButtons(shouldOpen);
        if (shouldOpen !== wasOpen) {
            notifyLayoutChange();
            window.dispatchEvent(new CustomEvent('calculator:visibility', { detail: { open: shouldOpen } }));
        }

        if (!shouldOpen) {
            window.clearStoredCalculatorPopupState?.();
            return;
        }

        window.restoreCalculatorPopupState?.();
        window.setTimeout(() => {
            if (typeof window.focusCalculatorMainInput === 'function') {
                window.focusCalculatorMainInput();
                return;
            }
            document.getElementById('mainInput')?.focus();
        }, 100);
    }

    window.toggleCalculatorOverlay = toggleCalculatorOverlay;

    const menuButton = document.getElementById('calculatorToggleMenu');
    if (menuButton && menuButton.dataset.boundCalculator !== 'true') {
        menuButton.dataset.boundCalculator = 'true';
        menuButton.addEventListener('click', () => toggleCalculatorOverlay());
    }

    syncTop();
    syncWidth();
    bindResizer();
    if (topbar && typeof ResizeObserver === 'function') {
        new ResizeObserver(syncTop).observe(topbar);
    }
    window.addEventListener('resize', () => {
        syncTop();
        syncWidth();
    });

    if (readStorage(OPEN_STATE_KEY) === '1') {
        toggleCalculatorOverlay(true);
    } else {
        root.classList.remove('calculator-open');
        updateToggleButtons(false);
    }
})();
