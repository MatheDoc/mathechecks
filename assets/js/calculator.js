// Calculator JavaScript

let currentInput = '0';
let result = 0;
let shouldResetInput = false;
let lgsVariables = 2;
let lgsEquations = 2;
let activeInputField = null;
let panelInputMode = false;
let shouldAnimateResult = false;
let copyFeedbackTimer = null;
let currentZIndex = 200;
let graphAutoPreviewFn = null;

const CALCULATOR_CORE_STATE_KEY = 'calculator-core-state-v1';
const CALCULATOR_PANEL_POSITION_KEY = 'calculator-panel-position-v1';
const CALCULATOR_POPUP_INPUT_STATE_KEY = 'calculator-popup-input-state-v1';
let isRestoringCalculatorPopupInputState = false;

function saveCalculatorCoreState() {
    const mainInput = document.getElementById('mainInput');
    const resultDisplay = document.getElementById('resultDisplay');

    try {
        sessionStorage.setItem(
            CALCULATOR_CORE_STATE_KEY,
            JSON.stringify({
                input: mainInput?.value ?? currentInput ?? '',
                resultText: resultDisplay?.textContent ?? '',
            })
        );
    } catch {
        // ignore storage issues
    }
}

function restoreCalculatorCoreState() {
    try {
        const raw = sessionStorage.getItem(CALCULATOR_CORE_STATE_KEY);
        if (!raw) return;
        const parsed = JSON.parse(raw);
        const input = typeof parsed?.input === 'string' ? parsed.input : '';
        const resultText = typeof parsed?.resultText === 'string' ? parsed.resultText : '';

        const mainInput = document.getElementById('mainInput');
        const resultDisplay = document.getElementById('resultDisplay');

        if (mainInput) {
            mainInput.value = input;
        }
        currentInput = input;

        if (resultDisplay) {
            resultDisplay.textContent = resultText || '0';
        }
        result = resultText || 0;
    } catch {
        // ignore invalid state
    }
}

function saveCalculatorPanelPosition() {
    const calculator = document.querySelector('.calculator');
    if (!calculator) return;

    const left = parseFloat(calculator.style.left || '');
    const top = parseFloat(calculator.style.top || '');
    if (!Number.isFinite(left) || !Number.isFinite(top)) return;

    try {
        sessionStorage.setItem(
            CALCULATOR_PANEL_POSITION_KEY,
            JSON.stringify({ left, top })
        );
    } catch {
        // ignore storage issues
    }
}

function restoreCalculatorPanelPosition() {
    const calculator = document.querySelector('.calculator');
    if (!calculator) return;

    try {
        const raw = sessionStorage.getItem(CALCULATOR_PANEL_POSITION_KEY);
        if (!raw) return;
        const parsed = JSON.parse(raw);
        const left = Number(parsed?.left);
        const top = Number(parsed?.top);
        if (!Number.isFinite(left) || !Number.isFinite(top)) return;

        calculator.style.position = 'fixed';
        calculator.style.left = `${left}px`;
        calculator.style.top = `${top}px`;
        calculator.style.right = 'auto';
        calculator.style.bottom = 'auto';
        calculator.style.transform = 'none';
        calculator.style.margin = '0';
    } catch {
        // ignore invalid state
    }
}

function saveCalculatorPopupInputState() {
    if (isRestoringCalculatorPopupInputState) return;

    const overlay = document.getElementById('calculator-overlay');
    if (!overlay) return;

    try {
        const fields = {};
        overlay.querySelectorAll('.popup input[id], .popup textarea[id], .popup select[id]').forEach((inputEl) => {
            fields[inputEl.id] = inputEl.value;
        });

        sessionStorage.setItem(
            CALCULATOR_POPUP_INPUT_STATE_KEY,
            JSON.stringify({
                lgsVariables,
                lgsEquations,
                fields,
            })
        );
    } catch {
        // ignore storage issues
    }
}

function restoreCalculatorPopupInputState() {
    try {
        const raw = sessionStorage.getItem(CALCULATOR_POPUP_INPUT_STATE_KEY);
        if (!raw) return;

        const parsed = JSON.parse(raw);
        if (!parsed || typeof parsed !== 'object') return;

        isRestoringCalculatorPopupInputState = true;

        const restoredVariables = Number(parsed.lgsVariables);
        const restoredEquations = Number(parsed.lgsEquations);
        if (Number.isFinite(restoredVariables) && restoredVariables >= 1 && restoredVariables <= 5) {
            lgsVariables = restoredVariables;
        }
        if (Number.isFinite(restoredEquations) && restoredEquations >= 1 && restoredEquations <= 5) {
            lgsEquations = restoredEquations;
        }

        renderLGS();

        const fields = parsed.fields;
        if (fields && typeof fields === 'object') {
            Object.entries(fields).forEach(([id, value]) => {
                const inputEl = document.getElementById(id);
                if (!inputEl) return;
                inputEl.value = typeof value === 'string' ? value : '';
            });
        }

        if (typeof updateBinomLiveResult === 'function') {
            updateBinomLiveResult();
        }

        if (typeof graphAutoPreviewFn === 'function') {
            graphAutoPreviewFn();
        }
    } catch {
        // ignore invalid state
    } finally {
        isRestoringCalculatorPopupInputState = false;
    }
}

const isTouchDevice = (() => {
    if (window.matchMedia && window.matchMedia('(pointer: coarse)').matches) return true;
    return navigator.maxTouchPoints && navigator.maxTouchPoints > 0;
})();

const isFinePointer = window.matchMedia ? window.matchMedia('(pointer: fine)').matches : false;
const isProbablyMobile = (() => {
    if (navigator.userAgentData && typeof navigator.userAgentData.mobile === 'boolean') {
        return navigator.userAgentData.mobile;
    }
    return /Android|iPhone|iPad|iPod|IEMobile|Opera Mini/i.test(navigator.userAgent);
})();

const shouldLockTouchInputs = isTouchDevice && isProbablyMobile && !isFinePointer;

function updateDisplay() {
    const resultDisplay = document.getElementById('resultDisplay');
    if (resultDisplay) {
        // Check if result is already a formatted string (e.g., from equation solver, LGS, etc.)
        // or if it's a number that needs formatting
        let formattedResult;
        if (typeof result === 'string') {
            formattedResult = result; // Already formatted (equations, errors, etc.)
        } else {
            formattedResult = formatGeneralResult(result); // Format numbers
        }
        resultDisplay.textContent = formattedResult;
        if (shouldAnimateResult) {
            resultDisplay.classList.remove('updated');
            void resultDisplay.offsetWidth;
            resultDisplay.classList.add('updated');
            shouldAnimateResult = false;
        }

        saveCalculatorCoreState();
    }
}

function copyResult() {
    const resultDisplay = document.getElementById('resultDisplay');
    let value = (resultDisplay?.textContent || '').trim();
    if (!value) {
        value = String(result ?? '').trim();
    }
    if (!value) return;

    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(value)
            .then(() => showCopyFeedback())
            .catch(() => fallbackCopy(value));
        return;
    }

    fallbackCopy(value);
}

function fallbackCopy(value) {
    const temp = document.createElement('textarea');
    temp.value = value;
    temp.setAttribute('readonly', '');
    temp.style.position = 'absolute';
    temp.style.left = '-9999px';
    document.body.appendChild(temp);
    temp.select();
    document.execCommand('copy');
    document.body.removeChild(temp);
    showCopyFeedback();
}

function showCopyFeedback() {
    const copyButton = document.getElementById('copyResultButton');
    if (!copyButton) return;
    copyButton.classList.remove('copied');
    void copyButton.offsetWidth;
    copyButton.classList.add('copied');
    if (copyFeedbackTimer) {
        clearTimeout(copyFeedbackTimer);
    }
    copyFeedbackTimer = setTimeout(() => {
        copyButton.classList.remove('copied');
    }, 1200);
}

