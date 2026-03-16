// Calculator graph module

function executeGraphFromInput(input) {
    result = 'Bitte GRAPH-Button verwenden';
    currentInput = '';
    shouldResetInput = true;
    updateDisplay();
}

function openGraphPopup() {
    openPopup('graphPopup');

    // Reset preview
    const preview = document.getElementById('graphPreview');
    if (preview) { preview.style.display = 'none'; preview.innerHTML = ''; }
    const pointsInfo = document.getElementById('graphPointsInfo');
    if (pointsInfo) { pointsInfo.style.display = 'none'; pointsInfo.innerHTML = ''; }

    focusPanelInput(document.getElementById('graphFunction'));

    // Automatische Vorschau initialisieren
    setupGraphAutoPreview();
}

function setupGraphAutoPreview() {
    const funcInput = document.getElementById('graphFunction');
    const xMinInput = document.getElementById('graphXMin');
    const xMaxInput = document.getElementById('graphXMax');
    const yMinInput = document.getElementById('graphYMin');
    const yMaxInput = document.getElementById('graphYMax');
    if (!funcInput || !xMinInput || !xMaxInput || !yMinInput || !yMaxInput) return;

    let lastValue = '';
    let debounceTimer = null;

    function tryPreview() {
        const funcVal = funcInput.value.trim();
        const xMinVal = xMinInput.value.trim();
        const xMaxVal = xMaxInput.value.trim();
        const yMinVal = yMinInput.value.trim();
        const yMaxVal = yMaxInput.value.trim();
        const current = funcVal + '|' + xMinVal + '|' + xMaxVal + '|' + yMinVal + '|' + yMaxVal;
        if (current === lastValue) return;
        lastValue = current;

        // Nur Vorschau, wenn Funktionsfeld nicht leer und mindestens ein x-Zeichen enthalten ist
        if (!funcVal || !/[a-zA-Z0-9]/.test(funcVal)) {
            const preview = document.getElementById('graphPreview');
            if (preview) {
                preview.style.display = 'none';
                preview.innerHTML = '';
            }
            const pointsInfo = document.getElementById('graphPointsInfo');
            if (pointsInfo) pointsInfo.style.display = 'none';
            return;
        }
        previewGraph();
    }

    function debouncedPreview() {
        if (debounceTimer) clearTimeout(debounceTimer);
        debounceTimer = setTimeout(tryPreview, 250);
    }

    [funcInput, xMinInput, xMaxInput, yMinInput, yMaxInput].forEach(input => {
        input.removeEventListener('input', debouncedPreview);
        input.addEventListener('input', debouncedPreview);
    });

    // Store reference globally so we can trigger it programmatically
    graphAutoPreviewFn = debouncedPreview;

    // Initial preview
    debouncedPreview();
}

document.addEventListener('calculator:popup-opened', (event) => {
    if (event.detail?.popupId !== 'graphPopup') return;
    queueMicrotask(() => {
        setupGraphAutoPreview();
    });
});

function closeGraphPopup() {
    closePopup('graphPopup');
    graphAutoPreviewFn = null;
    returnFocusToMain();
}

