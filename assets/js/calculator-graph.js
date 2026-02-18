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
    // Automatische Vorschau für Graph-Popup
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
}

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
    const xMin = xMinValue === '' ? -5 : parseFloat(xMinValue);
    const xMax = xMaxValue === '' ? 5 : parseFloat(xMaxValue);
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

    if (yMinInput !== '') optionen.yMin = parseFloat(yMinInput);
    if (yMaxInput !== '') optionen.yMax = parseFloat(yMaxInput);

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
    const tolerance = 0.000001;
    const rangeMin = -1000;
    const rangeMax = 1000;
    const steps = 20000;
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
        .map(r => Math.round(r * 1000000) / 1000000)
        .sort((a, b) => a - b)
        .filter((r, idx, arr) => idx === 0 || Math.abs(r - arr[idx - 1]) > 0.00001)
        .filter(r => r >= xMin && r <= xMax);

    return uniqueRoots;
}

// Extrempunkte numerisch per Nachbarschaftsvergleich
function findExtremaNumericalJS(rawExpr, xMin, xMax) {
    const range = xMax - xMin;
    const steps = Math.min(3000, Math.max(300, Math.floor(range * 200)));
    const h = range / steps;
    const extrema = [];
    function f(x) { return evaluateFunctionJS(rawExpr, x); }

    for (let i = 1; i < steps; i++) {
        const x = xMin + i * h;
        const xPrev = x - h;
        const xNext = x + h;
        const yPrev = f(xPrev);
        const y = f(x);
        const yNext = f(xNext);
        if (!Number.isFinite(yPrev) || !Number.isFinite(y) || !Number.isFinite(yNext)) continue;
        const isMax = y > yPrev && y > yNext;
        const isMin = y < yPrev && y < yNext;
        if (isMax || isMin) {
            const cleanX = Math.abs(x) < 1e-9 ? 0 : x;
            const cleanY = Math.abs(y) < 1e-9 ? 0 : y;
            extrema.push({ x: cleanX, y: cleanY, type: isMax ? 'Max' : 'Min' });
        }
    }

    const unique = [];
    for (const p of extrema) {
        if (!unique.some(q => Math.abs(q.x - p.x) < h * 2)) unique.push(p);
    }
    return unique.sort((a, b) => a.x - b.x);
}

// Wendepunkte numerisch über Vorzeichenwechsel der Krümmung
function findWendepunkteNumericalJS(rawExpr, xMin, xMax) {
    const range = xMax - xMin;
    const steps = Math.min(3000, Math.max(300, Math.floor(range * 200)));
    const h = range / steps;
    const points = [];
    function f(x) { return evaluateFunctionJS(rawExpr, x); }
    function secondDiff(x) { return (f(x + h) - 2 * f(x) + f(x - h)) / (h * h); }

    function refineInflection(a, b) {
        let fa = secondDiff(a);
        let fb = secondDiff(b);
        if (!Number.isFinite(fa) || !Number.isFinite(fb)) return null;
        if (fa * fb > 0) return null;
        let left = a, right = b;
        for (let i = 0; i < 40; i++) {
            const mid = (left + right) / 2;
            const fm = secondDiff(mid);
            if (!Number.isFinite(fm)) return null;
            if (Math.abs(fm) < 1e-9) { return mid; }
            if (fa * fm <= 0) { right = mid; fb = fm; } else { left = mid; fa = fm; }
        }
        return (left + right) / 2;
    }

    let prevX = xMin + h;
    let prevS2 = secondDiff(prevX);
    for (let i = 2; i < steps - 1; i++) {
        const x = xMin + i * h;
        const s2 = secondDiff(x);
        if (!Number.isFinite(prevS2) || !Number.isFinite(s2)) { prevS2 = s2; prevX = x; continue; }
        if (prevS2 * s2 < 0) {
            const xi = refineInflection(prevX, x) ?? x;
            const y = f(xi);
            if (Number.isFinite(y)) {
                const cleanX = Math.abs(xi) < 1e-9 ? 0 : xi;
                const cleanY = Math.abs(y) < 1e-9 ? 0 : y;
                points.push({ x: cleanX, y: cleanY });
            }
        } else {
            const s2Prev = prevS2;
            const s2Next = secondDiff(x + h);
            if (Number.isFinite(s2Next)) {
                const isLocalMin = Math.abs(s2) < Math.abs(s2Prev) && Math.abs(s2) < Math.abs(s2Next);
                if (isLocalMin && Math.abs(s2) < 1e-6) {
                    const y = f(x);
                    if (Number.isFinite(y)) {
                        const cleanX = Math.abs(x) < 1e-9 ? 0 : x;
                        const cleanY = Math.abs(y) < 1e-9 ? 0 : y;
                        points.push({ x: cleanX, y: cleanY });
                    }
                }
            }
        }
        prevS2 = s2; prevX = x;
    }
    const unique = [];
    for (const p of points) {
        if (!unique.some(q => Math.abs(q.x - p.x) < h * 2)) unique.push(p);
    }
    return unique.sort((a, b) => a.x - b.x);
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
