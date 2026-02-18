// Calculator popup module

function openPopup(popupId) {
    document.getElementById(popupId.replace('Popup', 'Overlay')).classList.add('open');
    const popup = document.getElementById(popupId);
    popup.classList.add('open');
    bringToFront(popup);
    centerPopup(popupId);
}

function closePopup(popupId) {
    document.getElementById(popupId.replace('Popup', 'Overlay')).classList.remove('open');
    document.getElementById(popupId).classList.remove('open');
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

    const xoffset = 60;
    const yoffset = 50;
    const left = calcRect.left + xoffset;
    const top = calcRect.top - yoffset;

    popup.style.left = `${left}px`;
    popup.style.top = `${top}px`;
}
