const gebietSelect = document.getElementById('gebietSelect');
const lernbereichSelect = document.getElementById('lernbereichSelect');
const sammlungSelect = document.getElementById('sammlungSelect');
const loadBtn = document.getElementById('loadBtn');
const showSolutions = document.getElementById('showSolutions');
const statusEl = document.getElementById('status');
const listEl = document.getElementById('list');
const MANIFEST_PATH = '../exports/json/manifest.json';
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

async function loadManifestOptions() {
    try {
        const response = await fetch(MANIFEST_PATH, { cache: 'no-store' });
        if (!response.ok) {
            return;
        }

        const entries = await response.json();
        setSelectionOptions(entries);
    } catch {
        resetSelect(gebietSelect, 'Manifest nicht geladen');
        resetSelect(lernbereichSelect, 'Manifest nicht geladen');
        resetSelect(sammlungSelect, 'Manifest nicht geladen');
    }
}

function setStatus(message, isError = false) {
    statusEl.textContent = message;
    statusEl.classList.toggle('error', isError);
}

function escapeHtml(text) {
    return text
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
}

function parseMcOptions(raw) {
    return raw
        .split(/(?<!\\)~/)
        .map((option) => option.trim())
        .filter((option) => option.length > 0)
        .map((option) => {
            const correct = option.startsWith('=');
            return {
                correct,
                label: correct ? option.slice(1).trim() : option
            };
        });
}

function replaceAnswerPlaceholders(answerText, renderPlaceholder) {
    const result = [];
    let index = 0;

    while (index < answerText.length) {
        const start = answerText.indexOf('{', index);
        if (start === -1) {
            result.push(answerText.slice(index));
            break;
        }

        result.push(answerText.slice(index, start));

        const maybePlaceholder = answerText.slice(start);
        const match = maybePlaceholder.match(/^\{(\d+):(NUMERICAL|MC):/);
        if (!match) {
            result.push('{');
            index = start + 1;
            continue;
        }

        let braceLevel = 1;
        let end = start + 1;
        while (end < answerText.length && braceLevel > 0) {
            if (answerText[end] === '{') braceLevel += 1;
            if (answerText[end] === '}') braceLevel -= 1;
            end += 1;
        }

        if (braceLevel !== 0) {
            result.push(answerText.slice(start));
            break;
        }

        const id = match[1];
        const kind = match[2];
        const prefix = `{${id}:${kind}:`;
        const fullMatch = answerText.slice(start, end);
        const raw = fullMatch.slice(prefix.length, -1);

        result.push(renderPlaceholder(kind, raw));
        index = end;
    }

    return result.join('');
}

function answerToPreview(answerText) {
    return replaceAnswerPlaceholders(answerText, (kind, raw) => {
        if (kind === 'NUMERICAL') {
            return '<input class="answer-input" type="text" placeholder="Antwort" />';
        }

        const options = parseMcOptions(raw)
            .map((option) => `<option>${escapeHtml(option.label)}</option>`)
            .join('');

        return `<select class="answer-select"><option selected disabled>Bitte w\u00e4hlen</option>${options}</select>`;
    });
}

function answerToSolution(answerText) {
    return replaceAnswerPlaceholders(answerText, (kind, raw) => {
        if (kind === 'NUMERICAL') {
            const numericalMatch = raw.match(/=([^:}]+):([^:}]+)/);
            if (!numericalMatch) {
                return '<span class="solution-badge">NUMERICAL</span>';
            }
            const value = escapeHtml(numericalMatch[1]);
            const tolerance = escapeHtml(numericalMatch[2]);
            return `<span class="solution-badge">${value} (±${tolerance})</span>`;
        }

        const correct = parseMcOptions(raw).find((option) => option.correct);
        if (!correct) {
            return '<span class="solution-badge">MC</span>';
        }
        return `<span class="solution-badge">${escapeHtml(correct.label)}</span>`;
    });
}

function toNumber(value, fallback) {
    const numeric = Number(value);
    return Number.isFinite(numeric) ? numeric : fallback;
}

