const DevCalculatorUtils = (() => {
    function normalizeNumberString(value) {
        return String(value ?? '').replace(/\./g, '').replace(/,/g, '.');
    }

    function binomialCoefficient(n, k) {
        const normalizedN = Number(n);
        const normalizedK = Number(k);
        if (!Number.isInteger(normalizedN) || !Number.isInteger(normalizedK)) return NaN;
        if (normalizedN < 0 || normalizedK < 0) return NaN;
        if (normalizedK > normalizedN) return 0;
        if (normalizedK === 0 || normalizedK === normalizedN) return 1;
        let result = 1;
        for (let i = 1; i <= normalizedK; i++) {
            result = (result * (normalizedN - (normalizedK - i))) / i;
        }
        return Math.round(result);
    }

    function factorial(value) {
        const normalizedValue = Number(value);
        if (!Number.isInteger(normalizedValue) || normalizedValue < 0) {
            return NaN;
        }
        let result = 1;
        for (let i = 2; i <= normalizedValue; i++) {
            result *= i;
        }
        return result;
    }

    function computeBinomProbability(a, b, n, p) {
        if (!Number.isFinite(a) || !Number.isFinite(b) || !Number.isFinite(n) || !Number.isFinite(p)) {
            return NaN;
        }
        if (n < 0 || p < 0 || p > 1) {
            return NaN;
        }
        if (b < a) {
            return 0;
        }
        let probability = 0;
        for (let k = a; k <= b; k++) {
            probability += binomialCoefficient(n, k) * Math.pow(p, k) * Math.pow(1 - p, n - k);
        }
        return probability;
    }

    function __binom(a, b, n, p) {
        return computeBinomProbability(
            Math.ceil(Number(a)),
            Math.floor(Number(b)),
            Math.trunc(Number(n)),
            Number(p)
        );
    }

    function logBase(base, value) {
        const normalizedBase = Number(base);
        const normalizedValue = Number(value);
        if (!Number.isFinite(normalizedBase) || !Number.isFinite(normalizedValue)) {
            return NaN;
        }
        if (normalizedBase <= 0 || normalizedBase === 1 || normalizedValue <= 0) {
            return NaN;
        }
        return Math.log(normalizedValue) / Math.log(normalizedBase);
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

    function extractParenthesized(expr, startIndex) {
        if (expr[startIndex] !== '(') return null;
        let depth = 1;
        let i = startIndex + 1;
        while (i < expr.length) {
            if (expr[i] === '(') depth++;
            if (expr[i] === ')') depth--;
            if (depth === 0) break;
            i++;
        }
        if (i >= expr.length) return null;
        return { start: startIndex, end: i };
    }

    function convertCustomENotation(value) {
        if (typeof value !== 'string') return value;
        let result = value.replace(/(pi|π|e)\s*E\s*([+\-])\s*(\d+)/gi,
            (match, constant, sign, exp) => `${constant}*1e${sign}${exp}`);
        result = result.replace(/(-?\d+(?:\.\d+)?)\s*E\s*([+\-])\s*(\d+)/gi,
            (match, mantissa, sign, exp) => `${mantissa}e${sign}${exp}`);
        return result;
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

    function convertNCrSyntax(value) {
        let expr = value;
        let idx = expr.toLowerCase().indexOf('ncr(');
        while (idx !== -1) {
            const argsParen = extractParenthesized(expr, idx + 3);
            if (!argsParen) break;
            const inner = expr.slice(argsParen.start + 1, argsParen.end);
            const sepPos = splitTopLevelSemicolon(inner);
            if (sepPos === -1) {
                idx = expr.toLowerCase().indexOf('ncr(', argsParen.end + 1);
                continue;
            }
            const nStr = inner.slice(0, sepPos).trim();
            const kStr = inner.slice(sepPos + 1).trim();
            expr = `${expr.slice(0, idx)}DevCalculatorUtils.binomialCoefficient(${nStr},${kStr})${expr.slice(argsParen.end + 1)}`;
            idx = expr.toLowerCase().indexOf('ncr(');
        }
        return expr;
    }

    function extractFactorialOperand(expr, endIndex) {
        let index = endIndex;
        while (index >= 0 && /\s/.test(expr[index])) {
            index -= 1;
        }
        if (index < 0) return null;

        if (expr[index] === ')') {
            let depth = 1;
            let start = index - 1;
            while (start >= 0) {
                if (expr[start] === ')') depth += 1;
                if (expr[start] === '(') depth -= 1;
                if (depth === 0) {
                    return { start, end: index };
                }
                start -= 1;
            }
            return null;
        }

        let start = index;
        while (start >= 0 && /[A-Za-z0-9_.]/.test(expr[start])) {
            start -= 1;
        }
        if (start === index) return null;
        return { start: start + 1, end: index };
    }

    function convertFactorialSyntax(value) {
        let expr = value;
        let idx = expr.indexOf('!');
        while (idx !== -1) {
            const operand = extractFactorialOperand(expr, idx - 1);
            if (!operand) {
                idx = expr.indexOf('!', idx + 1);
                continue;
            }
            const source = expr.slice(operand.start, idx).trim();
            expr = `${expr.slice(0, operand.start)}DevCalculatorUtils.factorial(${source})${expr.slice(idx + 1)}`;
            idx = expr.indexOf('!');
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
                if (ch === '(') {
                    depth++;
                    converted += ch;
                } else if (ch === ')') {
                    depth--;
                    converted += ch;
                } else if (ch === ';' && depth === 0) {
                    converted += ', ';
                } else {
                    converted += ch;
                }
            }
            expr = `${expr.slice(0, argsParen.start + 1)}${converted}${expr.slice(argsParen.end)}`;
            idx = expr.indexOf('binom(', argsParen.start + converted.length + 2);
        }
        return expr;
    }

    function normalizeExpression(input) {
        const normalized = normalizeNumberString(input);
        let expression = addImplicitMultiplication(
            normalizeUnaryMinusExponent(
                convertFactorialSyntax(
                    convertNCrSyntax(
                        convertBinomSyntaxForMathJS(convertWurzelSyntax(convertLogBaseSyntax(convertCustomENotation(normalized))))
                    )
                )
            )
        );
        return normalizeConstants(expression)
            .replace(/×/g, '*')
            .replace(/÷/g, '/')
            .replace(/−/g, '-')
            .replace(/\^/g, '**')
            .replace(/(?<!Math\.)\babs\s*\(/g, 'Math.abs(')
            .replace(/(?<!Math\.)\bbetrag\s*\(/gi, 'Math.abs(')
            .replace(/(?<!Math\.)\bsqrt\s*\(/g, 'Math.sqrt(')
            .replace(/(?<!Math\.)\bexp\s*\(/g, 'Math.exp(')
            .replace(/(?<!Math\.)\bln\s*\(/g, 'Math.log(')
            .replace(/(?<!DevCalculatorUtils\.)\blogBase\s*\(/g, 'DevCalculatorUtils.logBase(')
            .replace(/\bbinom\s*\(/g, '__binom(')
            .replace(/(?<!Math\.)\basin\s*\(/g, 'Math.asin(')
            .replace(/(?<!Math\.)\bacos\s*\(/g, 'Math.acos(')
            .replace(/(?<!Math\.)\batan\s*\(/g, 'Math.atan(')
            .replace(/(?<!Math\.)\bsin\s*\(/g, 'Math.sin(')
            .replace(/(?<!Math\.)\bcos\s*\(/g, 'Math.cos(')
            .replace(/(?<!Math\.)\btan\s*\(/g, 'Math.tan(');
    }

    function prepareGraphExpression(input) {
        const validENotation = /((?:\d+(?:\.\d+)?)|(?:pi)|(?:\u03c0)|(?:e))\s*E\s*[+\-]\s*\d+/gi;
        if (/E/.test(String(input ?? '').replace(validENotation, '___VALID___'))) return null;
        let expr = convertCustomENotation(String(input ?? ''));
        expr = expr.replace(/(\d),(\d)/g, '$1.$2');
        expr = convertBinomSyntaxForMathJS(expr);
        expr = convertLogBaseSyntaxForMathJS(expr);
        expr = convertWurzelSyntaxForMathJS(expr);
        expr = expr.replace(/\bbetrag\s*\(/gi, 'abs(');
        expr = expr.replace(/\blog\s*\(/g, 'log10(');
        expr = expr.replace(/\bln\s*\(/g, 'log(');
        expr = expr.replace(/\blogb\s*\(/g, 'log(');
        return expr;
    }

    function evaluateExpression(expression) {
        const normalized = normalizeExpression(expression);
        return eval(normalized);
    }

    function evaluateWithAssignments(expr, varNames, assignments) {
        let prepared = String(expr || '');
        varNames.forEach((variableName) => {
            const re = new RegExp(`(^|[^a-zA-Z0-9_.])${variableName}([^a-zA-Z0-9_]|$)`, 'g');
            const value = Object.prototype.hasOwnProperty.call(assignments, variableName)
                ? String(assignments[variableName])
                : '0';
            prepared = prepared.replace(re, `$1(${value})$2`);
        });
        const normalized = normalizeExpression(prepared);
        const result = eval(normalized);
        return typeof result === 'number' ? result : NaN;
    }

    function formatGeneralResult(value) {
        if (typeof value !== 'number' || !Number.isFinite(value)) {
            return 'Fehler';
        }
        const abs = Math.abs(value);
        if (abs !== 0 && (abs < 1e-4 || abs >= 1e9)) {
            const exp = value.toExponential(8);
            const [mantissa, exponent] = exp.split('e');
            const mTrim = mantissa.replace(/\.0+$/, '').replace(/(\.\d*?)0+$/, '$1');
            const expNum = parseInt(exponent, 10);
            const sign = expNum >= 0 ? '+' : '-';
            return `${toGermanNumber(mTrim)}E${sign}${Math.abs(expNum)}`;
        }
        const text = (Math.round(value * 1e9) / 1e9).toString();
        const trimmed = text.replace(/\.0+$/, '').replace(/(\.\d*?)0+$/, '$1');
        return toGermanNumber(trimmed);
    }

    return {
        normalizeNumberString,
        toGermanNumber,
        splitTopLevelSemicolon,
        normalizeExpression,
        prepareGraphExpression,
        evaluateExpression,
        evaluateWithAssignments,
        formatGeneralResult,
        factorial,
        binomialCoefficient,
        computeBinomProbability,
        logBase,
        addImplicitMultiplication,
        normalizeUnaryMinusExponent,
        normalizeConstants,
        convertCustomENotation,
        convertLogBaseSyntax,
        convertLogBaseSyntaxForMathJS,
        convertWurzelSyntax,
        convertWurzelSyntaxForMathJS,
        convertNCrSyntax,
        convertFactorialSyntax,
        convertBinomSyntaxForMathJS,
    };
})();
