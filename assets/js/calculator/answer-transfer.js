// Übernahme von Rechner-Ergebnissen in Antwortfelder.
// Ziel ist das zuletzt angeklickte Antwortfeld; bei offenem Rechner trägt es oben links ein kleines 🧮-Abzeichen.
// Die Wert-Chips im Verlauf (history.js) schreiben über window.CalculatorAnswerTarget in dieses Feld.
(() => {
    const TARGET_SELECTOR = [
        '.check-card__runtime-task .answer-input:not(select)',
        '.check-card__runtime-task .answer-numopt-input',
        '.cw-input',
    ].join(', ');
    // Freitextfelder: Wert an der Cursorposition einfügen statt den Inhalt zu ersetzen.
    const FREE_TEXT_SELECTOR = '.recall-input-slot, .fy-explain-input';

    let target = null;

    const badge = document.createElement('span');
    badge.className = 'calc-target-badge';
    badge.setAttribute('aria-hidden', 'true');
    badge.title = 'Ziel für Werte aus dem Taschenrechner';
    badge.textContent = '🧮';

    function isUsable(field) {
        return Boolean(field && field.isConnected && !field.disabled && !field.readOnly);
    }

    function placeBadge() {
        const host = target?.parentElement;
        if (!host) {
            badge.remove();
            return;
        }
        host.classList.add('calc-target-host');
        host.appendChild(badge);
        badge.style.left = `${target.offsetLeft}px`;
        badge.style.top = `${target.offsetTop}px`;
    }

    function setTarget(field) {
        if (field === target) return;
        target?.parentElement?.classList.remove('calc-target-host');
        target = field;
        placeBadge();
    }

    function insertInto(field, value) {
        const current = String(field.value || '');
        if (field.matches(FREE_TEXT_SELECTOR) && current) {
            const start = Number.isInteger(field.selectionStart) ? field.selectionStart : current.length;
            const end = Number.isInteger(field.selectionEnd) ? field.selectionEnd : start;
            const before = current.slice(0, start);
            const after = current.slice(end);
            const insertion = `${before && !/\s$/.test(before) ? ' ' : ''}${value}${after && !/^\s/.test(after) ? ' ' : ''}`;
            field.value = before + insertion + after;
            const caret = before.length + insertion.length;
            field.setSelectionRange?.(caret, caret);
        } else {
            field.value = value;
        }
        field.dispatchEvent(new Event('input', { bubbles: true }));
        field.dispatchEvent(new Event('change', { bubbles: true }));
    }

    function flash(element, className, duration = 900) {
        element?.classList.add(className);
        window.setTimeout(() => element?.classList.remove(className), duration);
    }

    function isReady() {
        if (isUsable(target)) return true;
        if (target) setTarget(null);
        return false;
    }

    /** Schreibt den Wert ins Zielfeld. Liefert false, wenn kein Zielfeld aktiv ist. */
    function transfer(value, chip) {
        if (!isReady()) return false;
        insertInto(target, value);
        target.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        flash(target, 'calc-target--filled');
        flash(chip, 'is-done', 700);
        return true;
    }

    function hint(active) {
        badge.classList.toggle('is-hint', Boolean(active) && isUsable(target));
    }

    window.CalculatorAnswerTarget = { isReady, transfer, hint };

    document.addEventListener('focusin', (event) => {
        const field = event.target;
        if (!(field instanceof HTMLElement) || field.closest('#calculator-overlay')) return;
        if (field.matches(TARGET_SELECTOR) && isUsable(field)) setTarget(field);
    });

    // Layout ändert sich mit Rechnerbreite und Fenstergröße.
    window.addEventListener('resize', () => {
        if (target) placeBadge();
    });
})();
