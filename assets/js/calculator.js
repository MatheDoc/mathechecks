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
        resultDisplay.textContent = result;
        if (shouldAnimateResult) {
            resultDisplay.classList.remove('updated');
            void resultDisplay.offsetWidth;
            resultDisplay.classList.add('updated');
            shouldAnimateResult = false;
        }
    }
}

function copyResult() {
    const value = String(result ?? '').trim();
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
    const inputs = document.querySelectorAll('#mainInput, #binomA, #binomB, #binomN, #binomP, #lgsMatrix input');
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

function appendNumber(num) {
    if (appendToActiveInput(String(num))) {
        return;
    }

    const mainInput = document.getElementById('mainInput');
    if (mainInput && activeInputField === mainInput) {
        insertAtCursor(mainInput, String(num));
    } else {
        if (shouldResetInput || currentInput === '0') {
            currentInput = String(num);
            shouldResetInput = false;
        } else {
            currentInput += num;
        }
        updateDisplay();
    }
}

function appendOperator(op) {
    if (appendToActiveInput(op)) {
        return;
    }

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

function appendFunction(func) {
    if (appendToActiveInput(func)) {
        return;
    }

    const mainInput = document.getElementById('mainInput');
    if (mainInput && activeInputField === mainInput) {
        insertAtCursor(mainInput, func);
    } else {
        if (shouldResetInput || currentInput === '0') {
            currentInput = func;
            shouldResetInput = false;
        } else {
            currentInput += func;
        }
        updateDisplay();
    }
}

function appendLogTemplate() {
    if (activeInputField && panelInputMode) {
        const currentValue = activeInputField.value || '';
        const start = activeInputField.selectionStart ?? currentValue.length;
        const end = activeInputField.selectionEnd ?? start;
        const template = 'log_()()';
        activeInputField.value =
            currentValue.slice(0, start) + template + currentValue.slice(end);
        setInputCursor(activeInputField, start + 5);
        return;
    }

    appendFunction('log_()()');
}

function appendRootTemplate() {
    const template = '()^(1/)';
    if (activeInputField && panelInputMode) {
        const currentValue = activeInputField.value || '';
        const start = activeInputField.selectionStart ?? currentValue.length;
        const end = activeInputField.selectionEnd ?? start;
        activeInputField.value = currentValue.slice(0, start) + template + currentValue.slice(end);
        // Place cursor inside the first parentheses to enter the radicand y
        setInputCursor(activeInputField, start + 1);
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
            /* root infix disabled */ convertLogBaseSyntax(normalized)
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
        result = formatGeneralResult(value);
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
        return value.toExponential(8);
    }
    // Otherwise, keep up to 9 decimal places and trim trailing zeros,
    // then format with German separators
    const text = (Math.round(value * 1e9) / 1e9).toString();
    const trimmed = text.replace(/\.0+$/, '').replace(/(\.\d*?)0+$/, '$1');
    return toGermanNumber(trimmed);
}

function toGermanNumber(text) {
    // Convert a plain numeric string with '.' decimal to German format
    // using ',' as decimal and '.' as thousands
    if (typeof text !== 'string') text = String(text ?? '');
    if (!text) return '';
    let sign = '';
    if (text.startsWith('-')) {
        sign = '-';
        text = text.slice(1);
    }
    const parts = text.split('.');
    const intPart = parts[0] || '0';
    const fracPart = parts[1] || '';
    const grouped = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    return fracPart ? `${sign}${grouped},${fracPart}` : `${sign}${grouped}`;
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
    if (inputValue.trim().match(/^binom\s*\(/i)) {
        executeBinFromInput(inputValue);
        return;
    }

    // Check for equation (single =)
    const equalsCount = (inputValue.match(/=/g) || []).length;
    if (equalsCount === 1) {
        solveEquation(inputValue);
        return;
    }

    // Normal calculation
    currentInput = inputValue;
    calculate();
}

function executeLGSFromInput(input) {
    try {
        // Support new syntax lgs(eq1;eq2;...) and gracefully handle legacy {eq1;eq2;...}
        let content = input.trim();
        const m = content.match(/^lgs\s*\((.*)\)\s*$/i);
        if (m) {
            content = m[1];
        } else if (content.startsWith('{') && content.endsWith('}')) {
            content = content.slice(1, -1);
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

// Evaluate a scalar numeric expression, allowing functions and constants,
// while substituting provided single-letter variables with 0.
function evaluateScalarExpression(expr, varNames) {
    try {
        let normalized = normalizeNumberString(expr || '');
        normalized = normalizeExpression(normalized);
        // Replace single-letter variables with 0 using token boundaries
        varNames.forEach((v) => {
            const re = new RegExp(`(^|[^a-zA-Z0-9_.])${v}([^a-zA-Z0-9_]|$)`, 'g');
            normalized = normalized.replace(re, '$10$2');
        });
        const value = eval(normalized);
        return typeof value === 'number' && Number.isFinite(value) ? value : 0;
    } catch (e) {
        return 0;
    }
}

// Evaluate the linear coefficient of targetVar in expr,
// by setting targetVar=1 and others=0, then subtracting the baseline.
function evaluateCoefficient(expr, varNames, targetVar) {
    try {
        let normalized = normalizeNumberString(expr || '');
        normalized = normalizeExpression(normalized);

        // Build expression with targetVar=1, others=0
        varNames.forEach((v) => {
            const re = new RegExp(`(^|[^a-zA-Z0-9_.])${v}([^a-zA-Z0-9_]|$)`, 'g');
            normalized = normalized.replace(re, (match, p1, p2) => {
                const val = v === targetVar ? '1' : '0';
                return `${p1}${val}${p2}`;
            });
        });

        const withOne = eval(normalized);
        const baseline = evaluateScalarExpression(expr, varNames);
        const coeff = (withOne ?? 0) - (baseline ?? 0);
        return typeof coeff === 'number' && Number.isFinite(coeff) ? coeff : 0;
    } catch (e) {
        return 0;
    }
}

function executeBinFromInput(input) {
    try {
        const match = input.match(/binom\s*\(\s*([^;]+)\s*;\s*([^;]+)\s*;\s*([^;]+)\s*;\s*([^)]+)\s*\)/i);
        if (!match) {
            throw new Error('Invalid format');
        }

        const aRaw = parseFloat(normalizeNumberString(match[1]));
        const bRaw = parseFloat(normalizeNumberString(match[2]));
        const n = parseInt(normalizeNumberString(match[3]));
        const pValue = normalizeNumberString(match[4]);

        let p = NaN;
        if (pValue.includes('/')) {
            const parts = pValue.split('/').map((part) => parseFloat(part.trim()));
            if (parts.length === 2 && parts.every((part) => !Number.isNaN(part)) && parts[1] !== 0) {
                p = parts[0] / parts[1];
            }
        } else {
            p = parseFloat(pValue);
        }

        const a = Math.ceil(aRaw);
        const b = Math.floor(bRaw);

        let probability = 0;
        for (let k = a; k <= b; k++) {
            const binomCoeff = binomialCoefficient(n, k);
            probability += binomCoeff * Math.pow(p, k) * Math.pow(1 - p, n - k);
        }

        currentInput = `Binom(a=${a}, b=${b}, n=${n}, p=${match[4]})`;
        result = formatGeneralResult(probability);
        shouldResetInput = true;
        updateDisplay();
    } catch (error) {
        result = 'Fehler in BINOM';
        updateDisplay();
    }
}

function addImplicitMultiplication(value) {
    return value
        .replace(/(\d)([a-zA-Zπ(])/g, '$1*$2')
        .replace(/(\))([\d(])/g, '$1*$2')
        .replace(/(\))([a-zA-Zπ])/g, '$1*$2');
}

function normalizeUnaryMinusExponent(value) {
    return value
        .replace(/(^|[+\-*/(=])\s*-\s*([a-zA-Z0-9.]+)\s*\^/g, '$1(-1)*$2^')
        .replace(/(^|[+\-*/(=])\s*-\s*(\([^()]*\))\s*\^/g, '$1(-1)*$2^');
}

function normalizeConstants(value) {
    return value
        .replace(/(^|[^a-zA-Z0-9_.])e([^a-zA-Z0-9_]|$)/g, '$1Math.E$2')
        .replace(/(^|[^a-zA-Z0-9_.])pi([^a-zA-Z0-9_]|$)/gi, '$1Math.PI$2')
        .replace(/π/g, 'Math.PI');
}

function convertRootInfix(value) {
    let expr = value;
    let index = expr.indexOf('√');

    while (index !== -1) {
        const left = findLeftOperand(expr, index - 1);
        const right = findRightOperand(expr, index + 1);

        if (!left || !right) {
            break;
        }

        const leftValue = expr.slice(left.start, left.end + 1);
        const rightValue = expr.slice(right.start, right.end + 1);

        expr = `${expr.slice(0, left.start)}root(${leftValue},${rightValue})${expr.slice(right.end + 1)}`;
        index = expr.indexOf('√');
    }

    return expr;
}

function convertLogBaseSyntax(value) {
    let expr = value;
    let index = expr.indexOf('log_(');

    while (index !== -1) {
        const baseStart = index + 4;
        const base = extractParenthesized(expr, baseStart);
        if (!base) {
            break;
        }

        const afterBase = base.end + 1;
        const valueStart = findNextNonSpace(expr, afterBase);
        if (valueStart === null || expr[valueStart] !== '(') {
            break;
        }

        const valuePart = extractParenthesized(expr, valueStart);
        if (!valuePart) {
            break;
        }

        const baseValue = expr.slice(base.start + 1, base.end);
        const valueValue = expr.slice(valuePart.start + 1, valuePart.end);
        expr = `${expr.slice(0, index)}logBase(${baseValue},${valueValue})${expr.slice(valuePart.end + 1)}`;
        index = expr.indexOf('log_(');
    }

    return expr;
}

function extractParenthesized(expr, startIndex) {
    if (expr[startIndex] !== '(') {
        return null;
    }

    let depth = 1;
    let i = startIndex + 1;
    while (i < expr.length) {
        if (expr[i] === '(') depth++;
        if (expr[i] === ')') depth--;
        if (depth === 0) break;
        i++;
    }
    if (i >= expr.length) {
        return null;
    }
    return { start: startIndex, end: i };
}

function findNextNonSpace(expr, startIndex) {
    let i = startIndex;
    while (i < expr.length && expr[i] === ' ') {
        i++;
    }
    return i < expr.length ? i : null;
}

function logBase(base, value) {
    return Math.log(value) / Math.log(base);
}

function findLeftOperand(expr, endIndex) {
    let end = endIndex;
    while (end >= 0 && expr[end] === ' ') {
        end--;
    }
    if (end < 0) return null;

    if (expr[end] === ')') {
        let depth = 1;
        let i = end - 1;
        while (i >= 0) {
            if (expr[i] === ')') depth++;
            if (expr[i] === '(') depth--;
            if (depth === 0) break;
            i--;
        }
        if (i < 0) return null;
        return { start: i, end };
    }

    let i = end;
    while (i >= 0 && /[a-zA-Z0-9.]/.test(expr[i])) {
        i--;
    }
    let start = i + 1;
    if (start > 0 && expr[start - 1] === '-' && (start - 1 === 0 || /[+\-*/(=]/.test(expr[start - 2]))) {
        start--;
    }
    return start <= end ? { start, end } : null;
}

function findRightOperand(expr, startIndex) {
    let start = startIndex;
    while (start < expr.length && expr[start] === ' ') {
        start++;
    }
    if (start >= expr.length) return null;

    if (expr[start] === '(') {
        let depth = 1;
        let i = start + 1;
        while (i < expr.length) {
            if (expr[i] === '(') depth++;
            if (expr[i] === ')') depth--;
            if (depth === 0) break;
            i++;
        }
        if (i >= expr.length) return null;
        return { start, end: i };
    }

    let i = start;
    if (expr[i] === '-' && i + 1 < expr.length && /[a-zA-Z0-9(]/.test(expr[i + 1])) {
        i++;
    }
    while (i < expr.length && /[a-zA-Z0-9.]/.test(expr[i])) {
        i++;
    }
    const end = i - 1;
    return end >= start ? { start, end } : null;
}

function root(x, y) {
    return Math.pow(y, 1 / x);
}

function toggleSign() {
    if (activeInputField) {
        const value = activeInputField.value || '';
        if (value.startsWith('-')) {
            activeInputField.value = value.slice(1);
        } else if (value.length > 0) {
            activeInputField.value = '-' + value;
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
    const isInOpenPopup = activeInputField.closest('#lgsPopup.open, #binPopup.open');
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
}

function setInputCursor(input, position) {
    input.focus({ preventScroll: true });
    if (input.setSelectionRange) {
        input.setSelectionRange(position, position);
    }
}

function normalizeNumberString(value) {
    return value.replace(/,/g, '.');
}

function openLGSPopup() {
    document.getElementById('lgsOverlay').classList.add('open');
    const popup = document.getElementById('lgsPopup');
    popup.classList.add('open');
    bringToFront(popup);
    centerPopup('lgsPopup');
    renderLGS();
    // Focus the first input in the LGS matrix
    const firstLgsInput = document.querySelector('#lgsMatrix input');
    if (firstLgsInput) {
        panelInputMode = true;
        activeInputField = firstLgsInput;
        firstLgsInput.focus({ preventScroll: true });
        setInputCursor(firstLgsInput, firstLgsInput.value?.length || 0);
    }
}

function closeLGSPopup() {
    document.getElementById('lgsOverlay').classList.remove('open');
    document.getElementById('lgsPopup').classList.remove('open');
    panelInputMode = false;
    const mainInput = document.getElementById('mainInput');
    if (mainInput) {
        activeInputField = mainInput;
        mainInput.focus({ preventScroll: true });
    }
}

function confirmLGS() {
    const varNames = ['x', 'y', 'z', 'u', 'v', 'w'];
    const equations = [];

    for (let i = 0; i < lgsEquations; i++) {
        const terms = [];
        for (let j = 0; j < lgsVariables; j++) {
            const coeff = parseFloat(document.getElementById(`a${i}${j}`).value || '0');
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
    document.getElementById('binOverlay').classList.add('open');
    const popup = document.getElementById('binPopup');
    popup.classList.add('open');
    bringToFront(popup);
    centerPopup('binPopup');
    updateBinomLiveResult();
    // Focus the first BIN input (a)
    const aInput = document.getElementById('binomA');
    if (aInput) {
        panelInputMode = true;
        activeInputField = aInput;
        aInput.focus({ preventScroll: true });
        setInputCursor(aInput, aInput.value?.length || 0);
    }
}

function closeBinPopup() {
    document.getElementById('binOverlay').classList.remove('open');
    document.getElementById('binPopup').classList.remove('open');
    panelInputMode = false;
    const mainInput = document.getElementById('mainInput');
    if (mainInput) {
        activeInputField = mainInput;
        mainInput.focus({ preventScroll: true });
    }
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

function centerPopup(popupId) {
    const popup = document.getElementById(popupId);
    const calculator = document.querySelector('.calculator');
    if (!calculator) return;

    const calcRect = calculator.getBoundingClientRect();
    const popupRect = popup.getBoundingClientRect();

    // Center relative to calculator
    const left = calcRect.left + (calcRect.width - popupRect.width) / 2;
    const top = calcRect.top + (calcRect.height - popupRect.height) / 2;

    popup.style.left = `${left}px`;
    popup.style.top = `${top}px`;
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
    const nInput = document.getElementById('binomN').value;
    const pInput = document.getElementById('binomP').value;
    const aInput = document.getElementById('binomA').value;
    const bInput = document.getElementById('binomB').value;

    const n = parseInt(normalizeNumberString(nInput));
    const pValue = normalizeNumberString(pInput);
    let p = NaN;
    if (pValue.includes('/')) {
        const parts = pValue.split('/').map((part) => parseFloat(part.trim()));
        if (parts.length === 2 && parts.every((part) => !Number.isNaN(part)) && parts[1] !== 0) {
            p = parts[0] / parts[1];
        }
    } else {
        p = parseFloat(pValue);
    }
    const aRaw = parseFloat(normalizeNumberString(aInput));
    const bRaw = parseFloat(normalizeNumberString(bInput));
    const a = Math.ceil(aRaw);
    const b = Math.floor(bRaw);

    let probability = 0;
    for (let k = a; k <= b; k++) {
        const binomCoeff = binomialCoefficient(n, k);
        probability += binomCoeff * Math.pow(p, k) * Math.pow(1 - p, n - k);
    }

    const pDisplay = pInput !== '' ? pInput : String(p);
    currentInput = `Binom(a=${a}, b=${b}, n=${n}, p=${pDisplay})`;
    result = formatGeneralResult(probability);
    shouldResetInput = true;
    updateDisplay();
}

function formatStepValue(value, step) {
    if (Math.abs(step) >= 1) {
        return String(Math.round(value));
    }
    const decimals = step.toString().split('.')[1]?.length || 0;
    const rounded = Math.round(value * Math.pow(10, decimals)) / Math.pow(10, decimals);
    return String(rounded).replace(/\.0+$/, '').replace(/(\.\d*?)0+$/, '$1');
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
    const binPopup = document.getElementById('binPopup');
    if (!binPopup.classList.contains('open')) return;

    try {
        const nInput = document.getElementById('binomN').value;
        const pInput = document.getElementById('binomP').value;
        const aInput = document.getElementById('binomA').value;
        const bInput = document.getElementById('binomB').value;

        const n = parseInt(normalizeNumberString(nInput));
        const pValue = normalizeNumberString(pInput);
        let p = NaN;
        if (pValue.includes('/')) {
            const parts = pValue.split('/').map((part) => parseFloat(part.trim()));
            if (parts.length === 2 && parts.every((part) => !Number.isNaN(part)) && parts[1] !== 0) {
                p = parts[0] / parts[1];
            }
        } else {
            p = parseFloat(pValue);
        }
        const aRaw = parseFloat(normalizeNumberString(aInput));
        const bRaw = parseFloat(normalizeNumberString(bInput));
        const a = Math.ceil(aRaw);
        const b = Math.floor(bRaw);

        let probability = 0;
        for (let k = a; k <= b; k++) {
            const binomCoeff = binomialCoefficient(n, k);
            probability += binomCoeff * Math.pow(p, k) * Math.pow(1 - p, n - k);
        }

        const rounded = Math.round(probability * 1000000) / 1000000;
        document.getElementById('binomLiveResult').textContent = formatGeneralResult(rounded);
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
                    /* root infix disabled */ convertLogBaseSyntax(expr)
                )
            );
            expr = normalizeConstants(expr)
                .replace(/x/g, `(${x})`)
                .replace(/\^/g, '**')
                .replace(/e\*\*/g, 'Math.E**')
                .replace(/sqrt/g, 'Math.sqrt')
                .replace(/root/g, 'root')
                .replace(/exp/g, 'Math.exp')
                .replace(/ln/g, 'Math.log')
                .replace(/log/g, 'Math.log10')
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
            return (left + right) / 2;
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

// Keyboard Support
document.addEventListener('keydown', function (event) {
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
    } else if (event.key === '(' || event.key === ')') {
        appendNumber(event.key);
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

// Focus Management
document.addEventListener('focusin', function (event) {
    if (event.target.tagName === 'INPUT' && event.target.type !== 'button') {
        activeInputField = event.target;
    }
});

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

        // Don't bring calculator to front if any popup is open
        const hasOpenPopup = document.querySelector('#lgsPopup.open, #binPopup.open');
        if (!hasOpenPopup) {
            bringToFront(calculator);
        }

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
    });

    // Bring calculator to front when clicked anywhere (but not if popup is open)
    calculator.addEventListener('pointerdown', (e) => {
        const hasOpenPopup = document.querySelector('#lgsPopup.open, #binPopup.open');
        if (!hasOpenPopup) {
            bringToFront(calculator);
        }
    });
}

// Popup Drag
function setupPopupDrag() {
    ['lgsPopup', 'binPopup', 'constPopup', 'triPopup'].forEach(popupId => {
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
            dragState = null;
        });
    });
}
function openConstPopup() {
    document.getElementById('constOverlay').classList.add('open');
    const popup = document.getElementById('constPopup');
    popup.classList.add('open');
    bringToFront(popup);
    centerPopup('constPopup');
}

function closeConstPopup() {
    document.getElementById('constOverlay').classList.remove('open');
    document.getElementById('constPopup').classList.remove('open');
    const mainInput = document.getElementById('mainInput');
    if (mainInput) {
        activeInputField = mainInput;
        mainInput.focus({ preventScroll: true });
    }
}

function openTriPopup() {
    document.getElementById('triOverlay').classList.add('open');
    const popup = document.getElementById('triPopup');
    popup.classList.add('open');
    bringToFront(popup);
    centerPopup('triPopup');
}

function closeTriPopup() {
    document.getElementById('triOverlay').classList.remove('open');
    document.getElementById('triPopup').classList.remove('open');
    const mainInput = document.getElementById('mainInput');
    if (mainInput) {
        activeInputField = mainInput;
        mainInput.focus({ preventScroll: true });
    }
}

// Initialization
function initCalculator() {
    initLGS();
    updateDisplay();
    applyTouchInputLock();
    bindBinomControls();
    setupCalculatorDrag();
    setupPopupDrag();

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
                }
            }
        });
        activeInputField = mainInput;
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCalculator);
} else {
    initCalculator();
}
