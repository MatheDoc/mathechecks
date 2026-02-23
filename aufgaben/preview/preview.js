const pathSelect = document.getElementById('jsonPath');
const loadBtn = document.getElementById('loadBtn');
const showSolutions = document.getElementById('showSolutions');
const statusEl = document.getElementById('status');
const listEl = document.getElementById('list');
const MANIFEST_PATH = '../exports/json/manifest.json';

function toOptionLabel(relativePath) {
    return relativePath.replaceAll('/', ' / ');
}

function toPreviewPath(relativePath) {
    return `../exports/json/${relativePath}`;
}

function setPathOptions(entries) {
    if (!Array.isArray(entries) || entries.length === 0) {
        return false;
    }

    const previous = pathSelect.value;
    const currentOptions = new Set(Array.from(pathSelect.options).map((option) => option.value));

    pathSelect.innerHTML = '';
    entries.forEach((relativePath) => {
        const option = document.createElement('option');
        option.value = toPreviewPath(relativePath);
        option.textContent = toOptionLabel(relativePath);
        pathSelect.appendChild(option);
    });

    if (previous && currentOptions.has(previous)) {
        pathSelect.value = previous;
    }

    return true;
}

async function loadManifestOptions() {
    try {
        const response = await fetch(MANIFEST_PATH, { cache: 'no-store' });
        if (!response.ok) {
            return;
        }

        const entries = await response.json();
        setPathOptions(entries);
    } catch {
        // Fallback: statische Optionen aus dem HTML bleiben aktiv.
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
    const options = [];
    const pattern = /([~=])([^~=]+)/g;
    let match = pattern.exec(raw);
    while (match) {
        options.push({
            correct: match[1] === '=',
            label: match[2].trim()
        });
        match = pattern.exec(raw);
    }
    return options;
}

function answerToPreview(answerText) {
    return answerText.replace(/\{\d+:(NUMERICAL|MC):([^}]*)\}/g, (_, kind, raw) => {
        if (kind === 'NUMERICAL') {
            return '<input class="answer-input" type="text" placeholder="Antwort" />';
        }

        const options = parseMcOptions(raw)
            .map((option) => `<option>${escapeHtml(option.label)}</option>`)
            .join('');

        return `<select class="answer-select"><option selected disabled>Bitte wählen</option>${options}</select>`;
    });
}

function answerToSolution(answerText) {
    return answerText.replace(/\{\d+:(NUMERICAL|MC):([^}]*)\}/g, (_, kind, raw) => {
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
    } else {
        const traces = Array.isArray(spec?.traces) ? spec.traces : [];
        traces.forEach((trace) => {
            if (!trace || typeof trace !== 'object') {
                return;
            }
            figure.data.push({
                x: Array.isArray(trace.x) ? trace.x : [],
                y: Array.isArray(trace.y) ? trace.y : [],
                mode: trace.mode ?? 'lines',
                name: trace.name,
                type: 'scatter',
                line: trace.line,
                marker: trace.marker,
            });
        });
    }

    if (spec?.layout && typeof spec.layout === 'object') {
        figure.layout = { ...figure.layout, ...spec.layout };
    }

    return figure;
}

function renderVisual(task, wrapper) {
    if (!window.Plotly) {
        return;
    }

    const visual = task?.visual;
    const spec = visual?.spec;
    if (!spec || typeof spec !== 'object') {
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
    const path = pathSelect.value.trim();
    if (!path) {
        setStatus('Bitte einen JSON-Pfad eintragen.', true);
        return;
    }

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

        setStatus(`${payload.length} Aufgaben geladen: ${path}`);
        typesetMath();
    } catch (error) {
        setStatus(`Fehler beim Laden: ${error.message}`, true);
    }
}

loadBtn.addEventListener('click', loadJsonAndRender);
pathSelect.addEventListener('change', loadJsonAndRender);
showSolutions.addEventListener('change', loadJsonAndRender);

loadManifestOptions().finally(loadJsonAndRender);
