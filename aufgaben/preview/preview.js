import { renderTask } from "../runtime/task-render.js";

const gebietSelect = document.getElementById('gebietSelect');
const lernbereichSelect = document.getElementById('lernbereichSelect');
const sammlungSelect = document.getElementById('sammlungSelect');
const loadBtn = document.getElementById('loadBtn');
const showSolutions = document.getElementById('showSolutions');
const statusEl = document.getElementById('status');
const listEl = document.getElementById('list');
const CONFIG_PATH = '../project_config.json';
const SELECTION_STORAGE_KEY = 'aufgaben.preview.selection';

const catalog = {};

function toPreviewPath(relativePath) {
    return `../exports/json/${relativePath}`;
}

function loadStoredSelection() {
    try {
        const raw = window.localStorage.getItem(SELECTION_STORAGE_KEY);
        if (!raw) {
            return { gebiet: '', lernbereich: '', sammlung: '' };
        }
        const parsed = JSON.parse(raw);
        return {
            gebiet: typeof parsed?.gebiet === 'string' ? parsed.gebiet : '',
            lernbereich: typeof parsed?.lernbereich === 'string' ? parsed.lernbereich : '',
            sammlung: typeof parsed?.sammlung === 'string' ? parsed.sammlung : '',
        };
    } catch {
        return { gebiet: '', lernbereich: '', sammlung: '' };
    }
}

function storeSelection() {
    const selection = {
        gebiet: gebietSelect.value || '',
        lernbereich: lernbereichSelect.value || '',
        sammlung: sammlungSelect.value || '',
    };
    try {
        window.localStorage.setItem(SELECTION_STORAGE_KEY, JSON.stringify(selection));
    } catch {
        // Ignorieren, falls localStorage nicht verfügbar ist.
    }
}

function resetSelect(selectEl, placeholder) {
    selectEl.innerHTML = '';
    const option = document.createElement('option');
    option.value = '';
    option.textContent = placeholder;
    selectEl.appendChild(option);
    selectEl.value = '';
    selectEl.disabled = true;
}

function fillSelect(selectEl, values, placeholder) {
    resetSelect(selectEl, placeholder);
    if (!Array.isArray(values) || values.length === 0) {
        return;
    }

    values.forEach((value) => {
        const option = document.createElement('option');
        option.value = value;
        option.textContent = value;
        selectEl.appendChild(option);
    });

    selectEl.disabled = false;
    selectEl.value = values[0];
}

function buildCatalog(entries) {
    Object.keys(catalog).forEach((key) => {
        delete catalog[key];
    });

    if (!Array.isArray(entries)) {
        return false;
    }

    entries.forEach((entry) => {
        if (typeof entry !== 'string') {
            return;
        }

        const parts = entry.split('/');
        if (parts.length < 3) {
            return;
        }

        const gebiet = parts[0];
        const lernbereich = parts[1];
        const fileName = parts.slice(2).join('/');
        const sammlung = fileName.endsWith('.json') ? fileName.slice(0, -5) : fileName;

        if (!catalog[gebiet]) {
            catalog[gebiet] = {};
        }
        if (!catalog[gebiet][lernbereich]) {
            catalog[gebiet][lernbereich] = [];
        }

        catalog[gebiet][lernbereich].push({ sammlung, relativePath: entry });
    });

    const gebiete = Object.keys(catalog);
    return gebiete.length > 0;
}

function refreshLernbereichSelection(preferredLernbereich = '') {
    const gebiet = gebietSelect.value;
    const lernbereiche = gebiet && catalog[gebiet]
        ? Object.keys(catalog[gebiet]).sort((a, b) => a.localeCompare(b, 'de'))
        : [];

    fillSelect(lernbereichSelect, lernbereiche, 'Bitte Lernbereich wählen');
    if (preferredLernbereich && lernbereiche.includes(preferredLernbereich)) {
        lernbereichSelect.value = preferredLernbereich;
    }
}

function refreshSammlungSelection(preferredSammlung = '') {
    const gebiet = gebietSelect.value;
    const lernbereich = lernbereichSelect.value;
    const entries = (gebiet && lernbereich && catalog[gebiet]?.[lernbereich]) ? catalog[gebiet][lernbereich] : [];

    sammlungSelect.innerHTML = '';
    const placeholder = document.createElement('option');
    placeholder.value = '';
    placeholder.textContent = 'Bitte Sammlung wählen';
    sammlungSelect.appendChild(placeholder);

    if (entries.length === 0) {
        sammlungSelect.value = '';
        sammlungSelect.disabled = true;
        return;
    }

    const sortedEntries = entries
        .slice()
        .sort((a, b) => a.sammlung.localeCompare(b.sammlung, 'de'));

    sortedEntries
        .forEach((entry) => {
            const option = document.createElement('option');
            option.value = entry.relativePath;
            option.textContent = entry.sammlung;
            sammlungSelect.appendChild(option);
        });

    sammlungSelect.disabled = false;
    sammlungSelect.value = sortedEntries[0].relativePath;
    if (preferredSammlung && sortedEntries.some((entry) => entry.relativePath === preferredSammlung)) {
        sammlungSelect.value = preferredSammlung;
    }
}