function applyTouchInputLock() {
    const inputs = document.querySelectorAll('#mainInput, #binomA, #binomB, #binomN, #binomP, #lgsMatrix input, #graphFunction, #graphXMin, #graphXMax, #graphYMin, #graphYMax');
    inputs.forEach((input) => {
        if (!input.dataset.defaultInputMode) {
            input.dataset.defaultInputMode = input.getAttribute('inputmode') || input.inputMode || '';
        }

        // Always disable browser stored info/autofill, regardless of device
        input.readOnly = false;
        input.autocapitalize = 'off';
        input.autocomplete = 'off';
        input.spellcheck = false;

        // Lock touch keyboards when coarse pointer/mobile is detected
        if (shouldLockTouchInputs) {
            input.inputMode = 'none';
        } else {
            input.inputMode = input.dataset.defaultInputMode || '';
        }
    });
}

function appendValue(value) {
    if (appendToActiveInput(value)) return;
    const mainInput = document.getElementById('mainInput');
    if (mainInput && activeInputField === mainInput) {
        insertAtCursor(mainInput, value);
    } else {
        if (shouldResetInput || currentInput === '0') {
            currentInput = value;
            shouldResetInput = false;
        } else {
            currentInput += value;
        }
        updateDisplay();
    }
}

function appendNumber(num) { appendValue(String(num)); }

function appendOperator(op) {
    if (appendToActiveInput(op)) return;
    const mainInput = document.getElementById('mainInput');
    if (mainInput && activeInputField === mainInput) {
        insertAtCursor(mainInput, op);
    } else {
        shouldResetInput = false;
        if (currentInput.slice(-1).match(/[\+\-\*\/\=]/)) {
            currentInput = currentInput.slice(0, -1) + op;
        } else {
            currentInput += op;
        }
        updateDisplay();
    }
}

function appendFunction(func) { appendValue(func); }

function appendLogTemplate() {
    if (activeInputField && panelInputMode) {
        const currentValue = activeInputField.value || '';
        const start = activeInputField.selectionStart ?? currentValue.length;
        const end = activeInputField.selectionEnd ?? start;
        const template = 'log(;)';
        activeInputField.value =
            currentValue.slice(0, start) + template + currentValue.slice(end);
        // Place cursor after '(', ready to type the base
        setInputCursor(activeInputField, start + 4);
        if (activeInputField.closest('#graphPopup') && graphAutoPreviewFn) {
            graphAutoPreviewFn();
        }
        return;
    }

    appendFunction('log(;)');
}

function appendRootTemplate() {
    const template = 'wurzel(;)';
    if (activeInputField && panelInputMode) {
        const currentValue = activeInputField.value || '';
        const start = activeInputField.selectionStart ?? currentValue.length;
        const end = activeInputField.selectionEnd ?? start;
        activeInputField.value = currentValue.slice(0, start) + template + currentValue.slice(end);
        // Place cursor before the semicolon to enter x first
        setInputCursor(activeInputField, start + 7);
        if (activeInputField.closest('#graphPopup') && graphAutoPreviewFn) {
            graphAutoPreviewFn();
        }
        return;
    }

    const mainInput = document.getElementById('mainInput');
    if (mainInput && activeInputField === mainInput) {
        insertAtCursor(mainInput, template);
        setInputCursor(mainInput, (mainInput.selectionStart ?? 0));
    } else {
        if (shouldResetInput || currentInput === '0') {
            currentInput = template;
            shouldResetInput = false;
        } else {
            currentInput += template;
        }
        updateDisplay();
    }
}

function appendAutoParen() {
    // If we're editing inside a popup input field
    if (activeInputField && panelInputMode) {
        const currentValue = activeInputField.value || '';
        const cursor = activeInputField.selectionStart ?? currentValue.length;
        const before = currentValue.slice(0, cursor);
        const paren = shouldInsertClosingParen(before) ? ')' : '(';
        insertAtCursor(activeInputField, paren);
        return;
    }

    // If the main input has focus, insert at the caret position
    const mainInput = document.getElementById('mainInput');
    if (mainInput && activeInputField === mainInput) {
        const value = mainInput.value || '';
        const cursor = mainInput.selectionStart ?? value.length;
        const before = value.slice(0, cursor);
        const paren = shouldInsertClosingParen(before) ? ')' : '(';
        insertAtCursor(mainInput, paren);
        return;
    }

    // Fallback to editing the internal buffer
    const paren = shouldInsertClosingParen(currentInput) ? ')' : '(';
    if (shouldResetInput || currentInput === '0') {
        currentInput = paren;
        shouldResetInput = false;
    } else {
        currentInput += paren;
    }
    updateDisplay();
}