function buildPlotlyFigure(spec) {
    const figure = { data: [], layout: {} };
    const specType = String(spec?.type ?? 'plotly').toLowerCase();

    if (specType === 'economic-curves') {
        const params = typeof spec?.params === 'object' && spec.params ? spec.params : {};
        const k3 = toNumber(params.k3, 0.05);
        const k2 = toNumber(params.k2, -1.0);
        const k1 = toNumber(params.k1, 10.0);
        const k0 = toNumber(params.k0, 80.0);
        const price = toNumber(params.price, 20.0);
        const capacity = Math.max(1, toNumber(params.capacity, 40.0));
        const points = Math.max(40, Math.trunc(toNumber(spec?.points, 300)));

        const x = [];
        const e = [];
        const k = [];
        const g = [];
        for (let i = 0; i < points; i += 1) {
            const xi = (capacity * i) / (points - 1);
            const ei = price * xi;
            const ki = k3 * (xi ** 3) + k2 * (xi ** 2) + k1 * xi + k0;
            x.push(xi);
            e.push(ei);
            k.push(ki);
            g.push(ei - ki);
        }

        figure.data.push(
            { x, y: e, mode: 'lines', name: 'E(x)', line: { color: '#2ca02c' } },
            { x, y: k, mode: 'lines', name: 'K(x)', line: { color: '#d62728' } },
            { x, y: g, mode: 'lines', name: 'G(x)', line: { color: '#1f77b4' } }
        );

        figure.layout = {
            title: 'Erlös-, Kosten- und Gewinnfunktion',
            xaxis: { title: 'Menge x' },
            yaxis: { title: 'Wert' },
            shapes: [
                {
                    type: 'line',
                    x0: capacity,
                    x1: capacity,
                    yref: 'paper',
                    y0: 0,
                    y1: 1,
                    line: { dash: 'dot', width: 1 },
                },
            ],
        };
    } else if (specType === 'cost-curves') {
        const params = typeof spec?.params === 'object' && spec.params ? spec.params : {};
        const k3 = toNumber(params.k3, 0.05);
        const k2 = toNumber(params.k2, -1.0);
        const k1 = toNumber(params.k1, 10.0);
        const k0 = toNumber(params.k0, 80.0);
        const maxX = Math.max(1, toNumber(params.maxX, 30.0));
        const startX = 0.5;
        const points = Math.max(40, Math.trunc(toNumber(spec?.points, 300)));

        const x = [];
        const gk = [];
        const k = [];
        const kv = [];
        for (let i = 0; i < points; i += 1) {
            const xi = startX + ((maxX - startX) * i) / (points - 1);
            x.push(xi);
            gk.push(3 * k3 * (xi ** 2) + 2 * k2 * xi + k1);
            k.push(k3 * (xi ** 2) + k2 * xi + k1 + (k0 / xi));
            kv.push(k3 * (xi ** 2) + k2 * xi + k1);
        }

        figure.data.push(
            { x, y: gk, mode: 'lines', name: 'GK(x)', line: { color: '#1f77b4' } },
            { x, y: k, mode: 'lines', name: 'k(x)', line: { color: '#d62728' } },
            { x, y: kv, mode: 'lines', name: 'kv(x)', line: { color: '#2ca02c' } }
        );

        figure.layout = {
            title: 'Grenzkosten-, Stückkosten- und variable Stückkostenfunktion',
            xaxis: { title: 'Menge x', range: [0, maxX] },
            yaxis: { title: 'Kosten' },
        };
    } else if (specType === 'market-curves') {
        const params = typeof spec?.params === 'object' && spec.params ? spec.params : {};
        const supplySlope = Math.max(0.01, toNumber(params.supplySlope, 1.2));
        const demandSlope = Math.max(0.01, toNumber(params.demandSlope, 1.8));
        const minPrice = toNumber(params.minPrice, 5.0);
        const maxPrice = toNumber(params.maxPrice, 20.0);
        const maxX = Math.max(5, toNumber(params.maxX, 20.0));
        const points = Math.max(40, Math.trunc(toNumber(spec?.points, 220)));

        const x = [];
        const supply = [];
        const demand = [];
        for (let i = 0; i < points; i += 1) {
            const xi = (maxX * i) / (points - 1);
            x.push(xi);
            supply.push(supplySlope * xi + minPrice);
            demand.push(-demandSlope * xi + maxPrice);
        }

        const eqX = (maxPrice - minPrice) / (supplySlope + demandSlope);
        const eqY = supplySlope * eqX + minPrice;

        figure.data.push(
            { x, y: supply, mode: 'lines', name: 'Angebot p_A(x)', line: { color: '#d62728' } },
            { x, y: demand, mode: 'lines', name: 'Nachfrage p_N(x)', line: { color: '#1f77b4' } }
        );

        figure.layout = {
            title: 'Angebots- und Nachfragefunktion',
            xaxis: { title: 'Menge x', range: [0, maxX] },
            yaxis: { title: 'Preis p', range: [0, Math.max(maxPrice, eqY) * 1.15] },
        };
    } else if (specType === 'market-equilibrium' || specType === 'market-abschoepfung') {
        const params = typeof spec?.params === 'object' && spec.params ? spec.params : {};
        const supplyP = params.supply ?? {};
        const demandP = params.demand ?? {};
        const eqX = toNumber(params.eqX, 10);
        const eqP = toNumber(params.eqP, 10);
        const maxX = Math.max(1, toNumber(params.maxX, 30));
        const points = Math.max(40, Math.trunc(toNumber(spec?.points, 260)));

        function evalFn(p, x) {
            if (p.type === 'linear') return (p.a ?? 1) * x + (p.b ?? 0);
            if (p.type === 'quadratic') return (p.a ?? 0) * x * x + (p.b ?? 0) * x + (p.c ?? 0);
            if (p.type === 'exp') return (p.A ?? 1) * Math.exp(-(p.rate ?? 0.1) * x) + (p.c ?? 0);
            return 0;
        }

        const x = [];
        const supply = [];
        for (let i = 0; i < points; i += 1) {
            const xi = (maxX * i) / (points - 1);
            x.push(xi);
            supply.push(evalFn(supplyP, xi));
        }

        const satX = specType === 'market-equilibrium' ? Math.max(eqX * 1.02, toNumber(params.satX, maxX)) : maxX;
        const demandPoints = Math.max(40, Math.round(points * satX / maxX));
        const xDemand = [];
        const demand = [];
        for (let i = 0; i < demandPoints; i += 1) {
            const xi = (satX * i) / (demandPoints - 1);
            xDemand.push(xi);
            demand.push(evalFn(demandP, xi));
        }

        if (specType === 'market-abschoepfung') {
            const x2 = toNumber(params.x2, 5);
            const p2 = toNumber(params.p2, 15);

            const kr2CurveX = Array.from({ length: 81 }, (_, i) => x2 * i / 80);
            const kr2CurveY = kr2CurveX.map((xi) => evalFn(demandP, xi));
            const kr2X = [0, x2, ...kr2CurveX.slice().reverse()];
            const kr2Y = [p2, p2, ...kr2CurveY.slice().reverse()];

            const kr1CurveX = Array.from({ length: 81 }, (_, i) => x2 + (eqX - x2) * i / 80);
            const kr1CurveY = kr1CurveX.map((xi) => evalFn(demandP, xi));
            const kr1X = [x2, eqX, ...kr1CurveX.slice().reverse()];
            const kr1Y = [eqP, eqP, ...kr1CurveY.slice().reverse()];

            figure.data.push(
                { x: kr2X, y: kr2Y, mode: 'lines', name: 'KR2', line: { width: 0 }, fill: 'toself', fillcolor: 'rgba(59, 130, 246, 0.25)' },
                { x: kr1X, y: kr1Y, mode: 'lines', name: 'KR1', line: { width: 0 }, fill: 'toself', fillcolor: 'rgba(16, 185, 129, 0.25)' },
                { x, y: supply, mode: 'lines', name: 'Angebot p_A(x)', line: { color: '#d62728' } },
                { x, y: demand, mode: 'lines', name: 'Nachfrage p_N(x)', line: { color: '#1f77b4' } },
            );
            const maxY = Math.max(toNumber(params.maxY, 30), p2) * 1.12;
            figure.layout = {
                title: 'Preisdifferenzierung mit KR1 und KR2',
                xaxis: { title: 'Menge x', range: [0, maxX] },
                yaxis: { title: 'Preis p', range: [0, maxY] },
                shapes: [
                    { type: 'line', x0: x2, x1: x2, y0: 0, y1: p2, line: { color: '#374151', dash: 'dot' } },
                    { type: 'line', x0: eqX, x1: eqX, y0: 0, y1: eqP, line: { color: '#374151', dash: 'dot' } },
                    { type: 'line', x0: 0, x1: x2, y0: p2, y1: p2, line: { color: '#374151', dash: 'dot' } },
                    { type: 'line', x0: 0, x1: eqX, y0: eqP, y1: eqP, line: { color: '#374151', dash: 'dot' } },
                ],
                annotations: [
                    { x: x2, y: -0.08, xref: 'x', yref: 'paper', text: 'x_2', showarrow: false },
                    { x: eqX, y: -0.08, xref: 'x', yref: 'paper', text: 'x_G', showarrow: false },
                    { x: 0, y: p2, xref: 'paper', yref: 'y', xanchor: 'right', text: 'p_2', showarrow: false },
                    { x: 0, y: eqP, xref: 'paper', yref: 'y', xanchor: 'right', text: 'p_G', showarrow: false },
                ],
            };
        } else {
            figure.data.push(
                { x, y: supply, mode: 'lines', name: 'Angebot p_A(x)', line: { color: '#d62728' } },
                { x: xDemand, y: demand, mode: 'lines', name: 'Nachfrage p_N(x)', line: { color: '#1f77b4' } },
            );
            const maxY = toNumber(params.maxY, Math.max(eqP, evalFn(demandP, 0)) * 1.12);
            figure.layout = {
                title: 'Angebots- und Nachfragefunktion',
                xaxis: { title: 'Menge x', range: [0, maxX] },
                yaxis: { title: 'Preis p', range: [0, maxY] },
            };
        }
    } else if (specType === 'ab-tree') {
        // Baumdiagramm im Stil von zeichneBaumdiagramm.js
        const pa = toNumber(spec?.pa, 0.5);
        const pba = toNumber(spec?.pba, 0.5);
        const pbna = toNumber(spec?.pbna, 0.5);
        const givenSlots = new Set(Array.isArray(spec?.givenSlots) ? spec.givenSlots : []);

        const pna = 1 - pa;
        const pnba = 1 - pba;
        const pnbna = 1 - pbna;
        const pAB = pa * pba;
        const pAnB = pa * pnba;
        const pnAB = pna * pbna;
        const pnAnB = pna * pnbna;

        // Slot-Werte (Slots 1..6 auf 2 NKS, 7..10 auf 4 NKS)
        const slotValues = {
            1: pa, 2: pna, 3: pba, 4: pnba, 5: pbna, 6: pnbna,
            7: pAB, 8: pAnB, 9: pnAB, 10: pnAnB,
        };
        const circledDigits = {
            1: '①', 2: '②', 3: '③', 4: '④', 5: '⑤',
            6: '⑥', 7: '⑦', 8: '⑧', 9: '⑨', 10: '⑩',
        };
        function fmtSlot(idx) {
            const v = slotValues[idx];
            if (givenSlots.has(idx)) {
                return idx <= 6 ? v.toFixed(2) : v.toFixed(4);
            }
            return circledDigits[idx] ?? String(idx);
        }

        // Knoten-Positionen (identisch zu zeichneBaumdiagramm.js)
        const nodes = [
            { x: 0, y: 0.5 },      // Start
            { x: 0.5, y: 0.75 },    // A
            { x: 0.5, y: 0.25 },    // ¬A
            { x: 1, y: 0.875 },     // B|A
            { x: 1, y: 0.625 },     // ¬B|A
            { x: 1, y: 0.375 },     // B|¬A
            { x: 1, y: 0.125 },     // ¬B|¬A
        ];

        const nodeLabels = ['', 'A', 'A\u0305', 'B', 'B\u0305', 'B', 'B\u0305'];

        // Kanten
        const edgePairs = [
            [0, 1], [0, 2], [1, 3], [1, 4], [2, 5], [2, 6],
        ];
        // Slot-Index pro Kante
        const edgeSlots = [1, 2, 3, 4, 5, 6];

        const edgeShapes = edgePairs.map(([fi, ti]) => ({
            type: 'line',
            x0: nodes[fi].x, y0: nodes[fi].y,
            x1: nodes[ti].x, y1: nodes[ti].y,
            line: { width: 2, color: 'gray' },
            layer: 'below',
        }));

        // Kanten-Labels (Slot-Nummern oder Werte)
        const edgeAnnotations = edgePairs.map(([fi, ti], i) => {
            const xm = (nodes[fi].x + nodes[ti].x) / 2;
            const ym = (nodes[fi].y + nodes[ti].y) / 2;
            const isFirstStage = fi === 0;
            const goesUp = nodes[ti].y > nodes[fi].y;
            const yOff = isFirstStage
                ? (goesUp ? -0.08 : 0.08)
                : (goesUp ? -0.05 : 0.05);
            const slotIdx = edgeSlots[i];
            const isGiven = givenSlots.has(slotIdx);
            return {
                x: xm, y: ym - yOff,
                text: fmtSlot(slotIdx),
                showarrow: false,
                font: { size: 18, color: '#111827' },
            };
        });

        // Blatt-Labels (Pfad-Wahrscheinlichkeiten = Slots 7..10)
        const leafSlots = [7, 8, 9, 10];
        const leafNodes = [3, 4, 5, 6];
        const leafAnnotations = leafNodes.map((ni, i) => {
            const slotIdx = leafSlots[i];
            const isGiven = givenSlots.has(slotIdx);
            return {
                x: nodes[ni].x + 0.15,
                y: nodes[ni].y,
                text: fmtSlot(slotIdx),
                showarrow: false,
                font: { size: 18, color: '#111827' },
            };
        });

        // Knoten-Trace (blaue Kreise wie zeichneBaumdiagramm.js)
        figure.data.push({
            x: nodes.map(n => n.x),
            y: nodes.map(n => n.y),
            text: nodeLabels,
            mode: 'markers+text',
            type: 'scatter',
            textposition: 'middle center',
            textfont: { size: 20 },
            marker: {
                size: nodes.map((_, i) => (i === 0 ? 0 : 40)),
                color: '#b3e0ff',
                opacity: 1,
                line: { width: 2, color: 'gray' },
                symbol: 'circle',
            },
            hoverinfo: 'none',
        });

        figure.layout = {
            xaxis: { visible: false, range: [0, 1.4] },
            yaxis: { visible: false, range: [0, 1] },
            shapes: edgeShapes,
            annotations: [...edgeAnnotations, ...leafAnnotations],
            margin: { l: 20, r: 20, t: 20, b: 20 },
            dragmode: false,
        };
    } else {
        const traces = Array.isArray(spec?.traces) ? spec.traces : [];
        traces.forEach((trace) => {
            if (!trace || typeof trace !== 'object') {
                return;
            }
            const plotlyTrace = {
                x: Array.isArray(trace.x) ? trace.x : [],
                y: Array.isArray(trace.y) ? trace.y : [],
                mode: trace.mode ?? 'lines',
                name: trace.name,
                type: trace.kind ?? 'scatter',
            };
            if (trace.line != null) {
                plotlyTrace.line = trace.line;
            }
            if (trace.marker != null) {
                plotlyTrace.marker = trace.marker;
            }
            if (trace.fill != null) {
                plotlyTrace.fill = trace.fill;
            }
            if (trace.fillcolor != null) {
                plotlyTrace.fillcolor = trace.fillcolor;
            }
            if (trace.text != null) {
                plotlyTrace.text = trace.text;
            }
            if (trace.textposition != null) {
                plotlyTrace.textposition = trace.textposition;
            }
            if (trace.textfont != null) {
                plotlyTrace.textfont = trace.textfont;
            }
            if (trace.showlegend != null) {
                plotlyTrace.showlegend = trace.showlegend;
            }
            if (trace.opacity != null) {
                plotlyTrace.opacity = trace.opacity;
            }
            if (trace.hoverinfo != null) {
                plotlyTrace.hoverinfo = trace.hoverinfo;
            }
            figure.data.push(plotlyTrace);
        });
    }

    if (spec?.layout && typeof spec.layout === 'object') {
        figure.layout = { ...figure.layout, ...spec.layout };
    }

    return figure;
}

