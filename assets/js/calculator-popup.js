// Calculator popup module

const CALCULATOR_ACTIVE_POPUP_KEY = "calculator-active-popup-v1";
const CALCULATOR_OPEN_POPUPS_KEY = "calculator-open-popups-v1";
const CALCULATOR_POPUP_POSITIONS_KEY = "calculator-popup-positions-v1";
const KNOWN_CALCULATOR_POPUPS = new Set([
    "lgsPopup",
    "binPopup",
    "constPopup",
    "triPopup",
    "graphPopup",
]);

function saveActiveCalculatorPopup(popupId) {
    try {
        if (!popupId) {
            localStorage.removeItem(CALCULATOR_ACTIVE_POPUP_KEY);
            return;
        }
        localStorage.setItem(CALCULATOR_ACTIVE_POPUP_KEY, popupId);
    } catch {
        // ignore storage issues
    }
}

function loadActiveCalculatorPopup() {
    try {
        const popupId = localStorage.getItem(CALCULATOR_ACTIVE_POPUP_KEY);
        if (!popupId) return null;
        if (!KNOWN_CALCULATOR_POPUPS.has(popupId)) return null;
        return popupId;
    } catch {
        return null;
    }
}

function loadOpenCalculatorPopups() {
    try {
        const raw = localStorage.getItem(CALCULATOR_OPEN_POPUPS_KEY);
        if (!raw) return [];
        const parsed = JSON.parse(raw);
        if (!Array.isArray(parsed)) return [];

        const valid = parsed.filter((popupId) => typeof popupId === "string" && KNOWN_CALCULATOR_POPUPS.has(popupId));
        return [...new Set(valid)];
    } catch {
        return [];
    }
}

function saveOpenCalculatorPopups(popupIds) {
    try {
        const valid = popupIds.filter((popupId) => KNOWN_CALCULATOR_POPUPS.has(popupId));
        if (!valid.length) {
            localStorage.removeItem(CALCULATOR_OPEN_POPUPS_KEY);
            return;
        }
        localStorage.setItem(CALCULATOR_OPEN_POPUPS_KEY, JSON.stringify([...new Set(valid)]));
    } catch {
        // ignore storage issues
    }
}

function setPopupOpenState(popupId, isOpen) {
    const current = loadOpenCalculatorPopups();
    const next = new Set(current);

    if (isOpen) {
        next.add(popupId);
    } else {
        next.delete(popupId);
    }

    saveOpenCalculatorPopups([...next]);
}

function restoreCalculatorPopupState() {
    const overlay = document.getElementById("calculator-overlay");
    if (!overlay || !overlay.classList.contains("open")) return;

    const popupIds = loadOpenCalculatorPopups();
    if (popupIds.length) {
        popupIds.forEach((popupId) => {
            const popup = document.getElementById(popupId);
            if (!popup) return;
            openPopup(popupId);
        });
        return;
    }

    const fallbackPopupId = loadActiveCalculatorPopup();
    if (!fallbackPopupId) return;

    const fallbackPopup = document.getElementById(fallbackPopupId);
    if (!fallbackPopup) {
        saveActiveCalculatorPopup(null);
        return;
    }

    openPopup(fallbackPopupId);
}

window.restoreCalculatorPopupState = restoreCalculatorPopupState;

function loadPopupPositions() {
    try {
        const raw = localStorage.getItem(CALCULATOR_POPUP_POSITIONS_KEY);
        if (!raw) return {};
        const parsed = JSON.parse(raw);
        return parsed && typeof parsed === "object" ? parsed : {};
    } catch {
        return {};
    }
}

function savePopupPositions(positions) {
    try {
        localStorage.setItem(CALCULATOR_POPUP_POSITIONS_KEY, JSON.stringify(positions));
    } catch {
        // ignore storage issues
    }
}

function loadPopupPosition(popupId) {
    const positions = loadPopupPositions();
    const pos = positions[popupId];
    if (!pos || typeof pos !== "object") return null;
    const left = Number(pos.left);
    const top = Number(pos.top);
    if (!Number.isFinite(left) || !Number.isFinite(top)) return null;
    return { left, top };
}

function applyPopupPosition(popupId, position) {
    if (!position) return false;
    const popup = document.getElementById(popupId);
    if (!popup) return false;
    popup.style.left = `${position.left}px`;
    popup.style.top = `${position.top}px`;
    return true;
}

function savePopupPosition(popupId) {
    const popup = document.getElementById(popupId);
    if (!popup) return;

    const left = parseFloat(popup.style.left || "");
    const top = parseFloat(popup.style.top || "");
    if (!Number.isFinite(left) || !Number.isFinite(top)) return;

    const positions = loadPopupPositions();
    positions[popupId] = { left, top };
    savePopupPositions(positions);
}

window.savePopupPosition = savePopupPosition;

window.clearStoredCalculatorPopupState = function clearStoredCalculatorPopupState() {
    saveActiveCalculatorPopup(null);
    saveOpenCalculatorPopups([]);
};

function openPopup(popupId) {
    document.getElementById(popupId.replace('Popup', 'Overlay')).classList.add('open');
    const popup = document.getElementById(popupId);
    popup.classList.add('open');
    bringToFront(popup);
    const hasStoredPosition = applyPopupPosition(popupId, loadPopupPosition(popupId));
    if (!hasStoredPosition) {
        centerPopup(popupId);
    }
    saveActiveCalculatorPopup(popupId);
    setPopupOpenState(popupId, true);
    document.dispatchEvent(new CustomEvent('calculator:popup-opened', { detail: { popupId } }));
}

function closePopup(popupId) {
    document.getElementById(popupId.replace('Popup', 'Overlay')).classList.remove('open');
    document.getElementById(popupId).classList.remove('open');

    const activePopup = loadActiveCalculatorPopup();
    if (activePopup === popupId) {
        saveActiveCalculatorPopup(null);
    }
    setPopupOpenState(popupId, false);
    document.dispatchEvent(new CustomEvent('calculator:popup-closed', { detail: { popupId } }));
}

function returnFocusToMain() {
    panelInputMode = false;
    const mainInput = document.getElementById('mainInput');
    if (mainInput) {
        activeInputField = mainInput;
        mainInput.focus({ preventScroll: true });
    }
}

function focusPanelInput(inputEl) {
    if (!inputEl) return;
    panelInputMode = true;
    activeInputField = inputEl;
    inputEl.focus({ preventScroll: true });
    setInputCursor(inputEl, inputEl.value?.length || 0);
}

function centerPopup(popupId) {
    const popup = document.getElementById(popupId);
    const calculator = document.querySelector('.calculator');
    if (!calculator) return;

    const calcRect = calculator.getBoundingClientRect();

    const xoffset = 0;
    const yoffset = 5;
    const left = calcRect.left + xoffset;
    const top = calcRect.bottom + yoffset;

    popup.style.left = `${left}px`;
    popup.style.top = `${top}px`;
}

document.addEventListener("DOMContentLoaded", () => {
    restoreCalculatorPopupState();
});