function shouldInsertClosingParen(value) {
    const openCount = (value.match(/\(/g) || []).length;
    const closeCount = (value.match(/\)/g) || []).length;
    if (openCount <= closeCount) {
        return false;
    }
    const trimmed = value.replace(/\s+/g, '');
    if (!trimmed) {
        return false;
    }
    const last = trimmed[trimmed.length - 1];
    return !/[+\-*/^=,(]/.test(last);
}

function closeKeyPopovers() {
    const popovers = document.querySelectorAll('.key-popover');
    popovers.forEach((popover) => {
        popover.classList.remove('open');
        const trigger = popover.querySelector('button[aria-expanded]');
        if (trigger) {
            trigger.setAttribute('aria-expanded', 'false');
        }
    });
}

function toggleKeyPopover(popoverId, trigger) {
    const popover = document.getElementById(popoverId);
    if (!popover) return;
    const container = popover.closest('.key-popover');
    if (!container) return;

    const isOpen = container.classList.contains('open');
    closeKeyPopovers();
    if (!isOpen) {
        container.classList.add('open');
        if (trigger) {
            trigger.setAttribute('aria-expanded', 'true');
        }
    }
}

document.addEventListener('click', (event) => {
    if (!event.target.closest('.key-popover')) {
        closeKeyPopovers();
    }
});

function clearAll() {
    const popupInputToClear = getOpenPopupInputToClear();
    if (popupInputToClear) {
        popupInputToClear.value = '';
        activeInputField = popupInputToClear;
        panelInputMode = true;
        if (popupInputToClear.closest('#graphPopup') && graphAutoPreviewFn) {
            graphAutoPreviewFn();
        }
        return;
    }

    const mainInput = document.getElementById('mainInput');
    if (mainInput) {
        mainInput.value = '';
    }
    currentInput = '0';
    result = 0;
    shouldResetInput = false;
    updateDisplay();
    // Return focus to main input after clearing
    if (mainInput) {
        activeInputField = mainInput;
        panelInputMode = false;
        mainInput.focus({ preventScroll: true });
        setInputCursor(mainInput, 0);
    }
}

function backspace() {
    if (activeInputField) {
        const value = activeInputField.value || '';
        const start = activeInputField.selectionStart ?? value.length;
        const end = activeInputField.selectionEnd ?? start;
        if (start !== end) {
            activeInputField.value = value.slice(0, start) + value.slice(end);
            setInputCursor(activeInputField, start);
        } else if (start > 0) {
            activeInputField.value = value.slice(0, start - 1) + value.slice(end);
            setInputCursor(activeInputField, start - 1);
        }
        if (activeInputField.closest('#graphPopup') && graphAutoPreviewFn) {
            graphAutoPreviewFn();
        }
        return;
    }

    if (currentInput.length > 1) {
        currentInput = currentInput.slice(0, -1);
    } else {
        currentInput = '0';
    }
    updateDisplay();
}
function insertAns() {
    const value = String(result ?? '').trim();
    if (!value) return;

    const mainInput = document.getElementById('mainInput');
    if (!mainInput) return;

    // Clear the input line first, then write the result
    mainInput.value = '';
    insertAtCursor(mainInput, value);
    activeInputField = mainInput;
    panelInputMode = false;
    mainInput.focus({ preventScroll: true });
}

function normalizeExpression(input) {
    const normalized = normalizeNumberString(input);

    let expression = addImplicitMultiplication(
        normalizeUnaryMinusExponent(
            /* root infix disabled */ convertBinomSyntaxForMathJS(convertWurzelSyntax(convertLogBaseSyntax(convertCustomENotation(normalized))))
        )
    );
    return normalizeConstants(expression)
        .replace(/×/g, '*')
        .replace(/÷/g, '/')
        .replace(/−/g, '-')
        .replace(/\^/g, '**')
        .replace(/sqrt\(/g, 'Math.sqrt(')
        .replace(/exp\(/g, 'Math.exp(')
        .replace(/ln\(/g, 'Math.log(')
        .replace(/sin\(/g, 'Math.sin(')
        .replace(/cos\(/g, 'Math.cos(')
        .replace(/tan\(/g, 'Math.tan(');
}

function calculate() {
    try {
        const expression = normalizeExpression(currentInput);
        const value = eval(expression);
        result = value;  // Store the raw number, formatting happens in updateDisplay()
        shouldResetInput = true;
        updateDisplay();
    } catch (error) {
        result = 'Fehler';
        updateDisplay();
    }
}

function formatGeneralResult(value) {
    if (typeof value !== 'number' || !Number.isFinite(value)) {
        return 'Fehler';
    }
    const abs = Math.abs(value);
    // Use scientific notation for very small or very large magnitudes
    if (abs !== 0 && (abs < 1e-4 || abs >= 1e9)) {
        const exp = value.toExponential(8);
        const [mantissa, exponent] = exp.split('e');
        const mTrim = mantissa
            .replace(/\.0+$/, '')
            .replace(/(\.\d*?)0+$/, '$1');
        const expNum = parseInt(exponent, 10);
        const sign = expNum >= 0 ? '+' : '-';
        const mantissaGerman = toGermanNumber(mTrim);
        return `${mantissaGerman}E${sign}${Math.abs(expNum)}`;
    }
    // Otherwise, keep up to 9 decimal places and trim trailing zeros,
    // then format with German separators
    const text = (Math.round(value * 1e9) / 1e9).toString();
    const trimmed = text.replace(/\.0+$/, '').replace(/(\.\d*?)0+$/, '$1');
    return toGermanNumber(trimmed);
}

// Detect if input contains 'x' as a variable (not part of function names like 'exp')
function containsVariableX(input) {
    const cleaned = input.replace(/\bexp\b/gi, '___');
    return /(?:^|[^a-zA-Z])x(?:[^a-zA-Z]|$)/i.test(cleaned);
}

// Expand/simplify a symbolic expression using math.js rationalize
function expandExpression(input) {
    try {
        // Prepare input for math.js (handle decimal commas, special functions)
        let expr = prepareGraphExpression(input);
        if (!expr) {
            result = 'Fehler: Ungültiger Ausdruck';
            updateDisplay();
            return;
        }

        // Use math.js rationalize to expand the expression
        const expanded = math.rationalize(expr);
        let output = expanded.toString({ implicit: 'hide', parenthesis: 'auto' });

        // Clean up formatting: compact polynomial notation
        output = output.replace(/ /g, '');
        // Implizite Multiplikation: 2*x → 2x
        output = output.replace(/(\d)\*([a-zA-Z])/g, '$1$2');

        currentInput = `${input} →`;
        result = output;
        shouldResetInput = true;
        updateDisplay();
    } catch (error) {
        result = 'Fehler: Ausdruck konnte nicht vereinfacht werden';
        updateDisplay();
    }
}

function handleExecute() {
    shouldAnimateResult = true;
    const mainInput = document.getElementById('mainInput');
    const inputValue = mainInput.value || '0';

    // Check for LGS syntax: lgs(eq1;eq2;...)
    if (inputValue.trim().match(/^lgs\s*\(/i)) {
        executeLGSFromInput(inputValue);
        return;
    }

    // Check for BIN syntax: binom(a;b;n;p)
    if (inputValue.trim().match(/^binom\s*\(.*\)\s*$/i)) {
        executeBinFromInput(inputValue);
        return;
    }

    // Check for GRAPH syntax: graph(function;options)
    if (inputValue.trim().match(/^graph\s*\(/i)) {
        executeGraphFromInput(inputValue);
        return;
    }

    // Check for equation (single =)
    const equalsCount = (inputValue.match(/=/g) || []).length;
    if (equalsCount === 1) {
        solveEquation(inputValue);
        return;
    }

    // Check for symbolic expression with x (no equation) → expand/ausmultiplizieren
    if (equalsCount === 0 && containsVariableX(inputValue)) {
        expandExpression(inputValue);
        return;
    }

    // Normal calculation
    currentInput = inputValue;
    calculate();
}

function executeLGSFromInput(input) {
    try {
        // Support syntax lgs(eq1;eq2;...)
        let content = input.trim();
        const m = content.match(/^lgs\s*\((.*)\)\s*$/i);
        if (m) {
            content = m[1];
        } else {
            throw new Error('Invalid LGS format');
        }
        const equations = content.split(';').map(s => s.trim()).filter(s => s.length > 0);

        // Determine variables from both sides (single-letter variables a-z)
        const varSet = new Set();
        equations.forEach(eq => {
            const [leftRaw, rightRaw] = eq.split('=');
            const collect = (text) => {
                (text.match(/[a-z]/gi) || []).forEach(v => varSet.add(v.toLowerCase()));
            };
            collect(leftRaw || '');
            collect(rightRaw || '');
        });

        const varNames = Array.from(varSet).sort();
        const varIndex = new Map(varNames.map((v, i) => [v, i]));

        // Build matrix A and vector b using evaluation with parentheses and expressions allowed
        const A = [];
        const b = [];

        equations.forEach(eq => {
            const [leftRaw, rightRaw] = eq.split('=');
            const left = (leftRaw || '').trim();
            const right = (rightRaw || '').trim();

            // Validate linearity for each side: disallow terms like x^2 or x*y
            const isLeftLinear = isLinearExpression(left, varNames);
            const isRightLinear = isLinearExpression(right, varNames);
            if (!isLeftLinear || !isRightLinear) {
                currentInput = 'LGS: Nichtlineare Terme gefunden';
                result = 'Fehler: Nicht linear (x^2, xy, ...)';
                shouldResetInput = true;
                updateDisplay();
                throw new Error('Nonlinear term found');
            }

            const row = new Array(varNames.length).fill(0);
            // Coefficient of each variable: coeffLeft - coeffRight
            varNames.forEach((v) => {
                const idx = varIndex.get(v);
                if (idx === undefined) return;
                const coeffLeft = evaluateCoefficient(left, varNames, v);
                const coeffRight = evaluateCoefficient(right, varNames, v);
                row[idx] = (coeffLeft ?? 0) - (coeffRight ?? 0);
            });

            // Evaluate constants on both sides by substituting variables with 0
            const leftConst = evaluateScalarExpression(left, varNames);
            const rightConst = evaluateScalarExpression(right, varNames);

            // Move constants to right: b_i = rightConst - leftConst
            A.push(row);
            b.push((rightConst ?? 0) - (leftConst ?? 0));
        });

        const solution = solveLinearSystem(A, b);

        if (solution.status === 'inconsistent') {
            currentInput = 'LGS: Keine Lösung';
            result = 'Keine Lösung';
        } else if (solution.status === 'infinite') {
            currentInput = 'LGS: Unendlich viele Lösungen';
            result = solution.parametric
                .map((expr) => expr.replace(/^x(\d+)/, (_, num) => varNames[parseInt(num, 10) - 1] || `x${num}`))
                .join(', ');
        } else {
            currentInput = 'LGS gelöst';
            result = solution.values
                .map((x, i) => `${varNames[i] || `x${i + 1}`}=${formatNumber(x)}`)
                .join(', ');
        }

        shouldResetInput = true;
        updateDisplay();
    } catch (error) {
        result = 'Fehler im LGS';
        updateDisplay();
    }
}
// Check if expression is linear in given variables using evaluation tests
function isLinearExpression(expr, varNames) {
    try {
        const eps = 1e-9;
        const baseline = evaluateWithAssignments(expr, varNames, {});
        const coeffs = new Map();

        for (let i = 0; i < varNames.length; i++) {
            const v = varNames[i];
            const val1 = evaluateWithAssignments(expr, varNames, { [v]: 1 });
            const val2 = evaluateWithAssignments(expr, varNames, { [v]: 2 });
            const c = (val1 - baseline);
            coeffs.set(v, c);
            // Check scaling: f(2) should equal baseline + 2*c
            if (!Number.isFinite(val1) || !Number.isFinite(val2) || Math.abs((baseline + 2 * c) - val2) > eps) {
                return false;
            }
        }

        // Check cross terms: f(v=1,w=1) should equal baseline + c_v + c_w
        for (let i = 0; i < varNames.length; i++) {
            for (let j = i + 1; j < varNames.length; j++) {
                const vi = varNames[i];
                const vj = varNames[j];
                const both = evaluateWithAssignments(expr, varNames, { [vi]: 1, [vj]: 1 });
                const expected = baseline + (coeffs.get(vi) || 0) + (coeffs.get(vj) || 0);
                if (!Number.isFinite(both) || Math.abs(both - expected) > eps) {
                    return false;
                }
            }
        }
        return true;
    } catch (e) {
        return false;
    }
}

// Evaluate expression with given variable assignments, others set to 0
function evaluateWithAssignments(expr, varNames, assignments) {
    try {
        let normalized = normalizeNumberString(expr || '');
        normalized = normalizeExpression(normalized);
        varNames.forEach((v) => {
            const re = new RegExp(`(^|[^a-zA-Z0-9_.])${v}([^a-zA-Z0-9_]|$)`, 'g');
            const val = Object.prototype.hasOwnProperty.call(assignments, v) ? String(assignments[v]) : '0';
            normalized = normalized.replace(re, `$1${val}$2`);
        });
        const value = eval(normalized);
        return typeof value === 'number' ? value : NaN;
    } catch (e) {
        return NaN;
    }
}

// Evaluate a scalar numeric expression with all variables set to 0
function evaluateScalarExpression(expr, varNames) {
    const value = evaluateWithAssignments(expr, varNames, {});
    return Number.isFinite(value) ? value : 0;
}

// Evaluate the linear coefficient of targetVar in expr
function evaluateCoefficient(expr, varNames, targetVar) {
    const withOne = evaluateWithAssignments(expr, varNames, { [targetVar]: 1 });
    const baseline = evaluateScalarExpression(expr, varNames);
    const coeff = (withOne ?? 0) - (baseline ?? 0);
    return Number.isFinite(coeff) ? coeff : 0;
}

// Parse p-value string, supporting fractions like "1/6"
function parsePValue(pStr) {
    const normalized = normalizeNumberString(pStr);
    if (normalized.includes('/')) {
        const parts = normalized.split('/').map(p => parseFloat(p.trim()));
        if (parts.length === 2 && parts.every(p => !isNaN(p)) && parts[1] !== 0) {
            return parts[0] / parts[1];
        }
    }
    return parseFloat(normalized);
}

function computeBinomProbability(a, b, n, p) {
    let probability = 0;
    for (let k = a; k <= b; k++) {
        probability += binomialCoefficient(n, k) * Math.pow(p, k) * Math.pow(1 - p, n - k);
    }
    return probability;
}

function binom(a, b, n, p) {
    const aNum = Math.ceil(Number(a));
    const bNum = Math.floor(Number(b));
    const nNum = parseInt(Number(n), 10);
    const pNum = Number(p);

    if (!Number.isFinite(aNum) || !Number.isFinite(bNum) || !Number.isFinite(nNum) || !Number.isFinite(pNum)) {
        return NaN;
    }

    return computeBinomProbability(aNum, bNum, nNum, pNum);
}

function executeBinFromInput(input) {
    try {
        const match = input.trim().match(/^binom\s*\(\s*([^;]+)\s*;\s*([^;]+)\s*;\s*([^;]+)\s*;\s*([^)]+)\s*\)$/i);
        if (!match) throw new Error('Invalid format');

        const a = Math.ceil(parseFloat(normalizeNumberString(match[1])));
        const b = Math.floor(parseFloat(normalizeNumberString(match[2])));
        const n = parseInt(normalizeNumberString(match[3]));
        const p = parsePValue(match[4]);

        currentInput = `Binom(a=${a}, b=${b}, n=${n}, p=${match[4]})`;
        result = computeBinomProbability(a, b, n, p);
        shouldResetInput = true;
        updateDisplay();
    } catch (error) {
        result = 'Fehler in BINOM';
        updateDisplay();
    }
}

function toggleSign() {
    if (activeInputField) {
        const value = activeInputField.value || '';
        if (value.startsWith('-')) {
            activeInputField.value = value.slice(1);
        } else if (value.length > 0) {
            activeInputField.value = '-' + value;
        }
        if (activeInputField.closest('#graphPopup') && graphAutoPreviewFn) {
            graphAutoPreviewFn();
        }
        return;
    }

    const numericPattern = /^-?\d+(\.\d+)?$/;
    if (numericPattern.test(currentInput)) {
        currentInput = currentInput.startsWith('-') ? currentInput.slice(1) : '-' + currentInput;
        updateDisplay();
    }
}

function appendToActiveInput(value) {
    const mainInput = document.getElementById('mainInput');
    if (!activeInputField || activeInputField === mainInput) {
        return false;
    }

    // Check if activeInputField is still in an open popup
    const isInOpenPopup = activeInputField.closest('#lgsPopup.open, #binPopup.open, #constPopup.open, #triPopup.open, #graphPopup.open');
    if (!isInOpenPopup) {
        return false;
    }

    const currentValue = activeInputField.value || '';
    if (activeInputField.type === 'number' || activeInputField.type === 'text') {
        const isSeparator = value === '.' || value === ',';
        const isExpressionInput = activeInputField.id === 'calInput';

        if (isSeparator && isExpressionInput) {
            const cursor = activeInputField.selectionStart ?? currentValue.length;
            const left = currentValue.slice(0, cursor);
            let i = left.length - 1;
            while (i >= 0 && /[0-9.,]/.test(left[i])) {
                i--;
            }
            const segment = left.slice(i + 1);
            const hasSeparator = segment.includes('.') || segment.includes(',');
            if (hasSeparator) {
                return true;
            }
            if (segment === '') {
                insertAtCursor(activeInputField, `0${value}`);
                if (activeInputField.closest('#binPopup')) {
                    updateBinomLiveResult();
                }
                return true;
            }
        } else if (isSeparator) {
            const hasSeparator = currentValue.includes('.') || currentValue.includes(',');
            if (hasSeparator) {
                return true;
            }
            if (currentValue === '' || currentValue === '-') {
                activeInputField.value = `${currentValue}0${value}`;
                if (activeInputField.closest('#binPopup')) {
                    updateBinomLiveResult();
                }
                if (activeInputField.closest('#graphPopup') && graphAutoPreviewFn) {
                    graphAutoPreviewFn();
                }
                return true;
            }
        }
    }

    insertAtCursor(activeInputField, value);

    // Trigger live result update for BIN popup inputs
    if (activeInputField.closest('#binPopup')) {
        updateBinomLiveResult();
    }

    return true;
}

function insertAtCursor(input, value) {
    const currentValue = input.value || '';
    const start = input.selectionStart ?? currentValue.length;
    const end = input.selectionEnd ?? start;
    input.value = currentValue.slice(0, start) + value + currentValue.slice(end);
    setInputCursor(input, start + value.length);

    // Trigger preview update for Graph popup inputs
    if (input.closest('#graphPopup') && graphAutoPreviewFn) {
        graphAutoPreviewFn();
    }
}

function setInputCursor(input, position) {
    input.focus({ preventScroll: true });
    if (input.setSelectionRange) {
        input.setSelectionRange(position, position);
    }
}

function normalizeNumberString(value) {
    // Remove thousands separators (.) then replace comma (decimal) with dot
    return value.replace(/\./g, '').replace(/,/g, '.');
}

function openLGSPopup() {
    openPopup('lgsPopup');
    renderLGS();
    focusPanelInput(document.querySelector('#lgsMatrix input'));
}

function closeLGSPopup() {
    closePopup('lgsPopup');
    returnFocusToMain();
}

function confirmLGS() {
    const varNames = ['x', 'y', 'z', 'u', 'v', 'w'];
    const equations = [];

    for (let i = 0; i < lgsEquations; i++) {
        const terms = [];
        for (let j = 0; j < lgsVariables; j++) {
            const coeffRaw = document.getElementById(`a${i}${j}`).value || '0';
            const coeff = parseFloat(normalizeNumberString(coeffRaw));
            if (coeff !== 0) {
                if (terms.length === 0) {
                    // First term
                    if (coeff === 1) {
                        terms.push(varNames[j]);
                    } else if (coeff === -1) {
                        terms.push(`-${varNames[j]}`);
                    } else {
                        terms.push(`${coeff}${varNames[j]}`);
                    }
                } else {
                    // Subsequent terms
                    if (coeff === 1) {
                        terms.push(`+${varNames[j]}`);
                    } else if (coeff === -1) {
                        terms.push(`-${varNames[j]}`);
                    } else if (coeff > 0) {
                        terms.push(`+${coeff}${varNames[j]}`);
                    } else {
                        terms.push(`${coeff}${varNames[j]}`);
                    }
                }
            }
        }
        const result = document.getElementById(`b${i}`).value || '0';
        equations.push((terms.length > 0 ? terms.join('') : '0') + '=' + result);
    }

    const compactForm = 'lgs(' + equations.join(';') + ')';
    const mainInput = document.getElementById('mainInput');
    mainInput.value = compactForm;
    activeInputField = mainInput;

    closeLGSPopup();
    handleExecute();
}

function openBinPopup() {
    openPopup('binPopup');
    updateBinomLiveResult();
    focusPanelInput(document.getElementById('binomA'));
}

function closeBinPopup() {
    closePopup('binPopup');
    returnFocusToMain();
}

function confirmBin() {
    const a = document.getElementById('binomA').value || '0';
    const b = document.getElementById('binomB').value || '0';
    const n = document.getElementById('binomN').value || '0';
    const p = document.getElementById('binomP').value || '0';

    const compactForm = `binom(${a};${b};${n};${p})`;
    const mainInput = document.getElementById('mainInput');
    mainInput.value = compactForm;
    activeInputField = mainInput;

    closeBinPopup();
    handleExecute();
}

// LGS Functions
function initLGS() {
    lgsVariables = 2;
    lgsEquations = 2;
    renderLGS();
}

function renderLGS() {
    const container = document.getElementById('lgsMatrix');
    const existingValues = {};

    container.querySelectorAll('input').forEach((input) => {
        existingValues[input.id] = input.value;
    });
    container.innerHTML = '';

    const varNames = ['x', 'y', 'z', 'u', 'v', 'w'];

    for (let i = 0; i < lgsEquations; i++) {
        const row = document.createElement('div');
        row.className = 'input-row';

        for (let j = 0; j < lgsVariables; j++) {
            if (j > 0) {
                const plusMinus = document.createElement('span');
                plusMinus.textContent = '+';
                plusMinus.className = 'lgs-operator';
                row.appendChild(plusMinus);
            }

            const input = document.createElement('input');
            input.type = 'text';
            input.inputMode = 'decimal';
            input.readOnly = false;
            input.id = `a${i}${j}`;
            input.name = `a${i}${j}`;
            input.autocomplete = 'off';
            input.autocapitalize = 'off';
            input.spellcheck = false;
            input.placeholder = '';
            input.value = existingValues[input.id] ?? '';
            row.appendChild(input);

            const varLabel = document.createElement('span');
            varLabel.textContent = varNames[j] || `x${j + 1}`;
            varLabel.className = 'lgs-var-label';
            row.appendChild(varLabel);
        }

        const equals = document.createElement('span');
        equals.textContent = '=';
        equals.className = 'lgs-equals';
        row.appendChild(equals);

        const resultInput = document.createElement('input');
        resultInput.type = 'text';
        resultInput.inputMode = 'decimal';
        resultInput.readOnly = false;
        resultInput.id = `b${i}`;
        resultInput.name = `b${i}`;
        resultInput.autocomplete = 'off';
        resultInput.autocapitalize = 'off';
        resultInput.spellcheck = false;
        resultInput.placeholder = '';
        resultInput.value = existingValues[resultInput.id] ?? '';
        row.appendChild(resultInput);

        container.appendChild(row);
    }

    applyTouchInputLock();
    bindLGSEnterKeys();
}

function addLGSVariable() {
    if (lgsVariables < 5) {
        lgsVariables++;
        renderLGS();
    }
}

function removeLGSVariable() {
    if (lgsVariables > 1) {
        lgsVariables--;
        renderLGS();
    }
}

function addLGSEquation() {
    if (lgsEquations < 5) {
        lgsEquations++;
        renderLGS();
    }
}

function removeLGSEquation() {
    if (lgsEquations > 1) {
        lgsEquations--;
        renderLGS();
    }
}

function solveLGS() {
    try {
        const A = [];
        const b = [];

        for (let i = 0; i < lgsEquations; i++) {
            A[i] = [];
            for (let j = 0; j < lgsVariables; j++) {
                const cellValue = document.getElementById(`a${i}${j}`).value;
                A[i][j] = parseFloat(normalizeNumberString(cellValue)) || 0;
            }
            const resultValue = document.getElementById(`b${i}`).value;
            b[i] = parseFloat(normalizeNumberString(resultValue)) || 0;
        }

        const solution = solveLinearSystem(A, b);

        if (solution.status === 'inconsistent') {
            currentInput = 'LGS: Keine Lösung';
            result = 'Keine Lösung';
        } else if (solution.status === 'infinite') {
            currentInput = 'LGS: Unendlich viele Lösungen';
            result = solution.parametric
                .map((expr) => expr.replace(/^x(\d+)/, (_, num) => `x${toSubscript(num)}`))
                .join(', ');
        } else {
            currentInput = 'LGS gelöst';
            result = solution.values
                .map((x, i) => `x${toSubscript(i + 1)}=${formatNumber(x)}`)
                .join(', ');
        }

        shouldResetInput = true;
        updateDisplay();
    } catch (error) {
        currentInput = 'LGS Fehler';
        result = 'Fehler';
        updateDisplay();
    }
}

function solveLinearSystem(A, b) {
    const rows = A.length;
    const cols = A[0]?.length || 0;
    const augmented = A.map((row, i) => [...row, b[i]]);
    const pivotCols = [];
    let r = 0;
    const eps = 1e-10;

    for (let c = 0; c < cols && r < rows; c++) {
        let pivotRow = r;
        for (let i = r + 1; i < rows; i++) {
            if (Math.abs(augmented[i][c]) > Math.abs(augmented[pivotRow][c])) {
                pivotRow = i;
            }
        }

        if (Math.abs(augmented[pivotRow][c]) < eps) {
            continue;
        }

        if (pivotRow !== r) {
            [augmented[r], augmented[pivotRow]] = [augmented[pivotRow], augmented[r]];
        }

        const pivotVal = augmented[r][c];
        for (let j = c; j <= cols; j++) {
            augmented[r][j] /= pivotVal;
        }

        for (let i = 0; i < rows; i++) {
            if (i === r) continue;
            const factor = augmented[i][c];
            if (Math.abs(factor) < eps) continue;
            for (let j = c; j <= cols; j++) {
                augmented[i][j] -= factor * augmented[r][j];
            }
        }

        pivotCols.push(c);
        r++;
    }

    for (let i = 0; i < rows; i++) {
        let allZero = true;
        for (let j = 0; j < cols; j++) {
            if (Math.abs(augmented[i][j]) >= eps) {
                allZero = false;
                break;
            }
        }
        if (allZero && Math.abs(augmented[i][cols]) >= eps) {
            return { status: 'inconsistent' };
        }
    }

    if (pivotCols.length === cols) {
        const values = new Array(cols).fill(0);
        for (let i = 0; i < pivotCols.length; i++) {
            const col = pivotCols[i];
            values[col] = augmented[i][cols];
        }
        return { status: 'unique', values };
    }

    const freeCols = [];
    for (let j = 0; j < cols; j++) {
        if (!pivotCols.includes(j)) {
            freeCols.push(j);
        }
    }

    const paramMap = new Map();
    freeCols.forEach((col, idx) => {
        paramMap.set(col, 'λ' + toSubscript(idx + 1));
    });

    const expressions = new Array(cols).fill('0');

    freeCols.forEach((col) => {
        expressions[col] = paramMap.get(col);
    });

    for (let i = 0; i < pivotCols.length; i++) {
        const col = pivotCols[i];
        let expr = formatNumber(augmented[i][cols]);
        freeCols.forEach((freeCol) => {
            const coeff = -augmented[i][freeCol];
            if (Math.abs(coeff) < eps) return;
            const sign = coeff >= 0 ? ' + ' : ' - ';
            const absCoeff = Math.abs(coeff);
            const coeffText = absCoeff === 1 ? '' : formatNumber(absCoeff);
            expr += `${sign}${coeffText}${paramMap.get(freeCol)}`;
        });
        expressions[col] = expr;
    }

    const parametric = expressions.map((expr, idx) => `x${idx + 1}=${expr}`);
    return { status: 'infinite', parametric };
}

function formatNumber(value) {
    const rounded = Math.round(value * 1000000) / 1000000;
    const text = rounded.toFixed(6);
    const trimmed = text.replace(/\.0+$/, '').replace(/(\.\d*?)0+$/, '$1');
    return toGermanNumber(trimmed);
}

const subscriptMap = {
    '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
    '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉'
};

function toSubscript(num) {
    return String(num)
        .split('')
        .map((char) => subscriptMap[char] ?? char)
        .join('');
}

// Binomial
function binomialCoefficient(n, k) {
    if (k < 0 || k > n) return 0;
    if (k === 0 || k === n) return 1;

    let result = 1;
    for (let i = 1; i <= k; i++) {
        result *= (n - k + i) / i;
    }
    return Math.round(result);
}

function calculateBinomial() {
    const aInput = document.getElementById('binomA').value;
    const bInput = document.getElementById('binomB').value;
    const nInput = document.getElementById('binomN').value;
    const pInput = document.getElementById('binomP').value;

    const a = Math.ceil(parseFloat(normalizeNumberString(aInput)));
    const b = Math.floor(parseFloat(normalizeNumberString(bInput)));
    const n = parseInt(normalizeNumberString(nInput));
    const p = parsePValue(pInput);

    const probability = computeBinomProbability(a, b, n, p);
    currentInput = `Binom(a=${a}, b=${b}, n=${n}, p=${pInput || p})`;
    result = probability;
    shouldResetInput = true;
    updateDisplay();
}

function formatStepValue(value, step) {
    if (Math.abs(step) >= 1) {
        return String(Math.round(value));
    }
    const decimals = step.toString().split('.')[1]?.length || 0;
    const rounded = Math.round(value * Math.pow(10, decimals)) / Math.pow(10, decimals);
    const s = String(rounded)
        .replace(/\.0+$/, '')
        .replace(/(\.\d*?)0+$/, '$1');
    // UI: Verwende Dezimalkomma für Anzeige im BINOM-Panel
    return s.replace('.', ',');
}

function adjustBinomValue(targetId, step) {
    const input = document.getElementById(targetId);
    if (!input) return;
    const raw = normalizeNumberString(input.value || '0');
    const current = parseFloat(raw);
    const next = (Number.isNaN(current) ? 0 : current) + step;
    input.value = formatStepValue(next, step);
    updateBinomLiveResult();
}

function updateBinomLiveResult() {
    if (!document.getElementById('binPopup').classList.contains('open')) return;
    try {
        const a = Math.ceil(parseFloat(normalizeNumberString(document.getElementById('binomA').value)));
        const b = Math.floor(parseFloat(normalizeNumberString(document.getElementById('binomB').value)));
        const n = parseInt(normalizeNumberString(document.getElementById('binomN').value));
        const p = parsePValue(document.getElementById('binomP').value);
        const probability = computeBinomProbability(a, b, n, p);
        document.getElementById('binomLiveResult').textContent = formatGeneralResult(Math.round(probability * 1e6) / 1e6);
    } catch (error) {
        document.getElementById('binomLiveResult').textContent = 'Fehler';
    }
}

function bindBinomControls() {
    const binomInputs = document.querySelectorAll('#binPopup input');
    binomInputs.forEach((input) => {
        input.addEventListener('input', () => {
            updateBinomLiveResult();
        });
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                confirmBin();
            }
        });
    });

    const stepButtons = document.querySelectorAll('.binom-step');
    stepButtons.forEach((button) => {
        button.addEventListener('click', () => {
            const targetId = button.dataset.target;
            const step = parseFloat(button.dataset.step || '0');
            if (!targetId || Number.isNaN(step)) return;
            adjustBinomValue(targetId, step);
        });
    });
}

function bindLGSEnterKeys() {
    const lgsInputs = document.querySelectorAll('#lgsMatrix input');
    lgsInputs.forEach((input) => {
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                confirmLGS();
            }
        });
    });
}

// Equation Solver
function solveEquation(equation) {
    equation = normalizeNumberString(equation || '').trim();

    try {
        let [leftSide, rightSide] = equation.split('=').map(s => s.trim());
        if (!rightSide) rightSide = '0';

        function f(x) {
            let expr = `(${leftSide}) - (${rightSide})`;
            expr = addImplicitMultiplication(
                normalizeUnaryMinusExponent(
                    /* root infix disabled */ convertWurzelSyntax(convertLogBaseSyntax(convertCustomENotation(expr)))
                )
            );
            expr = normalizeConstants(expr)
                .replace(/x/g, `(${x})`)
                .replace(/\^/g, '**')
                .replace(/e\*\*/g, 'Math.E**')
                .replace(/sqrt/g, 'Math.sqrt')
                .replace(/root/g, 'root')
                .replace(/exp/g, 'Math.exp')
                // Replace ln first, then log - use word boundaries to avoid conflicts
                .replace(/\bln\b/g, 'Math.log')
                // Only replace standalone log(...) calls with Math.log10(...), but not Math.log
                .replace(/(?<!Math\.)\blog\s*\(/g, 'Math.log10(')
                .replace(/sin/g, 'Math.sin')
                .replace(/cos/g, 'Math.cos')
                .replace(/tan/g, 'Math.tan');
            return eval(expr);
        }

        function refineRoot(a, b, tolerance) {
            let fa = f(a);
            let fb = f(b);
            if (isNaN(fa) || isNaN(fb)) {
                return null;
            }
            if (Math.abs(fa) < tolerance) return a;
            if (Math.abs(fb) < tolerance) return b;
            if (fa * fb > 0) return null;

            let left = a;
            let right = b;
            for (let i = 0; i < 100; i++) {
                const mid = (left + right) / 2;
                const fm = f(mid);
                if (isNaN(fm)) {
                    return null;
                }
                if (Math.abs(fm) < tolerance) {
                    return mid;
                }
                if (fa * fm <= 0) {
                    right = mid;
                    fb = fm;
                } else {
                    left = mid;
                    fa = fm;
                }
            }
            const candidate = (left + right) / 2;
            const fc = f(candidate);
            if (!Number.isFinite(fc)) {
                return null;
            }
            const acceptanceTolerance = Math.max(tolerance * 10, 1e-4);
            if (Math.abs(fc) > acceptanceTolerance) {
                return null;
            }
            return candidate;
        }

        const tolerance = 0.000001;
        const rangeMin = -1000;
        const rangeMax = 1000;
        const steps = 20000;
        const step = (rangeMax - rangeMin) / steps;
        const roots = [];

        for (let i = 0; i < steps; i++) {
            const x1 = rangeMin + i * step;
            const x2 = x1 + step;
            const f1 = f(x1);
            const f2 = f(x2);

            if (isNaN(f1) || isNaN(f2)) {
                continue;
            }

            if (Math.abs(f1) < tolerance) {
                roots.push(x1);
                continue;
            }

            if (f1 * f2 < 0) {
                const root = refineRoot(x1, x2, tolerance);
                if (root !== null) {
                    roots.push(root);
                }
            }
        }

        const uniqueRoots = roots
            .map(r => Math.round(r * 1000000) / 1000000)
            .sort((a, b) => a - b)
            .filter((r, idx, arr) => idx === 0 || Math.abs(r - arr[idx - 1]) > 0.00001);

        if (uniqueRoots.length === 0) {
            result = 'Keine Lösung';
            currentInput = equation;
        } else {
            result = uniqueRoots.map((root, i) => `x${toSubscript(i + 1)}=${formatNumber(root)}`).join(', ');
            currentInput = `${equation} →`;
            shouldResetInput = true;
        }

        updateDisplay();
    } catch (error) {
        result = 'Fehler beim Lösen';
        currentInput = equation;
        updateDisplay();
    }
}

// Keyboard & Focus: keyboard handling
document.addEventListener('keydown', function (event) {
    if (!event.ctrlKey && !event.metaKey && !event.altKey && event.key.toLowerCase() === 'c') {
        const popupInputToClear = getOpenPopupInputToClear();
        if (popupInputToClear) {
            event.preventDefault();
            popupInputToClear.value = '';
            activeInputField = popupInputToClear;
            panelInputMode = true;
            if (popupInputToClear.closest('#graphPopup') && graphAutoPreviewFn) {
                graphAutoPreviewFn();
            }
            return;
        }
    }

    const isPanelInputFocused = activeInputField && document.activeElement === activeInputField;

    if (isPanelInputFocused && event.key !== 'Enter') {
        return;
    }

    if (event.key === 'Dead' && (event.code === 'Backquote' || event.code === 'BracketLeft')) {
        appendOperator('^');
        event.preventDefault();
    } else if (event.key >= '0' && event.key <= '9') {
        appendNumber(event.key);
    } else if (event.key === '(' || event.key === ')') {
        // Use context-aware parentheses insertion for both keys
        appendAutoParen();
    } else if (event.key === '+' || event.key === '-' || event.key === '*' || event.key === '/') {
        appendOperator(event.key);
    } else if (event.key === '^') {
        appendOperator('^');
        event.preventDefault();
    } else if (event.key === '=') {
        appendOperator('=');
    } else if (event.key === 'Enter') {
        event.preventDefault();
        handleExecute();
    } else if (event.key === 'Escape') {
        clearAll();
    } else if (event.key === 'Backspace') {
        backspace();
    }
});

// Keyboard & Focus: popup-input helper
function getOpenPopupInputToClear() {
    const activePopupInput =
        activeInputField &&
            activeInputField.tagName === 'INPUT' &&
            activeInputField.closest('#lgsPopup.open, #binPopup.open, #constPopup.open, #triPopup.open, #graphPopup.open')
            ? activeInputField
            : null;

    const focused = document.activeElement;
    const focusedPopupInput =
        focused &&
            focused.tagName === 'INPUT' &&
            focused.closest('#lgsPopup.open, #binPopup.open, #constPopup.open, #triPopup.open, #graphPopup.open')
            ? focused
            : null;

    return activePopupInput || focusedPopupInput || null;
}

// Keyboard & Focus: focus tracking
document.addEventListener('focusin', function (event) {
    if (event.target.tagName === 'INPUT' && event.target.type !== 'button') {
        activeInputField = event.target;
        // Set panelInputMode if the input is inside a popup
        const isInPopup = event.target.closest('#lgsPopup, #binPopup, #constPopup, #triPopup, #graphPopup');
        if (isInPopup) {
            panelInputMode = true;
        } else if (event.target.id === 'mainInput') {
            panelInputMode = false;
        }
    }
});

// Keyboard & Focus: main input click tracking
document.addEventListener('click', function (event) {
    if (event.target.closest('#mainInput')) {
        activeInputField = document.getElementById('mainInput');
    }
});

// Z-Index Management - brings clicked windows to front
function bringToFront(element) {
    currentZIndex++;
    element.style.zIndex = currentZIndex;
}

// Calculator Drag Support
function setupCalculatorDrag() {
    const calculator = document.querySelector('.calculator');
    if (!calculator) return;

    let dragState = null;

    const display = calculator.querySelector('.display');
    if (!display) return;

    display.addEventListener('pointerdown', (e) => {
        // Don't drag if clicking on buttons or inputs
        if (e.target.closest('button, input, select, textarea, a')) return;

        // Bring calculator to front when dragging
        bringToFront(calculator);

        e.preventDefault();
        e.stopPropagation();

        // Get current position from getBoundingClientRect for accuracy
        const rect = calculator.getBoundingClientRect();

        dragState = {
            startX: e.clientX,
            startY: e.clientY,
            initialLeft: rect.left,
            initialTop: rect.top
        };

        display.style.cursor = 'grabbing';
        calculator.classList.add('dragging');

        if (display.setPointerCapture) {
            display.setPointerCapture(e.pointerId);
        }
    });

    display.addEventListener('pointermove', (e) => {
        if (!dragState) return;

        const dx = e.clientX - dragState.startX;
        const dy = e.clientY - dragState.startY;

        const newLeft = dragState.initialLeft + dx;
        const newTop = dragState.initialTop + dy;

        calculator.style.position = 'fixed';
        calculator.style.left = `${newLeft}px`;
        calculator.style.top = `${newTop}px`;
        calculator.style.right = 'auto';
        calculator.style.bottom = 'auto';
        calculator.style.transform = 'none';
        calculator.style.margin = '0';
    });

    display.addEventListener('pointerup', (e) => {
        if (!dragState) return;

        if (display.releasePointerCapture) {
            try {
                display.releasePointerCapture(e.pointerId);
            } catch (err) {
                // Ignore errors if pointer was already released
            }
        }

        display.style.cursor = 'move';
        calculator.classList.remove('dragging');
        dragState = null;
        saveCalculatorPanelPosition();
    });

    display.addEventListener('pointercancel', (e) => {
        if (!dragState) return;

        if (display.releasePointerCapture) {
            try {
                display.releasePointerCapture(e.pointerId);
            } catch (err) {
                // Ignore errors if pointer was already released
            }
        }

        display.style.cursor = 'move';
        calculator.classList.remove('dragging');
        dragState = null;
        saveCalculatorPanelPosition();
    });

    // Bring calculator to front when clicked anywhere
    calculator.addEventListener('pointerdown', (e) => {
        bringToFront(calculator);
    });
}

// Popup Drag
function setupPopupDrag() {
    ['lgsPopup', 'binPopup', 'constPopup', 'triPopup', 'graphPopup'].forEach(popupId => {
        const popup = document.getElementById(popupId);
        const dragHandle = document.getElementById(popupId.replace('Popup', 'PopupDrag'));

        let dragState = null;

        dragHandle.addEventListener('pointerdown', (e) => {
            if (e.target.closest('.popup-close')) return;

            // Bring popup to front
            bringToFront(popup);

            e.preventDefault();
            e.stopPropagation();

            dragState = {
                startX: e.clientX,
                startY: e.clientY,
                initialLeft: popup.offsetLeft,
                initialTop: popup.offsetTop
            };

            // Use CSS class to enforce consistent move cursor during drag
            popup.classList.add('dragging');

            if (dragHandle.setPointerCapture) {
                dragHandle.setPointerCapture(e.pointerId);
            }
        });

        popup.addEventListener('pointerdown', (e) => {
            // Bring popup to front when content area is clicked
            bringToFront(popup);
        });

        dragHandle.addEventListener('pointermove', (e) => {
            if (!dragState) return;

            const dx = e.clientX - dragState.startX;
            const dy = e.clientY - dragState.startY;

            popup.style.left = `${dragState.initialLeft + dx}px`;
            popup.style.top = `${dragState.initialTop + dy}px`;
        });

        dragHandle.addEventListener('pointerup', (e) => {
            if (!dragState) return;

            if (dragHandle.releasePointerCapture) {
                try {
                    dragHandle.releasePointerCapture(e.pointerId);
                } catch (err) {
                    // Ignore errors if pointer was already released
                }
            }

            popup.classList.remove('dragging');
            if (typeof savePopupPosition === 'function') {
                savePopupPosition(popupId);
            }
            dragState = null;
        });

        dragHandle.addEventListener('pointercancel', (e) => {
            if (!dragState) return;

            if (dragHandle.releasePointerCapture) {
                try {
                    dragHandle.releasePointerCapture(e.pointerId);
                } catch (err) {
                    // Ignore errors if pointer was already released
                }
            }

            popup.classList.remove('dragging');
            if (typeof savePopupPosition === 'function') {
                savePopupPosition(popupId);
            }
            dragState = null;
        });
    });
}
function openConstPopup() { openPopup('constPopup'); }

function closeConstPopup() {
    closePopup('constPopup');
    if (!activeInputField?.closest('#lgsPopup.open, #binPopup.open, #graphPopup.open')) {
        returnFocusToMain();
    }
}

function openTriPopup() { openPopup('triPopup'); }

function closeTriPopup() {
    closePopup('triPopup');
    if (!activeInputField?.closest('#lgsPopup.open, #binPopup.open, #graphPopup.open')) {
        returnFocusToMain();
    }
}

// Initialization
function initCalculator() {
    // Register binom(a, b, n, p) as a custom math.js function for graph plotting
    if (typeof math !== 'undefined') {
        math.import({
            binom: function (a, b, n, p) {
                // When a === b (e.g. binom(x;x;n;p) for P(X=k) histogram),
                // use floor for both so non-integer x still lands in the right bin.
                // Otherwise use ceil(a)/floor(b) for cumulative ranges.
                const aInt = a === b ? Math.floor(a) : Math.ceil(a);
                return computeBinomProbability(aInt, Math.floor(b), Math.round(n), p);
            }
        }, { override: true });
    }

    initLGS();
    applyTouchInputLock();
    bindBinomControls();
    setupCalculatorDrag();
    setupPopupDrag();
    restoreCalculatorPanelPosition();
    restoreCalculatorCoreState();
    restoreCalculatorPopupInputState();
    updateDisplay();

    document.addEventListener('input', (event) => {
        if (!event.target?.closest('#calculator-overlay .popup')) return;
        saveCalculatorPopupInputState();
    });

    const mainInput = document.getElementById('mainInput');
    if (mainInput) {
        mainInput.addEventListener('input', () => {
            const value = mainInput.value || '';
            const start = mainInput.selectionStart ?? value.length;
            const end = mainInput.selectionEnd ?? start;

            // Replace 'pi' with 'π'
            if (value.toLowerCase().includes('pi')) {
                const before = value.slice(0, start);
                const selection = value.slice(start, end);
                const after = value.slice(end);
                const newBefore = before.replace(/pi/gi, 'π');
                const newSelection = selection.replace(/pi/gi, 'π');
                const newAfter = after.replace(/pi/gi, 'π');
                const nextValue = newBefore + newSelection + newAfter;
                if (nextValue !== value) {
                    mainInput.value = nextValue;
                    const nextStart = newBefore.length;
                    const nextEnd = newBefore.length + newSelection.length;
                    mainInput.setSelectionRange(nextStart, nextEnd);
                    return;
                }
            }

            // Strip any '√' characters from input
            if (value.includes('√')) {
                const before = value.slice(0, start);
                const selection = value.slice(start, end);
                const after = value.slice(end);
                const newBefore = before.replace(/√/g, '');
                const newSelection = selection.replace(/√/g, '');
                const newAfter = after.replace(/√/g, '');
                const nextValue = newBefore + newSelection + newAfter;
                if (nextValue !== value) {
                    mainInput.value = nextValue;
                    const nextStart = newBefore.length;
                    const nextEnd = newBefore.length + newSelection.length;
                    mainInput.setSelectionRange(nextStart, nextEnd);
                    return;
                }
            }

            // Format numbers with thousands separators as user types
            // First, prevent manual dot input - dots should only be added automatically
            // Allow dots only in valid thousand separator positions
            const cleanValue = value.replace(/\s/g, '');

            // Remove manually typed dots that are not part of proper number formatting
            // Keep only dots that are in proper thousand separator positions (every 3 digits from right)
            // Check if it's a simple number (only digits, optional minus at start, optional comma for decimals, and dots for thousands)
            if (/^-?[\d.,]*$/.test(cleanValue) && !cleanValue.match(/[+*/^=()a-zA-Zπ]/)) {
                // Remove all dots first
                const withoutDots = cleanValue.replace(/\./g, '');
                // Check if we have a valid number structure (digits with at most one comma)
                const commaCount = (withoutDots.match(/,/g) || []).length;
                if (commaCount <= 1) {
                    // Normalize comma to dot for processing
                    const normalized = withoutDots.replace(',', '.');
                    const parts = normalized.split('.');
                    const intPart = parts[0] || '';
                    const fracPart = parts[1];

                    // Only format if we have digits in the integer part
                    if (intPart && /^-?\d+$/.test(intPart)) {
                        // Add thousands separators to integer part
                        const formattedInt = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
                        const formatted = fracPart !== undefined ? `${formattedInt},${fracPart}` : formattedInt;

                        if (formatted !== value) {
                            mainInput.value = formatted;
                            // Adjust cursor position based on dots added/removed
                            const dotsBeforeCursor = (value.slice(0, start).match(/\./g) || []).length;
                            const dotsInFormatted = (formatted.slice(0, start).match(/\./g) || []).length;
                            const cursorAdjustment = dotsInFormatted - dotsBeforeCursor;
                            const newPosition = start + cursorAdjustment;
                            mainInput.setSelectionRange(newPosition, newPosition);
                        }
                    }
                }
            } else {
                // For expressions (not pure numbers), remove all dots that user might have typed
                // Dots should never appear in expressions like "e.", "2+3.", etc.
                const withoutDots = value.replace(/\./g, '');
                if (withoutDots !== value) {
                    mainInput.value = withoutDots;
                    // Adjust cursor - count how many dots were removed before cursor
                    const dotsRemovedBeforeCursor = (value.slice(0, start).match(/\./g) || []).length;
                    const newPosition = start - dotsRemovedBeforeCursor;
                    mainInput.setSelectionRange(newPosition, newPosition);
                }
            }
        });
        activeInputField = mainInput;

        mainInput.addEventListener('input', () => {
            currentInput = mainInput.value || '';
            saveCalculatorCoreState();
        });
    }

    window.addEventListener('beforeunload', () => {
        saveCalculatorCoreState();
        saveCalculatorPopupInputState();
    });
    window.addEventListener('pagehide', () => {
        saveCalculatorCoreState();
        saveCalculatorPopupInputState();
    });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCalculator);
} else {
    initCalculator();
}