function buildVftTable(spec) {
    const slots = typeof spec?.slots === 'object' && spec.slots ? spec.slots : {};
    const givenSlots = new Set(Array.isArray(spec?.givenSlots) ? spec.givenSlots.map(Number) : []);
    const circled = { 1: '①', 2: '②', 3: '③', 4: '④', 5: '⑤', 6: '⑥', 7: '⑦', 8: '⑧' };

    function cell(idx) {
        if (givenSlots.has(idx)) {
            return Number(slots[String(idx)]).toFixed(4);
        }
        return circled[idx] ?? String(idx);
    }

    const thStyle = 'border:1px solid #000;padding:4px 10px;background:#f3f4f6';
    const tdStyle = 'border:1px solid #000;padding:4px 10px;text-align:center';
    const tdBoldStyle = 'border:2px solid #000;padding:4px 10px;text-align:center';
    const trTopStyle = 'border-top:2px solid #000';

    const table = document.createElement('table');
    table.style.cssText = 'border-collapse:collapse;text-align:center;margin:8px 0';

    table.innerHTML = `
        <tr>
            <th style="${thStyle}"></th>
            <th style="${thStyle}">\\(P(A)\\)</th>
            <th style="${thStyle}">\\(P(\\overline{A})\\)</th>
            <th style="${tdBoldStyle}"></th>
        </tr>
        <tr>
            <th style="${thStyle}">\\(P(B)\\)</th>
            <td style="${tdStyle}">${cell(1)}</td>
            <td style="${tdStyle}">${cell(3)}</td>
            <td style="${tdBoldStyle}">${cell(7)}</td>
        </tr>
        <tr>
            <th style="${thStyle}">\\(P(\\overline{B})\\)</th>
            <td style="${tdStyle}">${cell(2)}</td>
            <td style="${tdStyle}">${cell(4)}</td>
            <td style="${tdBoldStyle}">${cell(8)}</td>
        </tr>
        <tr style="${trTopStyle}">
            <th style="${thStyle}"></th>
            <td style="${tdStyle}">${cell(5)}</td>
            <td style="${tdStyle}">${cell(6)}</td>
            <td style="${tdBoldStyle}">1</td>
        </tr>`;

    return table;
}

