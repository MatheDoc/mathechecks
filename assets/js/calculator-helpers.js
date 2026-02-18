// Calculator helper functions

// Add thousands separators (.) to a number
function addThousandsSeparators(value) {
    if (typeof value === 'number') {
        value = String(value);
    }
    if (typeof value !== 'string') return value;

    const parts = value.split(',');
    const intPart = parts[0] || '';
    const fracPart = parts[1];
    const formatted = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, '.');

    return fracPart !== undefined ? `${formatted},${fracPart}` : formatted;
}

// Remove thousands separators (.) from a number
function removeThousandsSeparators(value) {
    if (typeof value !== 'string') return value;
    return value.replace(/\./g, '');
}

function toGermanNumber(text) {
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
    const formattedInt = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, '.');

    return fracPart ? `${sign}${formattedInt},${fracPart}` : `${sign}${formattedInt}`;
}

function addImplicitMultiplication(value) {
    return value
        .replace(/(\d)([a-df-zA-DF-Zπ(])/g, '$1*$2')
        .replace(/(\d)([eE])(?![+\-\d])/g, '$1*$2')
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

// Split string at first top-level semicolon (not inside parentheses)
function splitTopLevelSemicolon(str) {
    let depth = 0;
    for (let i = 0; i < str.length; i++) {
        const ch = str[i];
        if (ch === '(') depth++;
        else if (ch === ')') depth--;
        else if (ch === ';' && depth === 0) return i;
    }
    return -1;
}

function convertLogBaseSyntax(value) {
    let expr = value;
    let idx = expr.indexOf('log(');
    while (idx !== -1) {
        const argsParen = extractParenthesized(expr, idx + 3);
        if (!argsParen) break;
        const inner = expr.slice(argsParen.start + 1, argsParen.end);
        const sepPos = splitTopLevelSemicolon(inner);
        if (sepPos === -1) {
            idx = expr.indexOf('log(', argsParen.end + 1);
            continue;
        }
        const baseStr = inner.slice(0, sepPos).trim();
        const valueStr = inner.slice(sepPos + 1).trim();
        expr = `${expr.slice(0, idx)}logBase(${baseStr},${valueStr})${expr.slice(argsParen.end + 1)}`;
        idx = expr.indexOf('log(');
    }
    return expr;
}

function convertLogBaseSyntaxForMathJS(value) {
    let expr = value;
    let idx = expr.indexOf('log(');
    while (idx !== -1) {
        const argsParen = extractParenthesized(expr, idx + 3);
        if (!argsParen) break;
        const inner = expr.slice(argsParen.start + 1, argsParen.end);
        const sepPos = splitTopLevelSemicolon(inner);
        if (sepPos === -1) {
            idx = expr.indexOf('log(', argsParen.end + 1);
            continue;
        }
        const baseStr = inner.slice(0, sepPos).trim();
        const valueStr = inner.slice(sepPos + 1).trim();
        expr = `${expr.slice(0, idx)}logb(${valueStr}, ${baseStr})${expr.slice(argsParen.end + 1)}`;
        idx = expr.indexOf('log(');
    }
    return expr;
}

function convertWurzelSyntax(value) {
    let expr = value;
    let idx = expr.indexOf('wurzel(');
    while (idx !== -1) {
        const argsParen = extractParenthesized(expr, idx + 6);
        if (!argsParen) break;
        const inner = expr.slice(argsParen.start + 1, argsParen.end);
        const sepPos = splitTopLevelSemicolon(inner);
        if (sepPos === -1) {
            expr = `${expr.slice(0, idx)}Math.sqrt(${inner.trim()})${expr.slice(argsParen.end + 1)}`;
        } else {
            const xStr = inner.slice(0, sepPos).trim();
            const yStr = inner.slice(sepPos + 1).trim();
            expr = `${expr.slice(0, idx)}Math.pow(${xStr}, 1/(${yStr}))${expr.slice(argsParen.end + 1)}`;
        }
        idx = expr.indexOf('wurzel(');
    }
    return expr;
}

function convertBinomSyntaxForMathJS(value) {
    let expr = value;
    let idx = expr.indexOf('binom(');
    while (idx !== -1) {
        const argsParen = extractParenthesized(expr, idx + 5);
        if (!argsParen) break;
        const inner = expr.slice(argsParen.start + 1, argsParen.end);
        let converted = '';
        let depth = 0;
        for (let i = 0; i < inner.length; i++) {
            const ch = inner[i];
            if (ch === '(') { depth++; converted += ch; }
            else if (ch === ')') { depth--; converted += ch; }
            else if (ch === ';' && depth === 0) converted += ', ';
            else converted += ch;
        }
        expr = `${expr.slice(0, argsParen.start + 1)}${converted}${expr.slice(argsParen.end)}`;
        idx = expr.indexOf('binom(', argsParen.start + 1 + converted.length + 1);
    }
    return expr;
}

function convertWurzelSyntaxForMathJS(value) {
    let expr = value;
    let idx = expr.indexOf('wurzel(');
    while (idx !== -1) {
        const argsParen = extractParenthesized(expr, idx + 6);
        if (!argsParen) break;
        const inner = expr.slice(argsParen.start + 1, argsParen.end);
        const sepPos = splitTopLevelSemicolon(inner);
        if (sepPos === -1) {
            expr = `${expr.slice(0, idx)}sqrt(${inner.trim()})${expr.slice(argsParen.end + 1)}`;
        } else {
            const xStr = inner.slice(0, sepPos).trim();
            const yStr = inner.slice(sepPos + 1).trim();
            expr = `${expr.slice(0, idx)}(${xStr})^(1/(${yStr}))${expr.slice(argsParen.end + 1)}`;
        }
        idx = expr.indexOf('wurzel(');
    }
    return expr;
}

function convertCustomENotation(value) {
    if (typeof value !== 'string') return value;

    let result = value.replace(/(pi|π|e)\s*E\s*([+\-])\s*(\d+)/gi,
        (match, constant, sign, exp) => `${constant}*1e${sign}${exp}`
    );

    result = result.replace(/(-?\d+(?:\.\d+)?)\s*E\s*([+\-])\s*(\d+)/gi,
        (match, mantissa, sign, exp) => `${mantissa}e${sign}${exp}`
    );

    return result;
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

function logBase(base, value) {
    return Math.log(value) / Math.log(base);
}