// Prepare a function expression for math.js graph plotting
function prepareGraphExpression(input) {
    const validENotation = /((?:\d+(?:\.\d+)?)|(?:pi)|(?:\u03c0)|(?:e))\s*E\s*[+\-]\s*\d+/gi;
    if (/E/.test(input.replace(validENotation, '___VALID___'))) return null;
    let expr = convertCustomENotation(input);
    expr = expr.replace(/(\d),(\d)/g, '$1.$2');
    expr = convertBinomSyntaxForMathJS(expr);
    expr = convertLogBaseSyntaxForMathJS(expr);
    expr = convertWurzelSyntaxForMathJS(expr);
    expr = expr.replace(/\blog\s*\(/g, 'log10(');
    expr = expr.replace(/\bln\s*\(/g, 'log(');
    expr = expr.replace(/\blogb\s*\(/g, 'log(');
    return expr;
}

function previewGraph() {
    const rawFuncInput = document.getElementById('graphFunction').value.trim();
    if (!rawFuncInput) {
        const pointsInfo = document.getElementById('graphPointsInfo');
        if (pointsInfo) pointsInfo.style.display = 'none';
        alert('Bitte geben Sie eine Funktion ein.');
        return;
    }

    let funcInput = prepareGraphExpression(rawFuncInput);
    if (!funcInput) return;

    const xMinValue = document.getElementById('graphXMin').value.trim();
    const xMaxValue = document.getElementById('graphXMax').value.trim();
    const xMin = xMinValue === '' ? -5 : parseFloat(normalizeNumberString(xMinValue));
    const xMax = xMaxValue === '' ? 5 : parseFloat(normalizeNumberString(xMaxValue));
    const yMinInput = document.getElementById('graphYMin').value.trim();
    const yMaxInput = document.getElementById('graphYMax').value.trim();

    const preview = document.getElementById('graphPreview');
    preview.style.display = 'block';
    preview.innerHTML = '';
    preview.id = 'graphPreview'; // Ensure ID is set

    const optionen = {
        titel: '',
        xAchse: '',
        yAchse: '',
        xMin: xMin,
        xMax: xMax
    };

    if (yMinInput !== '') optionen.yMin = parseFloat(normalizeNumberString(yMinInput));
    if (yMaxInput !== '') optionen.yMax = parseFloat(normalizeNumberString(yMaxInput));

    const funktionen = [{
        term: funcInput,
        name: 'f(x)',
        beschreibung: funcInput
    }];

    try {
        zeichneGraph('graphPreview', funktionen, optionen);
        // Berechne und zeige wichtige Punkte an
        analyzeGraphPoints(rawFuncInput, xMin, xMax);
    } catch (error) {
        preview.innerHTML = '<div style="color: red; padding: 10px;">Fehler beim Zeichnen ' + '</div>';
    }
}

function confirmGraph() {
    let funcInput = document.getElementById('graphFunction').value.trim();
    if (!funcInput) { alert('Bitte geben Sie eine Funktion ein.'); return; }

    funcInput = prepareGraphExpression(funcInput);
    if (!funcInput) return;

    const xMin = document.getElementById('graphXMin').value.trim() || '-5';
    const xMax = document.getElementById('graphXMax').value.trim() || '5';
    const yMin = document.getElementById('graphYMin').value.trim();
    const yMax = document.getElementById('graphYMax').value.trim();

    // Build the graph command string
    let graphCmd = `graph(${funcInput}`;
    graphCmd += `;xmin=${xMin};xmax=${xMax}`;
    if (yMin !== '') graphCmd += `;ymin=${yMin}`;
    if (yMax !== '') graphCmd += `;ymax=${yMax}`;
    graphCmd += ')';

    const mainInput = document.getElementById('mainInput');
    mainInput.value = graphCmd;
    activeInputField = mainInput;

    closeGraphPopup();
    handleExecute();
}

// Baue einen JS-auswertbaren Ausdruck basierend auf solveEquation-Pipeline
function evaluateFunctionJS(rawExpr, x) {
    try {
        let expr = `(${rawExpr})`;
        // Analyse arbeitet mit dem Rohterm aus dem Popup: Dezimalkommas zu Dezimalpunkten normalisieren.
        expr = expr.replace(/(\d),(\d)/g, '$1.$2');
        expr = addImplicitMultiplication(
            normalizeUnaryMinusExponent(
                convertWurzelSyntax(convertLogBaseSyntax(convertCustomENotation(expr)))
            )
        );
        expr = normalizeConstants(expr)
            .replace(/\^/g, '**')
            .replace(/e\*\*/g, 'Math.E**')
            .replace(/sqrt/g, 'Math.sqrt')
            .replace(/root/g, 'root')
            .replace(/exp/g, 'Math.exp')
            .replace(/\bln\b/g, 'Math.log')
            // Nur standalone log(...) zu Math.log10(...)
            .replace(/(?<!Math\.)\blog\s*\(/g, 'Math.log10(')
            .replace(/sin/g, 'Math.sin')
            .replace(/cos/g, 'Math.cos')
            .replace(/tan/g, 'Math.tan')
            .replace(/x/g, `(${x})`);
        return eval(expr);
    } catch (e) {
        return NaN;
    }
}

// Finde Nullstellen via solveEquation-Logik und filtere auf [xMin,xMax]
function findZerosUsingSolveEquation(rawExpr, xMin, xMax) {
    const tolerance = GRAPH_ANALYSIS_CONFIG.zerosTolerance;
    const rangeMin = GRAPH_ANALYSIS_CONFIG.zerosRangeMin;
    const rangeMax = GRAPH_ANALYSIS_CONFIG.zerosRangeMax;
    const steps = GRAPH_ANALYSIS_CONFIG.zerosSteps;
    const step = (rangeMax - rangeMin) / steps;
    const roots = [];

    function f(x) { return evaluateFunctionJS(rawExpr, x); }

    function refineRoot(a, b) {
        let fa = f(a);
        let fb = f(b);
        if (isNaN(fa) || isNaN(fb)) return null;
        if (Math.abs(fa) < tolerance) return a;
        if (Math.abs(fb) < tolerance) return b;
        if (fa * fb > 0) return null;

        let left = a, right = b;
        for (let i = 0; i < 100; i++) {
            const mid = (left + right) / 2;
            const fm = f(mid);
            if (isNaN(fm)) return null;
            if (Math.abs(fm) < tolerance) return mid;
            if (fa * fm <= 0) { right = mid; fb = fm; } else { left = mid; fa = fm; }
        }
        return (left + right) / 2;
    }

    for (let i = 0; i < steps; i++) {
        const x1 = rangeMin + i * step;
        const x2 = x1 + step;
        const f1 = f(x1);
        const f2 = f(x2);
        if (isNaN(f1) || isNaN(f2)) continue;
        if (Math.abs(f1) < tolerance) { roots.push(x1); continue; }
        if (f1 * f2 < 0) {
            const root = refineRoot(x1, x2);
            if (root !== null) roots.push(root);
        }
    }

    const uniqueRoots = roots
        .map(r => Math.round(r * GRAPH_ANALYSIS_CONFIG.zerosRoundFactor) / GRAPH_ANALYSIS_CONFIG.zerosRoundFactor)
        .sort((a, b) => a - b)
        .filter((r, idx, arr) => idx === 0 || Math.abs(r - arr[idx - 1]) > GRAPH_ANALYSIS_CONFIG.zerosDeduplicateTolerance)
        .filter(r => r >= xMin && r <= xMax);

    return uniqueRoots;
}

const GRAPH_ANALYSIS_CONFIG = Object.freeze({
    zerosTolerance: 1e-6,
    zerosRangeMin: -1000,
    zerosRangeMax: 1000,
    zerosSteps: 20000,
    zerosRoundFactor: 1e6,
    zerosDeduplicateTolerance: 1e-5,
    gridMinSteps: 300,
    gridMaxSteps: 3000,
    gridStepsPerUnit: 200,
    cleanValueEpsilon: 1e-9,
    defaultSignTolerance: 1e-8,
    defaultRefineIterations: 40,
    extremaSignTolerance: 1e-7,
    extremaRefineIterations: 45,
    inflectionSignTolerance: 1e-8,
    inflectionRefineIterations: 45,
    deduplicateXFactor: 2
});

function getGraphAnalysisGrid(xMin, xMax) {
    const range = xMax - xMin;
    if (!Number.isFinite(range) || range <= 0) return null;
    const steps = Math.min(
        GRAPH_ANALYSIS_CONFIG.gridMaxSteps,
        Math.max(GRAPH_ANALYSIS_CONFIG.gridMinSteps, Math.floor(range * GRAPH_ANALYSIS_CONFIG.gridStepsPerUnit))
    );
    return { range, steps, h: range / steps };
}

function signWithTolerance(value, tolerance = GRAPH_ANALYSIS_CONFIG.defaultSignTolerance) {
    if (!Number.isFinite(value)) return 0;
    if (Math.abs(value) <= tolerance) return 0;
    return value > 0 ? 1 : -1;
}

function findSignChangeRoots(sampleFn, xMin, xMax, h, options = {}) {
    const signTolerance = options.signTolerance ?? GRAPH_ANALYSIS_CONFIG.defaultSignTolerance;
    const refineIterations = options.refineIterations ?? GRAPH_ANALYSIS_CONFIG.defaultRefineIterations;
    const roots = [];
    const steps = Math.max(1, Math.floor((xMax - xMin) / h));

    function refineRoot(a, b) {
        let left = a;
        let right = b;
        let fa = sampleFn(left);
        let fb = sampleFn(right);
        if (!Number.isFinite(fa) || !Number.isFinite(fb)) return null;

        let signA = signWithTolerance(fa, signTolerance);
        let signB = signWithTolerance(fb, signTolerance);
        if (signA === 0) return left;
        if (signB === 0) return right;
        if (signA === signB) return null;

        for (let i = 0; i < refineIterations; i++) {
            const mid = (left + right) / 2;
            const fm = sampleFn(mid);
            if (!Number.isFinite(fm)) return null;
            const signM = signWithTolerance(fm, signTolerance);
            if (signM === 0) return mid;

            if (signA !== signM) {
                right = mid;
                fb = fm;
                signB = signM;
            } else {
                left = mid;
                fa = fm;
                signA = signM;
            }
        }
        return (left + right) / 2;
    }

    for (let i = 0; i < steps; i++) {
        const x1 = xMin + i * h;
        const x2 = i === steps - 1 ? xMax : x1 + h;
        const v1 = sampleFn(x1);
        const v2 = sampleFn(x2);
        if (!Number.isFinite(v1) || !Number.isFinite(v2)) continue;

        const s1 = signWithTolerance(v1, signTolerance);
        const s2 = signWithTolerance(v2, signTolerance);
        if (s1 === 0 && s2 === 0) continue;
        if (s1 !== 0 && s2 !== 0 && s1 === s2) continue;

        const root = refineRoot(x1, x2);
        if (root !== null && Number.isFinite(root)) roots.push(root);
    }

    return roots;
}

function deduplicatePointsByX(points, tolerance) {
    const unique = [];
    for (const point of points) {
        if (!unique.some(existing => Math.abs(existing.x - point.x) < tolerance)) unique.push(point);
    }
    return unique;
}

// Extrempunkte numerisch über Vorzeichenwechsel der 1. Ableitung
function findExtremaNumericalJS(rawExpr, xMin, xMax) {
    const grid = getGraphAnalysisGrid(xMin, xMax);
    if (!grid) return [];

    const { h } = grid;
    const cache = new Map();
    function f(x) {
        if (cache.has(x)) return cache.get(x);
        const value = evaluateFunctionJS(rawExpr, x);
        cache.set(x, value);
        return value;
    }
    function firstDiff(x) {
        return (f(x + h) - f(x - h)) / (2 * h);
    }

    const roots = findSignChangeRoots(firstDiff, xMin, xMax, h, {
        signTolerance: GRAPH_ANALYSIS_CONFIG.extremaSignTolerance,
        refineIterations: GRAPH_ANALYSIS_CONFIG.extremaRefineIterations
    });
    const extrema = [];

    for (const xr of roots) {
        const leftSlope = firstDiff(xr - h);
        const rightSlope = firstDiff(xr + h);
        if (!Number.isFinite(leftSlope) || !Number.isFinite(rightSlope)) continue;

        const leftSign = signWithTolerance(leftSlope, GRAPH_ANALYSIS_CONFIG.extremaSignTolerance);
        const rightSign = signWithTolerance(rightSlope, GRAPH_ANALYSIS_CONFIG.extremaSignTolerance);
        if (leftSign === 0 || rightSign === 0 || leftSign === rightSign) continue;

        const y = f(xr);
        if (!Number.isFinite(y)) continue;

        const cleanX = Math.abs(xr) < GRAPH_ANALYSIS_CONFIG.cleanValueEpsilon ? 0 : xr;
        const cleanY = Math.abs(y) < GRAPH_ANALYSIS_CONFIG.cleanValueEpsilon ? 0 : y;
        extrema.push({ x: cleanX, y: cleanY, type: leftSign > rightSign ? 'Max' : 'Min' });
    }

    return deduplicatePointsByX(extrema, h * GRAPH_ANALYSIS_CONFIG.deduplicateXFactor).sort((a, b) => a.x - b.x);
}

// Wendepunkte numerisch über Vorzeichenwechsel der 2. Ableitung
function findWendepunkteNumericalJS(rawExpr, xMin, xMax) {
    const grid = getGraphAnalysisGrid(xMin, xMax);
    if (!grid) return [];

    const { h } = grid;
    const cache = new Map();
    function f(x) {
        if (cache.has(x)) return cache.get(x);
        const value = evaluateFunctionJS(rawExpr, x);
        cache.set(x, value);
        return value;
    }
    function secondDiff(x) {
        return (f(x + h) - 2 * f(x) + f(x - h)) / (h * h);
    }

    const roots = findSignChangeRoots(secondDiff, xMin, xMax, h, {
        signTolerance: GRAPH_ANALYSIS_CONFIG.inflectionSignTolerance,
        refineIterations: GRAPH_ANALYSIS_CONFIG.inflectionRefineIterations
    });
    const points = [];

    for (const xr of roots) {
        const leftCurvature = secondDiff(xr - h);
        const rightCurvature = secondDiff(xr + h);
        if (!Number.isFinite(leftCurvature) || !Number.isFinite(rightCurvature)) continue;

        const leftSign = signWithTolerance(leftCurvature, GRAPH_ANALYSIS_CONFIG.inflectionSignTolerance);
        const rightSign = signWithTolerance(rightCurvature, GRAPH_ANALYSIS_CONFIG.inflectionSignTolerance);
        if (leftSign === 0 || rightSign === 0 || leftSign === rightSign) continue;

        const y = f(xr);
        if (!Number.isFinite(y)) continue;
        const cleanX = Math.abs(xr) < GRAPH_ANALYSIS_CONFIG.cleanValueEpsilon ? 0 : xr;
        const cleanY = Math.abs(y) < GRAPH_ANALYSIS_CONFIG.cleanValueEpsilon ? 0 : y;
        points.push({ x: cleanX, y: cleanY });
    }

    return deduplicatePointsByX(points, h * GRAPH_ANALYSIS_CONFIG.deduplicateXFactor).sort((a, b) => a.x - b.x);
}

// Analysiere wichtige Punkte des Graphen
function analyzeGraphPoints(funcExprRaw, xMin, xMax) {
    const container = document.getElementById('graphPointsInfo');
    if (!container) return;

    container.innerHTML = '';
    container.style.display = 'none';

    try {
        const nullstellen = findZerosUsingSolveEquation(funcExprRaw, xMin, xMax);
        const extrema = findExtremaNumericalJS(funcExprRaw, xMin, xMax);
        const wendepunkte = findWendepunkteNumericalJS(funcExprRaw, xMin, xMax);

        let html = '<div class="graph-points-list">';

        if (nullstellen.length > 0) {
            html += '<div class="point-category"><strong>Nullstellen:</strong></div>';
            nullstellen.forEach(x => {
                html += `<div class="point-item">x = ${formatPointValue(x)}</div>`;
            });
        }

        if (extrema.length > 0) {
            html += '<div class="point-category"><strong>Extrempunkte:</strong></div>';
            extrema.forEach(p => {
                html += `<div class="point-item">${p.type}(${formatPointValue(p.x)} | ${formatPointValue(p.y)})</div>`;
            });
        }

        if (wendepunkte.length > 0) {
            html += '<div class="point-category"><strong>Wendepunkte:</strong></div>';
            wendepunkte.forEach(p => {
                html += `<div class="point-item">W(${formatPointValue(p.x)} | ${formatPointValue(p.y)})</div>`;
            });
        }

        if (nullstellen.length === 0 && extrema.length === 0 && wendepunkte.length === 0) {
            html += '<div class="point-item" style="color: var(--textfarbe-schwach);">Keine besonderen Punkte im Bereich gefunden</div>';
        }

        html += '</div>';
        container.innerHTML = html;
        container.style.display = 'block';
    } catch (error) {
        container.innerHTML = '<div class="point-item" style="color: var(--warn-farbe);">Analyse nicht möglich</div>';
        container.style.display = 'block';
    }
}

function formatPointValue(value) {
    if (!Number.isFinite(value)) return 'n.def.';
    if (Math.abs(value) < 1e-9) return '0';
    const absValue = Math.abs(value);
    if (absValue < 0.001 || absValue > 99999) {
        return value.toExponential(2).replace('.', ',');
    }
    const formatted = value.toFixed(5).replace(/\.?0+$/, '');
    return formatted.replace('.', ',');
}