function renderVisual(task, wrapper) {
    const visual = task?.visual;
    const spec = visual?.spec;
    if (!spec || typeof spec !== 'object') {
        return;
    }

    const specType = String(spec?.type ?? '').toLowerCase();

    // VFT: DOM-Tabelle, kein Plotly nötig
    if (specType === 'vft') {
        const tableWrapper = document.createElement('div');
        tableWrapper.className = 'intro';
        tableWrapper.appendChild(buildVftTable(spec));
        wrapper.appendChild(tableWrapper);
        return;
    }

    if (!window.Plotly) {
        return;
    }

    const plotContainer = document.createElement('div');
    plotContainer.className = 'intro';
    wrapper.appendChild(plotContainer);

    const figure = buildPlotlyFigure(spec);
    if (!Array.isArray(figure.data) || figure.data.length === 0) {
        return;
    }

    window.Plotly.newPlot(
        plotContainer,
        figure.data,
        {
            ...figure.layout,
            template: 'plotly_white',
            legend: {
                orientation: 'h',
                x: 0.5,
                xanchor: 'center',
                y: -0.2,
                yanchor: 'top',
            },
            margin: { l: 40, r: 20, t: 35, b: 90 },
        },
        { responsive: true, displaylogo: false }
    );
}

function renderTask(task, index, showSolution) {
    const wrapper = document.createElement('article');
    wrapper.className = 'task';

    const title = document.createElement('h2');
    title.textContent = `Aufgabe ${index + 1}`;
    wrapper.appendChild(title);

    const intro = document.createElement('div');
    intro.className = 'intro';
    intro.innerHTML = task.einleitung ?? '';
    wrapper.appendChild(intro);

    renderVisual(task, wrapper);

    const fragen = Array.isArray(task.fragen) ? task.fragen : [];
    const antworten = Array.isArray(task.antworten) ? task.antworten : [];
    const itemCount = Math.min(fragen.length, antworten.length);

    const qaList = document.createElement('ol');
    qaList.className = 'qa-list';

    for (let i = 0; i < itemCount; i += 1) {
        const item = document.createElement('li');
        item.className = 'qa-item';

        const frage = document.createElement('div');
        frage.className = 'frage';
        frage.textContent = fragen[i];
        item.appendChild(frage);

        const answerPreview = document.createElement('div');
        answerPreview.className = 'answer-preview';
        answerPreview.innerHTML = answerToPreview(antworten[i]);
        item.appendChild(answerPreview);

        if (showSolution) {
            const solution = document.createElement('div');
            solution.className = 'solution';
            solution.innerHTML = answerToSolution(antworten[i]);
            item.appendChild(solution);
        }

        qaList.appendChild(item);
    }

    wrapper.appendChild(qaList);
    return wrapper;
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
            listEl.appendChild(renderTask(task, index, showSolutions.checked));
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

loadManifestOptions().finally(loadJsonAndRender);