function setSelectionOptions(entries) {
    const hasEntries = buildCatalog(entries);
    if (!hasEntries) {
        resetSelect(gebietSelect, 'Keine Gebiete gefunden');
        resetSelect(lernbereichSelect, 'Keine Lernbereiche gefunden');
        resetSelect(sammlungSelect, 'Keine Sammlungen gefunden');
        return false;
    }

    const storedSelection = loadStoredSelection();
    const gebiete = Object.keys(catalog).sort((a, b) => a.localeCompare(b, 'de'));
    fillSelect(gebietSelect, gebiete, 'Bitte Gebiet wählen');
    if (storedSelection.gebiet && gebiete.includes(storedSelection.gebiet)) {
        gebietSelect.value = storedSelection.gebiet;
    }

    refreshLernbereichSelection(storedSelection.lernbereich);
    refreshSammlungSelection(storedSelection.sammlung);
    storeSelection();

    return true;
}

function buildEntriesFromConfig(config) {
    const entries = [];
    const outputDir = config?.defaults?.outputDir ?? 'aufgaben/exports/json';

    for (const job of config?.jobs ?? []) {
        for (const target of job?.targets ?? []) {
            const gebiet = (target.gebiet ?? 'unsorted').trim();
            const lernbereich = (target.lernbereich ?? 'unsorted').trim();
            const sammlung = (target.sammlung ?? 'unknown').trim();
            entries.push(`${gebiet}/${lernbereich}/${sammlung}.json`);
        }
    }

    for (const entry of config?.static ?? []) {
        const gebiet = (entry.gebiet ?? 'unsorted').trim();
        const lernbereich = (entry.lernbereich ?? 'unsorted').trim();
        const sammlung = (entry.sammlung ?? 'unknown').trim();
        entries.push(`${gebiet}/${lernbereich}/${sammlung}.json`);
    }

    return entries;
}

async function loadConfigOptions() {
    try {
        const response = await fetch(CONFIG_PATH, { cache: 'no-store' });
        if (!response.ok) {
            return;
        }

        const config = await response.json();
        const entries = buildEntriesFromConfig(config);
        setSelectionOptions(entries);
    } catch {
        resetSelect(gebietSelect, 'Config nicht geladen');
        resetSelect(lernbereichSelect, 'Config nicht geladen');
        resetSelect(sammlungSelect, 'Config nicht geladen');
    }
}

function setStatus(message, isError = false) {
    statusEl.textContent = message;
    statusEl.classList.toggle('error', isError);
}

function typesetMath() {
    if (window.MathJax?.typesetPromise) {
        window.MathJax.typesetPromise().catch(() => { });
    }
}

async function loadJsonAndRender() {
    const relativePath = sammlungSelect.value.trim();
    if (!relativePath) {
        setStatus('Bitte zuerst eine Sammlung auswählen.', true);
        return;
    }

    const path = toPreviewPath(relativePath);

    setStatus('Lade JSON ...');
    listEl.innerHTML = '';

    try {
        const response = await fetch(path);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const payload = await response.json();
        if (!Array.isArray(payload)) {
            throw new Error('JSON ist kein Array.');
        }

        payload.forEach((task, index) => {
            listEl.appendChild(renderTask(task, { index, showSolution: showSolutions.checked }));
        });

        setStatus(`${payload.length} Aufgaben geladen: ${relativePath}`);
        typesetMath();
    } catch (error) {
        setStatus(`Fehler beim Laden: ${error.message}`, true);
    }
}

loadBtn.addEventListener('click', loadJsonAndRender);
gebietSelect.addEventListener('change', () => {
    refreshLernbereichSelection();
    refreshSammlungSelection();
    storeSelection();
    loadJsonAndRender();
});
lernbereichSelect.addEventListener('change', () => {
    refreshSammlungSelection();
    storeSelection();
    loadJsonAndRender();
});
sammlungSelect.addEventListener('change', () => {
    storeSelection();
    loadJsonAndRender();
});
showSolutions.addEventListener('change', loadJsonAndRender);

loadConfigOptions().finally(loadJsonAndRender);
