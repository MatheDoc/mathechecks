const DevCalculatorCommands = (() => {
    const LGS_VARIABLE_NAMES = ['a', 'b', 'c', 'd', 'e', 'f'];

    function getLGSVariableName(index) {
        return LGS_VARIABLE_NAMES[index] || `x${index + 1}`;
    }

    function parsePValue(pString) {
        const normalized = DevCalculatorUtils.normalizeNumberString(String(pString ?? ''));
        if (normalized.includes('/')) {
            const parts = normalized.split('/').map((part) => parseFloat(part.trim()));
            if (parts.length === 2 && parts.every((part) => !Number.isNaN(part)) && parts[1] !== 0) {
                return parts[0] / parts[1];
            }
        }
        return parseFloat(normalized);
    }

    function buildBinomCommand(fields) {
        return `binom(${fields.a || '0'};${fields.b || '0'};${fields.n || '0'};${fields.p || '0'})`;
    }

    function getLiveBinomResult(fields) {
        const a = Math.ceil(parseFloat(DevCalculatorUtils.normalizeNumberString(fields.a || '0')));
        const b = Math.floor(parseFloat(DevCalculatorUtils.normalizeNumberString(fields.b || '0')));
        const n = parseInt(DevCalculatorUtils.normalizeNumberString(fields.n || '0'), 10);
        const p = parsePValue(fields.p || '0');
        const probability = DevCalculatorUtils.computeBinomProbability(a, b, n, p);
        if (!Number.isFinite(probability)) return '-';
        return DevCalculatorUtils.formatGeneralResult(probability);
    }

    function getLGSPanelExpression(rawValue, fallback = '0') {
        const text = String(rawValue ?? '').trim();
        return text || fallback;
    }

    function tryEvaluateLGSPanelExpression(rawValue) {
        const value = DevCalculatorUtils.evaluateWithAssignments(getLGSPanelExpression(rawValue), [], {});
        return Number.isFinite(value) ? value : null;
    }

    function buildLGSCommand({ variables, equations, values }) {
        const rows = [];
        for (let equationIndex = 0; equationIndex < equations; equationIndex++) {
            const terms = [];
            for (let variableIndex = 0; variableIndex < variables; variableIndex++) {
                const coeffExpression = getLGSPanelExpression(values[`a${equationIndex}${variableIndex}`]);
                const coeffValue = tryEvaluateLGSPanelExpression(coeffExpression);
                const variableName = getLGSVariableName(variableIndex);
                if (coeffValue !== 0) {
                    terms.push(`(${coeffExpression})${variableName}`);
                }
            }
            const resultText = getLGSPanelExpression(values[`b${equationIndex}`]);
            rows.push(`${terms.length > 0 ? terms.join('+') : '0'}=${resultText}`);
        }
        return `lgs(${rows.join(';')})`;
    }

    function parseCommandOptions(parts) {
        const options = {};
        parts.forEach((part) => {
            const [key, value] = part.split('=').map((entry) => entry.trim());
            if (key && value) options[key.toLowerCase()] = value;
        });
        return options;
    }

    function getStandaloneCallInner(input, commandName) {
        const text = String(input ?? '').trim();
        const startMatch = text.match(new RegExp(`^${commandName}\\s*\\(`, 'i'));
        if (!startMatch) return null;

        const openParenIndex = startMatch[0].length - 1;
        let depth = 0;

        for (let index = openParenIndex; index < text.length; index++) {
            const ch = text[index];
            if (ch === '(') depth++;
            else if (ch === ')') depth--;

            if (depth === 0) {
                if (index !== text.length - 1) return null;
                return text.slice(openParenIndex + 1, index);
            }
        }

        return null;
    }

    function startsWithNamedCall(input, commandName) {
        return new RegExp(`^${commandName}\\s*\\(`, 'i').test(String(input ?? '').trim());
    }

    function replaceStandaloneX(expression, xValue) {
        return String(expression || '').replace(
            /(^|[^a-zA-Z0-9_.])x([^a-zA-Z0-9_]|$)/g,
            `$1(${xValue})$2`
        );
    }

    function evaluateExpressionWithX(rawExpression, xValue) {
        const normalized = DevCalculatorUtils.normalizeExpression(
            normalizeDecimalCommas(`(${String(rawExpression || '')})`)
        ).replace(/(?<!Math\.)\blog\s*\(/g, 'Math.log10(');
        const expression = replaceStandaloneX(normalized, xValue);
        return eval(expression);
    }

    function formatSubscriptNumber(value) {
        return String(value ?? '').replace(/\d/g, (digit) => '₀₁₂₃₄₅₆₇₈₉'[Number(digit)]);
    }

    function formatIndexedVariable(name, index) {
        return `${String(name ?? '')}${formatSubscriptNumber(index)}`;
    }

    function normalizeDecimalCommas(expression) {
        return String(expression || '').replace(/(\d)\s*,\s*(\d)/g, '$1.$2');
    }

    function refineBracketedRoot(evaluateFn, a, b, tolerance, maxIterations = 100) {
        let fa = evaluateFn(a);
        let fb = evaluateFn(b);
        if (Number.isNaN(fa) || Number.isNaN(fb)) return null;
        if (Math.abs(fa) < tolerance) return a;
        if (Math.abs(fb) < tolerance) return b;
        if (fa * fb > 0) return null;

        let left = a;
        let right = b;
        for (let iteration = 0; iteration < maxIterations; iteration++) {
            const mid = (left + right) / 2;
            const fm = evaluateFn(mid);
            if (Number.isNaN(fm)) return null;
            if (Math.abs(fm) < tolerance) return mid;
            if (fa * fm <= 0) {
                right = mid;
                fb = fm;
            } else {
                left = mid;
                fa = fm;
            }
        }

        const root = (left + right) / 2;
        const fRoot = evaluateFn(root);
        return !Number.isNaN(fRoot) && Math.abs(fRoot) < tolerance ? root : null;
    }

    function refineTouchingRoot(evaluateFn, a, b, tolerance, maxIterations = 60) {
        let left = a;
        let right = b;
        let bestX = null;
        let bestAbsValue = Number.POSITIVE_INFINITY;

        for (let iteration = 0; iteration < maxIterations; iteration++) {
            const third = (right - left) / 3;
            const mid1 = left + third;
            const mid2 = right - third;
            const f1 = evaluateFn(mid1);
            const f2 = evaluateFn(mid2);
            if (Number.isNaN(f1) || Number.isNaN(f2)) return null;

            const abs1 = Math.abs(f1);
            const abs2 = Math.abs(f2);
            if (abs1 < bestAbsValue) {
                bestAbsValue = abs1;
                bestX = mid1;
            }
            if (abs2 < bestAbsValue) {
                bestAbsValue = abs2;
                bestX = mid2;
            }

            if (abs1 <= abs2) {
                right = mid2;
            } else {
                left = mid1;
            }
        }

        if (bestX === null) return null;
        const bestValue = evaluateFn(bestX);
        return !Number.isNaN(bestValue) && Math.abs(bestValue) < tolerance ? bestX : null;
    }

    function findRootInInterval(evaluateFn, a, b, fA, fB, tolerance, touchCandidateTolerance = 1e-2) {
        if (Number.isNaN(fA) || Number.isNaN(fB)) return null;

        const absFA = Math.abs(fA);
        const absFB = Math.abs(fB);
        const endpointCandidate = absFA <= absFB ? a : b;
        const endpointAbsValue = Math.min(absFA, absFB);

        if (fA * fB < 0) {
            return refineBracketedRoot(evaluateFn, a, b, tolerance) ?? (endpointAbsValue < tolerance ? endpointCandidate : null);
        }

        const mid = (a + b) / 2;
        const fMid = evaluateFn(mid);
        if (Number.isNaN(fMid)) return null;
        const absFMid = Math.abs(fMid);

        if (Math.min(endpointAbsValue, absFMid) > touchCandidateTolerance) {
            return null;
        }

        return refineTouchingRoot(evaluateFn, a, b, tolerance)
            ?? (absFMid < tolerance ? mid : null)
            ?? (endpointAbsValue < tolerance ? endpointCandidate : null);
    }

    function deduplicateNumericRoots(values, evaluateFn, roundFactor, proximityTolerance) {
        const sorted = values
            .map((value) => ({
                roundedValue: Math.round(value * roundFactor) / roundFactor,
                residual: Math.abs(evaluateFn(value)),
            }))
            .sort((left, right) => left.roundedValue - right.roundedValue);

        const deduplicated = [];
        sorted.forEach((candidate) => {
            const last = deduplicated[deduplicated.length - 1];
            if (last && Math.abs(candidate.roundedValue - last.roundedValue) <= proximityTolerance) {
                if (candidate.residual < last.residual) {
                    deduplicated[deduplicated.length - 1] = candidate;
                }
                return;
            }
            deduplicated.push(candidate);
        });

        return deduplicated.map((entry) => entry.roundedValue);
    }

    function evaluateScalarExpression(expr, varNames) {
        const value = DevCalculatorUtils.evaluateWithAssignments(expr, varNames, {});
        return Number.isFinite(value) ? value : 0;
    }

    function evaluateCoefficient(expr, varNames, targetVar) {
        const withOne = DevCalculatorUtils.evaluateWithAssignments(expr, varNames, { [targetVar]: 1 });
        const baseline = evaluateScalarExpression(expr, varNames);
        const coeff = (withOne ?? 0) - (baseline ?? 0);
        return Number.isFinite(coeff) ? coeff : 0;
    }

    function isLinearExpression(expr, varNames) {
        try {
            const eps = 1e-9;
            const baseline = DevCalculatorUtils.evaluateWithAssignments(expr, varNames, {});
            const coeffs = new Map();
            for (let i = 0; i < varNames.length; i++) {
                const variableName = varNames[i];
                const val1 = DevCalculatorUtils.evaluateWithAssignments(expr, varNames, { [variableName]: 1 });
                const val2 = DevCalculatorUtils.evaluateWithAssignments(expr, varNames, { [variableName]: 2 });
                const coeff = val1 - baseline;
                coeffs.set(variableName, coeff);
                if (!Number.isFinite(val1) || !Number.isFinite(val2) || Math.abs((baseline + 2 * coeff) - val2) > eps) {
                    return false;
                }
            }
            for (let i = 0; i < varNames.length; i++) {
                for (let j = i + 1; j < varNames.length; j++) {
                    const vi = varNames[i];
                    const vj = varNames[j];
                    const both = DevCalculatorUtils.evaluateWithAssignments(expr, varNames, { [vi]: 1, [vj]: 1 });
                    const expected = baseline + (coeffs.get(vi) || 0) + (coeffs.get(vj) || 0);
                    if (!Number.isFinite(both) || Math.abs(both - expected) > eps) {
                        return false;
                    }
                }
            }
            return true;
        } catch {
            return false;
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
            if (!pivotCols.includes(j)) freeCols.push(j);
        }

        const paramMap = new Map();
        freeCols.forEach((col, idx) => {
            paramMap.set(col, `t${idx + 1}`);
        });

        const expressions = new Array(cols).fill('0');
        freeCols.forEach((col) => {
            expressions[col] = paramMap.get(col);
        });

        for (let i = 0; i < pivotCols.length; i++) {
            const col = pivotCols[i];
            let expr = DevCalculatorUtils.formatGeneralResult(augmented[i][cols]);
            freeCols.forEach((freeCol) => {
                const coeff = -augmented[i][freeCol];
                if (Math.abs(coeff) < eps) return;
                const sign = coeff >= 0 ? ' + ' : ' - ';
                const absCoeff = Math.abs(coeff);
                const coeffText = absCoeff === 1 ? '' : DevCalculatorUtils.formatGeneralResult(absCoeff);
                expr += `${sign}${coeffText}${paramMap.get(freeCol)}`;
            });
            expressions[col] = expr;
        }

        return { status: 'infinite', parametric: expressions.map((expr, idx) => `${LGS_VARIABLE_NAMES[idx] || `x${idx + 1}`}=${expr}`) };
    }

    function executeLGSCommand(input, outputApi) {
        try {
            const match = input.match(/^lgs\s*\((.*)\)\s*$/i);
            if (!match) throw new Error('invalid');
            const equations = match[1].split(';').map((part) => part.trim()).filter(Boolean);
            const varSet = new Set();
            equations.forEach((equation) => {
                const [leftRaw, rightRaw] = equation.split('=');
                [leftRaw || '', rightRaw || ''].forEach((text) => {
                    (text.match(/[a-z]/gi) || []).forEach((variableName) => varSet.add(variableName.toLowerCase()));
                });
            });
            const varNames = Array.from(varSet).sort();
            const varIndex = new Map(varNames.map((variableName, index) => [variableName, index]));
            const A = [];
            const b = [];

            equations.forEach((equation) => {
                const [leftRaw, rightRaw] = equation.split('=');
                const left = (leftRaw || '').trim();
                const right = (rightRaw || '').trim();
                if (!isLinearExpression(left, varNames) || !isLinearExpression(right, varNames)) {
                    throw new Error('nonlinear');
                }
                const row = new Array(varNames.length).fill(0);
                varNames.forEach((variableName) => {
                    const idx = varIndex.get(variableName);
                    row[idx] = evaluateCoefficient(left, varNames, variableName) - evaluateCoefficient(right, varNames, variableName);
                });
                const leftConst = evaluateScalarExpression(left, varNames);
                const rightConst = evaluateScalarExpression(right, varNames);
                A.push(row);
                b.push(rightConst - leftConst);
            });

            const solution = solveLinearSystem(A, b);
            if (solution.status === 'inconsistent') {
                outputApi.setText('Keine Lösung', { headline: 'LGS' });
                return;
            }
            if (solution.status === 'infinite') {
                outputApi.setText(solution.parametric.join(', '), { headline: 'LGS' });
                return;
            }
            outputApi.setText(
                solution.values.map((value, index) => `${varNames[index] || `x${index + 1}`}=${DevCalculatorUtils.formatGeneralResult(value)}`).join(', '),
                { headline: 'LGS' }
            );
        } catch (error) {
            outputApi.setText(
                error.message === 'nonlinear' ? 'Fehler: Nicht linear (x^2, xy, ...)' : 'Fehler im LGS',
                { headline: 'LGS' }
            );
        }
    }

    function solveEquationCommand(equation, outputApi) {
        try {
            let [leftSide, rightSide] = equation.split('=').map((part) => part.trim());
            if (!rightSide) rightSide = '0';

            function f(x) {
                return evaluateExpressionWithX(`(${leftSide}) - (${rightSide})`, x);
            }

            const tolerance = 1e-6;
            const rangeMin = -1000;
            const rangeMax = 1000;
            const steps = 20000;
            const step = (rangeMax - rangeMin) / steps;
            const roots = [];
            const identitySamplePoints = [rangeMin, -10, -1, 0, 1, 10, rangeMax];
            const isIdentityEquation = identitySamplePoints.every((sampleX) => {
                const value = f(sampleX);
                return Number.isFinite(value) && Math.abs(value) < tolerance;
            });

            if (isIdentityEquation) {
                outputApi.setText('Unendlich viele Lösungen', { headline: 'Gleichung' });
                return;
            }

            for (let i = 0; i < steps; i++) {
                const x1 = rangeMin + i * step;
                const x2 = x1 + step;
                const f1 = f(x1);
                const f2 = f(x2);
                const root = findRootInInterval(f, x1, x2, f1, f2, tolerance);
                if (root !== null) roots.push(root);
            }

            const uniqueRoots = deduplicateNumericRoots(roots, f, 1e6, Math.max(1e-5, step / 20));

            if (!uniqueRoots.length) {
                outputApi.setText('Keine Lösung', { headline: 'Gleichung' });
                return;
            }

            outputApi.setText(
                uniqueRoots
                    .map((root, index) => `${formatIndexedVariable('x', index + 1)}=${DevCalculatorUtils.formatGeneralResult(root)}`)
                    .join(', '),
                { headline: 'Gleichung' }
            );
        } catch {
            outputApi.setText('Fehler beim Lösen', { headline: 'Gleichung' });
        }
    }

    function containsVariableX(input) {
        const cleaned = input.replace(/\bexp\b/gi, '___');
        return /(?:^|[^a-zA-Z])x(?:[^a-zA-Z]|$)/i.test(cleaned);
    }

    function expandExpression(input, outputApi) {
        try {
            const expr = DevCalculatorUtils.prepareGraphExpression(input);
            if (!expr || typeof math === 'undefined') {
                outputApi.setText('Fehler: Ausdruck konnte nicht vereinfacht werden', { headline: 'Fehler' });
                return;
            }
            const expanded = math.rationalize(expr);
            let output = expanded.toString({ implicit: 'hide', parenthesis: 'auto' });
            output = output.replace(/ /g, '').replace(/(\d)\*([a-zA-Z])/g, '$1$2');
            outputApi.setText(output, { headline: 'Term' });
        } catch {
            outputApi.setText('Fehler: Ausdruck konnte nicht vereinfacht werden', { headline: 'Fehler' });
        }
    }

    function buildGraphCommand(fields) {
        const parts = [fields.function || 'x'];
        ['xmin', 'xmax', 'ymin', 'ymax'].forEach((key) => {
            const value = String(fields[key] ?? '').trim();
            if (value) parts.push(`${key}=${value}`);
        });
        return `graph(${parts.join(';')})`;
    }

    function buildUnaryFunctionExpression(name, value) {
        return `${String(name ?? '').trim()}(${String(value ?? '').trim()})`;
    }

    function buildExpExpression(value) {
        return `e^(${String(value ?? '').trim()})`;
    }

    function buildLogExpression(fields) {
        return `log(${String(fields.base ?? '').trim()};${String(fields.value ?? '').trim()})`;
    }

    function buildFractionExpression(fields) {
        return `(${String(fields.numerator ?? '').trim()})/(${String(fields.denominator ?? '').trim()})`;
    }

    function buildPowerExpression(fields) {
        return `(${String(fields.base ?? '').trim()})^(${String(fields.exponent ?? '').trim()})`;
    }

    function buildIntegralExpression(fields) {
        return `int(${String(fields.integrand ?? '').trim()};${String(fields.lowerBound ?? '').trim()};${String(fields.upperBound ?? '').trim()})`;
    }

    function buildFactorialExpression(value) {
        return `(${String(value ?? '').trim()})!`;
    }

    function buildBinomialCoefficientExpression(fields) {
        return `nCr(${String(fields.n ?? '').trim()};${String(fields.k ?? '').trim()})`;
    }

    const GRAPH_ANALYSIS_CONFIG = Object.freeze({
        zerosTolerance: 1e-9,
        zerosMinSteps: 120,
        zerosMaxSteps: 600,
        zerosStepsPerUnit: 40,
        zerosRoundFactor: 1e4,
        zerosDeduplicateTolerance: 1e-4,
        gridMinSteps: 100,
        gridMaxSteps: 600,
        gridStepsPerUnit: 40,
        cleanValueEpsilon: 1e-9,
        defaultSignTolerance: 1e-8,
        defaultRefineIterations: 12,
        extremaSignTolerance: 1e-7,
        extremaRefineIterations: 14,
        inflectionSignTolerance: 1e-8,
        inflectionRefineIterations: 14,
        deduplicateXFactor: 2,
        pointValueDecimals: 4,
    });

    function evaluateGraphFunctionJS(rawExpr, x) {
        try {
            return evaluateExpressionWithX(rawExpr, x);
        } catch {
            return NaN;
        }
    }

    function buildGraphFunctionEvaluator(rawExpr) {
        const prepared = DevCalculatorUtils.prepareGraphExpression(rawExpr);
        const cache = new Map();
        let compiledExpression = null;

        if (typeof window.math !== 'undefined' && prepared) {
            try {
                compiledExpression = window.math.parse(prepared).compile();
            } catch {
                compiledExpression = null;
            }
        }

        return function evaluateGraphAt(x) {
            if (cache.has(x)) return cache.get(x);
            const cleanX = Math.abs(x) < GRAPH_ANALYSIS_CONFIG.cleanValueEpsilon ? 0 : x;
            let value = NaN;

            if (compiledExpression) {
                try {
                    const evaluated = compiledExpression.evaluate({ x: cleanX });
                    value = typeof evaluated === 'number' && Number.isFinite(evaluated) ? evaluated : NaN;
                } catch {
                    value = NaN;
                }
            }

            if (!Number.isFinite(value)) {
                value = evaluateGraphFunctionJS(rawExpr, cleanX);
            }

            cache.set(x, value);
            return value;
        };
    }

    function buildGraphDerivativeEvaluators(rawExpr) {
        if (typeof window.math === 'undefined') return null;

        const prepared = DevCalculatorUtils.prepareGraphExpression(rawExpr);
        if (!prepared) return null;

        function buildCompiledEvaluator(compiledExpression) {
            return function evaluateCompiledAt(x) {
                try {
                    const cleanX = Math.abs(x) < GRAPH_ANALYSIS_CONFIG.cleanValueEpsilon ? 0 : x;
                    const value = compiledExpression.evaluate({ x: cleanX });
                    return typeof value === 'number' && Number.isFinite(value) ? value : NaN;
                } catch {
                    return NaN;
                }
            };
        }

        try {
            const expressionNode = window.math.parse(prepared);
            const firstDerivativeNode = window.math.derivative(expressionNode, 'x');
            const secondDerivativeNode = window.math.derivative(firstDerivativeNode, 'x');

            return {
                firstDerivativeEvaluator: buildCompiledEvaluator(firstDerivativeNode.compile()),
                secondDerivativeEvaluator: buildCompiledEvaluator(secondDerivativeNode.compile()),
            };
        } catch {
            return null;
        }
    }

    function getGraphRootSearchConfig(xMin, xMax) {
        const range = xMax - xMin;
        if (!Number.isFinite(range) || range <= 0) return null;

        const steps = Math.min(
            GRAPH_ANALYSIS_CONFIG.zerosMaxSteps,
            Math.max(GRAPH_ANALYSIS_CONFIG.zerosMinSteps, Math.floor(range * GRAPH_ANALYSIS_CONFIG.zerosStepsPerUnit))
        );
        const step = range / steps;

        return { steps, step };
    }

    function collectGraphSampleZeroRoots(evaluateFn, xMin, xMax, steps, step, tolerance) {
        const roots = [];

        for (let i = 0; i <= steps; i++) {
            const x = i === steps ? xMax : xMin + i * step;
            const value = evaluateFn(x);
            if (Number.isFinite(value) && Math.abs(value) <= tolerance) roots.push(x);
        }

        return roots;
    }

    function refineGraphDomainBoundaryRoot(evaluateFn, invalidX, validX, tolerance, maxIterations = 60) {
        let invalid = invalidX;
        let valid = validX;
        let validValue = evaluateFn(valid);
        if (!Number.isFinite(validValue)) return null;

        for (let i = 0; i < maxIterations; i++) {
            const mid = (invalid + valid) / 2;
            if (mid === invalid || mid === valid) break;

            const midValue = evaluateFn(mid);
            if (Number.isFinite(midValue)) {
                valid = mid;
                validValue = midValue;
            } else {
                invalid = mid;
            }
        }

        return Math.abs(validValue) <= tolerance ? valid : null;
    }

    function collectGraphDomainBoundaryRoots(evaluateFn, xMin, xMax, steps, step) {
        const roots = [];
        const boundaryTolerance = Math.max(
            GRAPH_ANALYSIS_CONFIG.zerosTolerance,
            4 * Math.sqrt(Number.EPSILON)
        );

        for (let i = 0; i < steps; i++) {
            const x1 = xMin + i * step;
            const x2 = i === steps - 1 ? xMax : x1 + step;
            const v1 = evaluateFn(x1);
            const v2 = evaluateFn(x2);
            const finite1 = Number.isFinite(v1);
            const finite2 = Number.isFinite(v2);
            if (finite1 === finite2) continue;

            const candidate = finite1
                ? refineGraphDomainBoundaryRoot(evaluateFn, x2, x1, boundaryTolerance)
                : refineGraphDomainBoundaryRoot(evaluateFn, x1, x2, boundaryTolerance);
            if (candidate !== null) roots.push(candidate);
        }

        return roots;
    }

    function collectGraphSpecialPointRoots(points, evaluateFn, tolerance) {
        return (points || [])
            .filter((point) => Number.isFinite(point?.x))
            .filter((point) => {
                const residual = evaluateFn(point.x);
                return Number.isFinite(residual) && Math.abs(residual) <= tolerance;
            })
            .map((point) => point.x);
    }

    function findGraphRoots(evaluateFn, specialPoints, xMin, xMax) {
        const tolerance = GRAPH_ANALYSIS_CONFIG.zerosTolerance;
        const search = getGraphRootSearchConfig(xMin, xMax);
        if (!search) return [];

        const { steps, step } = search;
        const signChangeRoots = findSignChangeRoots(evaluateFn, xMin, xMax, step, {
            signTolerance: tolerance,
            refineIterations: GRAPH_ANALYSIS_CONFIG.defaultRefineIterations,
        });
        const sampleRoots = collectGraphSampleZeroRoots(evaluateFn, xMin, xMax, steps, step, tolerance);
        const boundaryRoots = collectGraphDomainBoundaryRoots(evaluateFn, xMin, xMax, steps, step);
        const specialRoots = collectGraphSpecialPointRoots(specialPoints, evaluateFn, tolerance);

        const roots = [...signChangeRoots, ...sampleRoots, ...boundaryRoots, ...specialRoots];

        return deduplicateNumericRoots(
            roots,
            evaluateFn,
            GRAPH_ANALYSIS_CONFIG.zerosRoundFactor,
            Math.max(GRAPH_ANALYSIS_CONFIG.zerosDeduplicateTolerance, step / 20)
        );
    }

    function getGraphAnalysisGrid(xMin, xMax) {
        const range = xMax - xMin;
        if (!Number.isFinite(range) || range <= 0) return null;
        const steps = Math.min(
            GRAPH_ANALYSIS_CONFIG.gridMaxSteps,
            Math.max(GRAPH_ANALYSIS_CONFIG.gridMinSteps, Math.floor(range * GRAPH_ANALYSIS_CONFIG.gridStepsPerUnit))
        );
        return { h: range / steps };
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
            const fa = sampleFn(left);
            const fb = sampleFn(right);
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
                    signB = signM;
                } else {
                    left = mid;
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
            if (!unique.some((existing) => Math.abs(existing.x - point.x) < tolerance)) {
                unique.push(point);
            }
        }
        return unique;
    }

    function cleanGraphPointValue(value) {
        return Math.abs(value) < GRAPH_ANALYSIS_CONFIG.cleanValueEpsilon ? 0 : value;
    }

    function findGraphCriticalPoints(valueFn, xMin, xMax, options) {
        const grid = getGraphAnalysisGrid(xMin, xMax);
        if (!grid) return [];

        const { h } = grid;
        const derivativeFn = options.buildDerivativeFn(h);
        if (typeof derivativeFn !== 'function') return [];

        const roots = findSignChangeRoots(derivativeFn, xMin, xMax, h, {
            signTolerance: options.signTolerance,
            refineIterations: options.refineIterations,
        });
        const points = [];

        for (const xr of roots) {
            const leftValue = derivativeFn(xr - h);
            const rightValue = derivativeFn(xr + h);
            if (!Number.isFinite(leftValue) || !Number.isFinite(rightValue)) continue;

            const leftSign = signWithTolerance(leftValue, options.signTolerance);
            const rightSign = signWithTolerance(rightValue, options.signTolerance);
            if (leftSign === 0 || rightSign === 0 || leftSign === rightSign) continue;

            const y = valueFn(xr);
            if (!Number.isFinite(y)) continue;

            points.push(options.createPoint({
                x: cleanGraphPointValue(xr),
                y: cleanGraphPointValue(y),
                leftSign,
                rightSign,
            }));
        }

        return deduplicatePointsByX(points, h * GRAPH_ANALYSIS_CONFIG.deduplicateXFactor)
            .sort((left, right) => left.x - right.x);
    }

    function mergeGraphPointResults(primaryPoints, secondaryPoints, xMin, xMax) {
        const grid = getGraphAnalysisGrid(xMin, xMax);
        const tolerance = grid
            ? grid.h * GRAPH_ANALYSIS_CONFIG.deduplicateXFactor
            : GRAPH_ANALYSIS_CONFIG.zerosDeduplicateTolerance;

        return deduplicatePointsByX([...(primaryPoints || []), ...(secondaryPoints || [])], tolerance)
            .sort((left, right) => left.x - right.x);
    }

    function findGraphExtremaNumerical(valueFn, xMin, xMax) {
        return findGraphCriticalPoints(valueFn, xMin, xMax, {
            buildDerivativeFn(h) {
                return function firstDiff(x) {
                    return (valueFn(x + h) - valueFn(x - h)) / (2 * h);
                };
            },
            signTolerance: GRAPH_ANALYSIS_CONFIG.extremaSignTolerance,
            refineIterations: GRAPH_ANALYSIS_CONFIG.extremaRefineIterations,
            createPoint({ x, y, leftSign, rightSign }) {
                return {
                    x,
                    y,
                    type: leftSign > rightSign ? 'Max' : 'Min',
                };
            },
        });
    }

    function findGraphInflectionPointsNumerical(valueFn, xMin, xMax) {
        return findGraphCriticalPoints(valueFn, xMin, xMax, {
            buildDerivativeFn(h) {
                return function secondDiff(x) {
                    return (valueFn(x + h) - 2 * valueFn(x) + valueFn(x - h)) / (h * h);
                };
            },
            signTolerance: GRAPH_ANALYSIS_CONFIG.inflectionSignTolerance,
            refineIterations: GRAPH_ANALYSIS_CONFIG.inflectionRefineIterations,
            createPoint({ x, y }) {
                return { x, y };
            },
        });
    }

    function findGraphExtrema(valueFn, firstDerivativeEvaluator, xMin, xMax) {
        const symbolicExtrema = firstDerivativeEvaluator
            ? findGraphCriticalPoints(valueFn, xMin, xMax, {
                buildDerivativeFn() {
                    return firstDerivativeEvaluator;
                },
                signTolerance: GRAPH_ANALYSIS_CONFIG.extremaSignTolerance,
                refineIterations: GRAPH_ANALYSIS_CONFIG.extremaRefineIterations,
                createPoint({ x, y, leftSign, rightSign }) {
                    return {
                        x,
                        y,
                        type: leftSign > rightSign ? 'Max' : 'Min',
                    };
                },
            })
            : [];
        const numericalExtrema = findGraphExtremaNumerical(valueFn, xMin, xMax);

        return mergeGraphPointResults(symbolicExtrema, numericalExtrema, xMin, xMax);
    }

    function findGraphInflectionPoints(valueFn, secondDerivativeEvaluator, xMin, xMax) {
        const symbolicPoints = secondDerivativeEvaluator
            ? findGraphCriticalPoints(valueFn, xMin, xMax, {
                buildDerivativeFn() {
                    return secondDerivativeEvaluator;
                },
                signTolerance: GRAPH_ANALYSIS_CONFIG.inflectionSignTolerance,
                refineIterations: GRAPH_ANALYSIS_CONFIG.inflectionRefineIterations,
                createPoint({ x, y }) {
                    return { x, y };
                },
            })
            : [];
        const numericalPoints = findGraphInflectionPointsNumerical(valueFn, xMin, xMax);

        return mergeGraphPointResults(symbolicPoints, numericalPoints, xMin, xMax);
    }

    function analyzeGraph(rawExpr, xMin, xMax) {
        const valueFn = buildGraphFunctionEvaluator(rawExpr);
        const derivativeEvaluators = buildGraphDerivativeEvaluators(rawExpr);
        const extrema = findGraphExtrema(valueFn, derivativeEvaluators?.firstDerivativeEvaluator, xMin, xMax);
        const inflectionPoints = findGraphInflectionPoints(valueFn, derivativeEvaluators?.secondDerivativeEvaluator, xMin, xMax);

        return {
            roots: findGraphRoots(valueFn, [...extrema, ...inflectionPoints], xMin, xMax),
            extrema,
            inflectionPoints,
        };
    }

    function formatPointValue(value) {
        if (!Number.isFinite(value)) return 'n.def.';
        if (Math.abs(value) < 1e-9) return '0';
        const absValue = Math.abs(value);
        if (absValue < 0.001 || absValue > 99999) {
            return value.toExponential(2).replace('.', ',');
        }
        return value.toFixed(GRAPH_ANALYSIS_CONFIG.pointValueDecimals).replace(/\.?0+$/, '').replace('.', ',');
    }

    function formatGraphAnalysisHtml(analysis) {
        const sections = [];

        if (analysis.roots.length) {
            sections.push(
                `<div class="point-category"><strong>Nullstellen:</strong></div>${analysis.roots
                    .map((value) => `<div class="point-item">x = ${formatPointValue(value)}</div>`)
                    .join('')}`
            );
        }

        if (analysis.extrema.length) {
            sections.push(
                `<div class="point-category"><strong>Extrempunkte:</strong></div>${analysis.extrema
                    .map((point) => `<div class="point-item">${point.type}(${formatPointValue(point.x)} | ${formatPointValue(point.y)})</div>`)
                    .join('')}`
            );
        }

        if (analysis.inflectionPoints.length) {
            sections.push(
                `<div class="point-category"><strong>Wendepunkte:</strong></div>${analysis.inflectionPoints
                    .map((point) => `<div class="point-item">W(${formatPointValue(point.x)} | ${formatPointValue(point.y)})</div>`)
                    .join('')}`
            );
        }

        if (!sections.length) {
            return '<div class="point-item">Keine besonderen Punkte im Bereich gefunden</div>';
        }

        return `<div class="graph-points-list">${sections.join('')}</div>`;
    }

    // --- Matrizenrechnung ---

    class MatrixError extends Error {
        constructor(message) {
            super(message);
            this.name = 'MatrixError';
        }
    }

    function splitTopLevelByChar(str, sep) {
        const parts = [];
        let depth = 0;
        let current = '';
        for (const ch of str) {
            if (ch === '(' || ch === '[' || ch === '{') depth++;
            else if (ch === ')' || ch === ']' || ch === '}') depth--;
            else if (ch === sep && depth === 0) {
                parts.push(current);
                current = '';
                continue;
            }
            current += ch;
        }
        parts.push(current);
        return parts;
    }

    function parseMatLiteral(str) {
        const s = String(str ?? '').trim();
        const parenStart = s.search(/\s*\(/);
        if (parenStart < 0 || s[s.length - 1] !== ')') throw new MatrixError('Kein gültiges mat()-Literal');
        const inner = s.slice(parenStart + 1, s.length - 1).trim();
        const rowStrs = splitTopLevelByChar(inner, ';');
        const rows = rowStrs.map((rowStr) => {
            const r = rowStr.trim();
            if (!r.startsWith('[') || !r.endsWith(']')) {
                throw new MatrixError(`Ungültige Zeile: ${r}`);
            }
            const entriesRaw = splitTopLevelByChar(r.slice(1, -1), ';');
            return entriesRaw.map((e) => {
                const val = DevCalculatorUtils.evaluateExpression(e.trim());
                if (!Number.isFinite(val)) throw new MatrixError(`Ungültiger Eintrag: ${e.trim()}`);
                return val;
            });
        });
        if (!rows.length || !rows[0].length) throw new MatrixError('Leere Matrix');
        const cols = rows[0].length;
        if (!rows.every((row) => row.length === cols)) throw new MatrixError('Matrix nicht rechteckig');
        return rows;
    }

    function matDims(A) {
        return `${A.length}×${A[0]?.length ?? 0}`;
    }

    function matAdd(A, B) {
        if (A.length !== B.length || (A[0]?.length ?? 0) !== (B[0]?.length ?? 0)) {
            throw new MatrixError(`Addition: Dimensionen passen nicht (${matDims(A)} + ${matDims(B)})`);
        }
        return A.map((row, i) => row.map((v, j) => v + B[i][j]));
    }

    function matSub(A, B) {
        if (A.length !== B.length || (A[0]?.length ?? 0) !== (B[0]?.length ?? 0)) {
            throw new MatrixError(`Subtraktion: Dimensionen passen nicht (${matDims(A)} − ${matDims(B)})`);
        }
        return A.map((row, i) => row.map((v, j) => v - B[i][j]));
    }

    function matMul(A, B) {
        const m = A.length;
        const n = A[0]?.length ?? 0;
        const p = B[0]?.length ?? 0;
        if (n !== B.length) {
            throw new MatrixError(`Multiplikation: Dimensionen passen nicht (${matDims(A)} · ${matDims(B)})`);
        }
        return Array.from({ length: m }, (_, i) =>
            Array.from({ length: p }, (_, j) =>
                A[i].reduce((sum, v, k) => sum + v * B[k][j], 0)
            )
        );
    }

    function matScale(scalar, A) {
        return A.map((row) => row.map((v) => scalar * v));
    }

    function matInverse(A) {
        const n = A.length;
        if (n !== (A[0]?.length ?? 0)) {
            throw new MatrixError('Inverse: Nur für quadratische Matrizen');
        }
        const eps = 1e-12;
        const aug = A.map((row, i) => {
            const eye = new Array(n).fill(0);
            eye[i] = 1;
            return [...row, ...eye];
        });
        for (let col = 0; col < n; col++) {
            let pivRow = col;
            for (let row = col + 1; row < n; row++) {
                if (Math.abs(aug[row][col]) > Math.abs(aug[pivRow][col])) pivRow = row;
            }
            [aug[col], aug[pivRow]] = [aug[pivRow], aug[col]];
            const piv = aug[col][col];
            if (Math.abs(piv) < eps) throw new MatrixError('Matrix nicht invertierbar');
            for (let j = 0; j < 2 * n; j++) aug[col][j] /= piv;
            for (let row = 0; row < n; row++) {
                if (row === col) continue;
                const factor = aug[row][col];
                if (Math.abs(factor) < eps) continue;
                for (let j = 0; j < 2 * n; j++) aug[row][j] -= factor * aug[col][j];
            }
        }
        return aug.map((row) => row.slice(n));
    }

    function matIdentity(size) {
        return Array.from({ length: size }, (_, rowIndex) =>
            Array.from({ length: size }, (_, colIndex) => (rowIndex === colIndex ? 1 : 0))
        );
    }

    function matPow(A, exponent) {
        const size = A.length;
        if (size !== (A[0]?.length ?? 0)) {
            throw new MatrixError('Potenz: Nur für quadratische Matrizen');
        }
        if (!Number.isInteger(exponent)) {
            throw new MatrixError('Potenz: Exponent muss ganzzahlig sein');
        }
        if (exponent === 0) return matIdentity(size);

        let base = exponent < 0 ? matInverse(A) : A;
        let remaining = Math.abs(exponent);
        let result = matIdentity(size);

        while (remaining > 0) {
            if (remaining % 2 === 1) {
                result = matMul(result, base);
            }
            remaining = Math.floor(remaining / 2);
            if (remaining > 0) {
                base = matMul(base, base);
            }
        }

        return result;
    }

    function isEntireParenthesized(text) {
        if (!text.startsWith('(') || !text.endsWith(')')) return false;
        let roundDepth = 0;
        let squareDepth = 0;
        let curlyDepth = 0;

        for (let index = 0; index < text.length; index++) {
            const ch = text[index];
            if (ch === '(') roundDepth++;
            else if (ch === ')') roundDepth--;
            else if (ch === '[') squareDepth++;
            else if (ch === ']') squareDepth--;
            else if (ch === '{') curlyDepth++;
            else if (ch === '}') curlyDepth--;

            if (roundDepth < 0 || squareDepth < 0 || curlyDepth < 0) return false;
            if (roundDepth === 0 && squareDepth === 0 && curlyDepth === 0 && index < text.length - 1) {
                return false;
            }
        }

        return roundDepth === 0 && squareDepth === 0 && curlyDepth === 0;
    }

    function unwrapOuterParens(text) {
        let unwrapped = String(text ?? '').trim();
        while (isEntireParenthesized(unwrapped)) {
            unwrapped = unwrapped.slice(1, -1).trim();
        }
        return unwrapped;
    }

    function isUnarySign(text, index) {
        const ch = text[index];
        if (ch !== '+' && ch !== '-') return false;

        let prevIndex = index - 1;
        while (prevIndex >= 0 && /\s/.test(text[prevIndex])) prevIndex--;
        if (prevIndex < 0) return true;

        return /[+\-*/^([\{;]/.test(text[prevIndex]);
    }

    function findTopLevelBinaryOperator(text, operators, { preferRightmost = true } = {}) {
        const operatorSet = new Set(operators);
        let roundDepth = 0;
        let squareDepth = 0;
        let curlyDepth = 0;
        let candidate = -1;

        for (let index = 0; index < text.length; index++) {
            const ch = text[index];
            if (ch === '(') {
                roundDepth++;
                continue;
            }
            if (ch === ')') {
                roundDepth--;
                continue;
            }
            if (ch === '[') {
                squareDepth++;
                continue;
            }
            if (ch === ']') {
                squareDepth--;
                continue;
            }
            if (ch === '{') {
                curlyDepth++;
                continue;
            }
            if (ch === '}') {
                curlyDepth--;
                continue;
            }

            if (roundDepth !== 0 || squareDepth !== 0 || curlyDepth !== 0) continue;
            if (!operatorSet.has(ch)) continue;
            if ((ch === '+' || ch === '-') && isUnarySign(text, index)) continue;

            candidate = index;
            if (!preferRightmost) return candidate;
        }

        return candidate;
    }

    function evaluateScalarResult(result) {
        if (result.type !== 'scalar') {
            throw new MatrixError('An dieser Stelle ist ein Skalar erforderlich');
        }
        return result.value;
    }

    function parseMatrixExponent(result) {
        const value = evaluateScalarResult(result);
        if (!Number.isFinite(value)) {
            throw new MatrixError('Potenz: Exponent ist ungültig');
        }
        const rounded = Math.round(value);
        if (Math.abs(value - rounded) > 1e-10) {
            throw new MatrixError('Potenz: Matrixexponenten müssen ganzzahlig sein');
        }
        return rounded;
    }

    function parseMatrixAtom(text, matrixVars) {
        const trimmed = String(text ?? '').trim();
        if (!trimmed) throw new MatrixError('Leerer Ausdruck');

        if (/^mat\s*\(/i.test(trimmed)) {
            return { type: 'matrix', value: parseMatLiteral(trimmed) };
        }

        if (/^[A-H]$/i.test(trimmed)) {
            const variableName = trimmed.toUpperCase();
            if (!Object.prototype.hasOwnProperty.call(matrixVars, variableName)) {
                throw new MatrixError(`Unbekannte Variable: ${variableName}`);
            }
            return { type: 'matrix', value: matrixVars[variableName] };
        }

        let scalarValue;
        try {
            scalarValue = DevCalculatorUtils.evaluateExpression(trimmed);
        } catch {
            throw new MatrixError(`Ungültiger Ausdruck: ${trimmed}`);
        }
        if (!Number.isFinite(scalarValue)) {
            throw new MatrixError(`Ungültiger Skalarausdruck: ${trimmed}`);
        }
        return { type: 'scalar', value: scalarValue };
    }

    function combineMatrixSum(left, right, operator) {
        if (left.type === 'scalar' && right.type === 'scalar') {
            return { type: 'scalar', value: operator === '+' ? left.value + right.value : left.value - right.value };
        }
        if (left.type === 'matrix' && right.type === 'matrix') {
            const fn = operator === '+' ? matAdd : matSub;
            return { type: 'matrix', value: fn(left.value, right.value) };
        }
        throw new MatrixError('Fehler: Skalar und Matrix können nicht addiert/subtrahiert werden');
    }

    function combineMatrixProduct(left, right) {
        if (left.type === 'scalar' && right.type === 'scalar') {
            return { type: 'scalar', value: left.value * right.value };
        }
        if (left.type === 'scalar' && right.type === 'matrix') {
            return { type: 'matrix', value: matScale(left.value, right.value) };
        }
        if (left.type === 'matrix' && right.type === 'scalar') {
            return { type: 'matrix', value: matScale(right.value, left.value) };
        }
        return { type: 'matrix', value: matMul(left.value, right.value) };
    }

    function applyMatrixPower(base, exponent) {
        if (base.type === 'scalar') {
            return { type: 'scalar', value: Math.pow(base.value, evaluateScalarResult(exponent)) };
        }
        return { type: 'matrix', value: matPow(base.value, parseMatrixExponent(exponent)) };
    }

    function parseMatrixExpression(input, matrixVars) {
        function parseMixedExpression(source) {
            const text = unwrapOuterParens(source);
            if (!text) throw new MatrixError('Leerer Ausdruck');

            const addIndex = findTopLevelBinaryOperator(text, ['+', '-']);
            if (addIndex >= 0) {
                const left = parseMixedExpression(text.slice(0, addIndex));
                const right = parseMixedExpression(text.slice(addIndex + 1));
                return combineMatrixSum(left, right, text[addIndex]);
            }

            const multIndex = findTopLevelBinaryOperator(text, ['*']);
            if (multIndex >= 0) {
                const left = parseMixedExpression(text.slice(0, multIndex));
                const right = parseMixedExpression(text.slice(multIndex + 1));
                return combineMatrixProduct(left, right);
            }

            const powerIndex = findTopLevelBinaryOperator(text, ['^'], { preferRightmost: false });
            if (powerIndex >= 0) {
                const base = parseMixedExpression(text.slice(0, powerIndex));
                const exponent = parseMixedExpression(text.slice(powerIndex + 1));
                return applyMatrixPower(base, exponent);
            }

            if (text.startsWith('+')) {
                return parseMixedExpression(text.slice(1));
            }

            if (text.startsWith('-')) {
                const operand = parseMixedExpression(text.slice(1));
                if (operand.type === 'matrix') {
                    return { type: 'matrix', value: matScale(-1, operand.value) };
                }
                return { type: 'scalar', value: -operand.value };
            }

            return parseMatrixAtom(text, matrixVars);
        }

        return parseMixedExpression(String(input ?? '').trim());
    }

    function buildMatLiteralString(rows) {
        const formatRow = (row) => `[${row.map((v) => String(v ?? '0')).join(';')}]`;
        return `mat(${rows.map(formatRow).join(';')})`;
    }

    function matSerialize(matrix) {
        return buildMatLiteralString(
            matrix.map((row) => row.map((v) => DevCalculatorUtils.formatGeneralResult(v)))
        );
    }

    function renderMatrixGrid(matrix) {
        const cols = matrix[0]?.length ?? 0;
        const container = document.createElement('div');
        container.className = 'mat-grid';
        if (cols > 0) container.style.gridTemplateColumns = `repeat(${cols}, auto)`;
        matrix.forEach((row) => {
            row.forEach((val) => {
                const cell = document.createElement('span');
                cell.className = 'mat-grid__cell';
                cell.textContent = DevCalculatorUtils.formatGeneralResult(val);
                container.appendChild(cell);
            });
        });
        return container;
    }

    function evaluateMatrixExpr(input, matrixVars) {
        return parseMatrixExpression(input, matrixVars || {});
    }

    function executeMatrixCommand(input, outputApi) {
        try {
            const result = evaluateMatrixExpr(input);
            if (result.type === 'matrix') {
                if (typeof outputApi.setMatrix === 'function') {
                    outputApi.setMatrix(result.value, { headline: 'Matrix' });
                } else {
                    outputApi.setText(matSerialize(result.value), { headline: 'Matrix' });
                }
            } else {
                outputApi.setText(DevCalculatorUtils.formatGeneralResult(result.value), { headline: 'Ergebnis' });
            }
        } catch (e) {
            outputApi.setText(e.message || 'Fehler', { headline: 'Matrix' });
        }
    }

    function execute(command, outputApi, { includeGraphAnalysis = true } = {}) {
        const input = String(command ?? '').trim();
        if (!input) {
            outputApi.setText('0', { headline: 'Bereit' });
            return;
        }

        const graphInner = getStandaloneCallInner(input, 'graph');
        const binomInner = getStandaloneCallInner(input, 'binom');
        const lgsInner = getStandaloneCallInner(input, 'lgs');

        if (graphInner !== null) {
            const inner = graphInner;
            const parts = [];
            let depth = 0;
            let chunk = '';
            for (const char of inner) {
                if (char === '(') depth++;
                if (char === ')') depth--;
                if (char === ';' && depth === 0) {
                    parts.push(chunk.trim());
                    chunk = '';
                    continue;
                }
                chunk += char;
            }
            if (chunk.trim()) parts.push(chunk.trim());
            const func = parts.shift() || 'x';
            const options = parseCommandOptions(parts);
            const xMin = options.xmin ? parseFloat(DevCalculatorUtils.normalizeNumberString(options.xmin)) : -5;
            const xMax = options.xmax ? parseFloat(DevCalculatorUtils.normalizeNumberString(options.xmax)) : 5;
            const yMin = options.ymin ? parseFloat(DevCalculatorUtils.normalizeNumberString(options.ymin)) : null;
            const yMax = options.ymax ? parseFloat(DevCalculatorUtils.normalizeNumberString(options.ymax)) : null;
            const prepared = DevCalculatorUtils.prepareGraphExpression(func);
            if (!prepared) {
                outputApi.setText('Ungültiger Graph-Term', { headline: 'Fehler' });
                return;
            }
            const graphOptions = {
                titel: '',
                xAchse: '',
                yAchse: '',
                xMin,
                xMax,
            };
            if (Number.isFinite(yMin)) graphOptions.yMin = yMin;
            if (Number.isFinite(yMax)) graphOptions.yMax = yMax;
            const pointsHtml = includeGraphAnalysis
                ? formatGraphAnalysisHtml(analyzeGraph(func, xMin, xMax))
                : '';
            outputApi.setGraph({
                targetId: 'graphPanelPreview',
                funktionen: [{ term: prepared, name: 'f(x)', beschreibung: prepared }],
                optionen: graphOptions,
                panelFields: {
                    function: func,
                    xmin: options.xmin || '',
                    xmax: options.xmax || '',
                    ymin: options.ymin || '',
                    ymax: options.ymax || '',
                },
                pointsHtml,
                resultText: 'siehe Graph-Panel',
            });
            return;
        }

        if (startsWithNamedCall(input, 'graph')) {
            outputApi.setText('Ungültiger Graph-Befehl', { headline: 'Fehler' });
            return;
        }

        if (/\bmat\s*\(/i.test(input)) {
            executeMatrixCommand(input, outputApi);
            return;
        }

        if (binomInner !== null) {
            const values = binomInner.split(';').map((part) => part.trim());
            const live = getLiveBinomResult({ a: values[0], b: values[1], n: values[2], p: values[3] });
            outputApi.setText(live, { headline: 'Binom' });
            return;
        }

        if (lgsInner !== null) {
            executeLGSCommand(input, outputApi);
            return;
        }

        if (startsWithNamedCall(input, 'lgs')) {
            outputApi.setText('Ungültiger LGS-Befehl', { headline: 'Fehler' });
            return;
        }

        const equalsCount = (input.match(/=/g) || []).length;
        if (equalsCount === 1) {
            solveEquationCommand(input, outputApi);
            return;
        }

        if (equalsCount === 0 && containsVariableX(input)) {
            try {
                const value = DevCalculatorUtils.evaluateExpression(input);
                if (Number.isFinite(value)) {
                    outputApi.setText(DevCalculatorUtils.formatGeneralResult(value), { headline: 'Ergebnis' });
                    return;
                }
            } catch {
                // Fall back to symbolic expansion for open x-terms.
            }
            expandExpression(input, outputApi);
            return;
        }

        try {
            const value = DevCalculatorUtils.evaluateExpression(input);
            outputApi.setText(DevCalculatorUtils.formatGeneralResult(value), { headline: 'Ergebnis' });
        } catch {
            outputApi.setText('Fehler', { headline: 'Fehler' });
        }
    }

    return {
        execute,
        getLGSVariableName,
        buildLGSCommand,
        buildBinomCommand,
        buildGraphCommand,
        buildUnaryFunctionExpression,
        buildExpExpression,
        buildLogExpression,
        buildFractionExpression,
        buildPowerExpression,
        buildIntegralExpression,
        buildFactorialExpression,
        buildBinomialCoefficientExpression,
        getLiveBinomResult,
        evaluateMatrixExpr,
        buildMatLiteralString,
        renderMatrixGrid,
        matSerialize,
    };
})();
