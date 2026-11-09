// Rechner-Verlauf (eigener Menüpunkt, Standard): letzte Rechnungen pro Gerät, neueste unten.
// Klick auf die Rechnung holt sie zurück in die Eingabe; Wert-Chips gehen ins markierte Antwortfeld
// (answer-transfer.js), ohne Antwortfeld in die Eingabe. ↑/↓ im Main-Input wie in einer Konsole.
(() => {
    const STORAGE_KEY = 'calculator-history-v1';
    const MAX_ENTRIES = 20;

    const section = document.getElementById('calculatorHistory');
    const list = document.getElementById('calculatorHistoryList');
    const emptyHint = document.getElementById('calculatorHistoryEmpty');
    const clearButton = document.getElementById('calculatorHistoryClear');
    const mainInput = document.getElementById('mainInput');
    const scroller = document.querySelector('.calculator-panels');
    const modeSelect = document.getElementById('calculatorModeSelect');
    if (!section || !list || !mainInput) return;

    function load() {
        try {
            const parsed = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
            return Array.isArray(parsed) ? parsed.filter((entry) => entry && typeof entry.input === 'string') : [];
        } catch {
            return [];
        }
    }

    function save() {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(entries));
        } catch {
            // Ignore storage errors.
        }
    }

    let entries = load();
    // Position beim Blättern mit ↑/↓; -1 = aktueller Entwurf.
    let historyIndex = -1;
    let draft = '';

    function createChip(text, title, onClick) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'calculator-history__chip';
        button.textContent = text;
        button.title = title;
        button.addEventListener('click', onClick);
        return button;
    }

    // Neuester Eintrag steht unten, direkt über Ergebnis und Eingabe.
    function scrollToLatest() {
        if (!scroller || modeSelect?.value !== 'history') return;
        window.requestAnimationFrame(() => {
            scroller.scrollTop = scroller.scrollHeight;
        });
    }

    function render() {
        list.replaceChildren(...entries.slice().reverse().map((entry) => {
            const item = document.createElement('li');
            item.className = 'calculator-history__item';

            const inputButton = document.createElement('button');
            inputButton.type = 'button';
            inputButton.className = 'calculator-history__input';
            inputButton.textContent = entry.input;
            inputButton.title = 'Rechnung erneut in die Eingabe übernehmen';
            inputButton.addEventListener('click', () => window.CalculatorApi?.setInput(entry.input));

            const results = document.createElement('div');
            results.className = 'calculator-history__results';
            const values = Array.isArray(entry.values) ? entry.values : [];
            if (values.length) {
                values.forEach(({ label, value }) => {
                    const chip = createChip(
                        label ? `${label}=${value}` : value,
                        'Ins markierte Antwortfeld übernehmen (ohne Antwortfeld: in die Eingabe)',
                        () => {
                            if (window.CalculatorAnswerTarget?.transfer(value, chip)) return;
                            window.CalculatorApi?.insert(value);
                        }
                    );
                    chip.addEventListener('mouseenter', () => window.CalculatorAnswerTarget?.hint(true));
                    chip.addEventListener('mouseleave', () => window.CalculatorAnswerTarget?.hint(false));
                    results.appendChild(chip);
                });
            } else {
                const text = document.createElement('span');
                text.className = 'calculator-history__text';
                text.textContent = entry.text;
                results.appendChild(text);
            }

            item.append(inputButton, results);
            return item;
        }));
        const isEmpty = entries.length === 0;
        if (emptyHint) emptyHint.hidden = !isEmpty;
        if (clearButton) clearButton.hidden = isEmpty;
        scrollToLatest();
    }

    window.addEventListener('calculator:result', (event) => {
        const { input, text, values, isError, kind } = event.detail || {};
        if (!input || isError || kind !== 'text') return;
        if (entries[0]?.input === input && entries[0]?.text === text) return;
        entries = [{ input, text, values: values || [] }, ...entries].slice(0, MAX_ENTRIES);
        save();
        render();
        historyIndex = -1;
    });

    clearButton?.addEventListener('click', () => {
        entries = [];
        save();
        render();
    });

    // ↑/↓ blättern durch frühere Eingaben; der aktuelle Entwurf bleibt erhalten.
    mainInput.addEventListener('keydown', (event) => {
        if (event.key !== 'ArrowUp' && event.key !== 'ArrowDown') return;
        if (!entries.length) return;

        const nextIndex = event.key === 'ArrowUp'
            ? Math.min(historyIndex + 1, entries.length - 1)
            : historyIndex - 1;
        if (nextIndex === historyIndex) return;
        event.preventDefault();

        if (historyIndex === -1) draft = mainInput.value;
        historyIndex = Math.max(nextIndex, -1);
        mainInput.value = historyIndex === -1 ? draft : entries[historyIndex].input;
        mainInput.setSelectionRange(mainInput.value.length, mainInput.value.length);
        mainInput.dispatchEvent(new Event('input', { bubbles: true }));
    });

    mainInput.addEventListener('input', (event) => {
        if (event.isTrusted) historyIndex = -1;
    });

    modeSelect?.addEventListener('change', scrollToLatest);
    window.addEventListener('calculator:visibility', (event) => {
        if (event.detail?.open) scrollToLatest();
    });

    render();
})();
