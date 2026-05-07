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

    function replaceStandaloneX(expression, xValue) {
        return String(expression || '').replace(
            /(^|[^a-zA-Z0-9_.])x([^a-zA-Z0-9_]|$)/g,
            `$1(${xValue})$2`
        );
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
                let expr = `(${leftSide}) - (${rightSide})`;
                expr = normalizeDecimalCommas(expr);
                expr = DevCalculatorUtils.addImplicitMultiplication(
                    DevCalculatorUtils.normalizeUnaryMinusExponent(
                        DevCalculatorUtils.convertFactorialSyntax(
                            DevCalculatorUtils.convertNCrSyntax(
                                DevCalculatorUtils.convertWurzelSyntax(
                                    DevCalculatorUtils.convertLogBaseSyntax(
                                        DevCalculatorUtils.convertCustomENotation(expr)
                                    )
                                )
                            )
                        )
                    )
                );
                expr = DevCalculatorUtils.normalizeConstants(expr)
                    .replace(/\^/g, '**')
                    .replace(/e\*\*/g, 'Math.E**')
                    .replace(/(?<!Math\.)\babs\b/g, 'Math.abs')
                    .replace(/(?<!Math\.)\bbetrag\b/gi, 'Math.abs')
                    .replace(/(?<!Math\.)\bsqrt\b/g, 'Math.sqrt')
                    .replace(/(?<!Math\.)\bexp\b/g, 'Math.exp')
                    .replace(/(?<!Math\.)\bln\b/g, 'Math.log')
                    .replace(/(?<!DevCalculatorUtils\.)\blogBase\s*\(/g, 'DevCalculatorUtils.logBase(')
                    .replace(/(?<!Math\.)\blog\s*\(/g, 'Math.log10(')
                    .replace(/(?<!Math\.)\basin\b/g, 'Math.asin')
                    .replace(/(?<!Math\.)\bacos\b/g, 'Math.acos')
                    .replace(/(?<!Math\.)\batan\b/g, 'Math.atan')
                    .replace(/(?<!Math\.)\bsin\b/g, 'Math.sin')
                    .replace(/(?<!Math\.)\bcos\b/g, 'Math.cos')
                    .replace(/(?<!Math\.)\btan\b/g, 'Math.tan');
                expr = replaceStandaloneX(expr, x);
                return eval(expr);
            }

            const tolerance = 1e-6;
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
        deduplicateXFactor: 2,
    });

    function evaluateGraphFunctionJS(rawExpr, x) {
        try {
            let expr = `(${rawExpr})`;
            expr = normalizeDecimalCommas(expr);
            expr = DevCalculatorUtils.addImplicitMultiplication(
                DevCalculatorUtils.normalizeUnaryMinusExponent(
                    DevCalculatorUtils.convertFactorialSyntax(
                        DevCalculatorUtils.convertNCrSyntax(
                            DevCalculatorUtils.convertWurzelSyntax(
                                DevCalculatorUtils.convertLogBaseSyntax(
                                    DevCalculatorUtils.convertCustomENotation(expr)
                                )
                            )
                        )
                    )
                )
            );
            expr = DevCalculatorUtils.normalizeConstants(expr)
                .replace(/\^/g, '**')
                .replace(/e\*\*/g, 'Math.E**')
                .replace(/(?<!Math\.)\babs\b/g, 'Math.abs')
                .replace(/(?<!Math\.)\bbetrag\b/gi, 'Math.abs')
                .replace(/(?<!Math\.)\bsqrt\b/g, 'Math.sqrt')
                .replace(/(?<!Math\.)\bexp\b/g, 'Math.exp')
                .replace(/(?<!Math\.)\bln\b/g, 'Math.log')
                .replace(/(?<!DevCalculatorUtils\.)\blogBase\s*\(/g, 'DevCalculatorUtils.logBase(')
                .replace(/(?<!Math\.)\blog\s*\(/g, 'Math.log10(')
                .replace(/(?<!Math\.)\basin\b/g, 'Math.asin')
                .replace(/(?<!Math\.)\bacos\b/g, 'Math.acos')
                .replace(/(?<!Math\.)\batan\b/g, 'Math.atan')
                .replace(/(?<!Math\.)\bsin\b/g, 'Math.sin')
                .replace(/(?<!Math\.)\bcos\b/g, 'Math.cos')
                .replace(/(?<!Math\.)\btan\b/g, 'Math.tan');
            expr = replaceStandaloneX(expr, x);
            return eval(expr);
        } catch {
            return NaN;
        }
    }

    function findGraphRoots(rawExpr, xMin, xMax) {
        const tolerance = GRAPH_ANALYSIS_CONFIG.zerosTolerance;
        const rangeMin = GRAPH_ANALYSIS_CONFIG.zerosRangeMin;
        const rangeMax = GRAPH_ANALYSIS_CONFIG.zerosRangeMax;
        const steps = GRAPH_ANALYSIS_CONFIG.zerosSteps;
        const step = (rangeMax - rangeMin) / steps;
        const roots = [];

        for (let i = 0; i < steps; i++) {
            const x1 = rangeMin + i * step;
            const x2 = x1 + step;
            const f1 = evaluateGraphFunctionJS(rawExpr, x1);
            const f2 = evaluateGraphFunctionJS(rawExpr, x2);
            const root = findRootInInterval(
                (x) => evaluateGraphFunctionJS(rawExpr, x),
                x1,
                x2,
                f1,
                f2,
                tolerance
            );
            if (root !== null) roots.push(root);
        }

        return deduplicateNumericRoots(
            roots,
            (value) => evaluateGraphFunctionJS(rawExpr, value),
            GRAPH_ANALYSIS_CONFIG.zerosRoundFactor,
            Math.max(GRAPH_ANALYSIS_CONFIG.zerosDeduplicateTolerance, step / 20)
        )
            .filter((value) => value >= xMin && value <= xMax);
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

    function findGraphExtrema(rawExpr, xMin, xMax) {
        const grid = getGraphAnalysisGrid(xMin, xMax);
        if (!grid) return [];

        const { h } = grid;
        const cache = new Map();

        function f(x) {
            if (cache.has(x)) return cache.get(x);
            const value = evaluateGraphFunctionJS(rawExpr, x);
            cache.set(x, value);
            return value;
        }

        function firstDiff(x) {
            return (f(x + h) - f(x - h)) / (2 * h);
        }

        const roots = findSignChangeRoots(firstDiff, xMin, xMax, h, {
            signTolerance: GRAPH_ANALYSIS_CONFIG.extremaSignTolerance,
            refineIterations: GRAPH_ANALYSIS_CONFIG.extremaRefineIterations,
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

            extrema.push({
                x: Math.abs(xr) < GRAPH_ANALYSIS_CONFIG.cleanValueEpsilon ? 0 : xr,
                y: Math.abs(y) < GRAPH_ANALYSIS_CONFIG.cleanValueEpsilon ? 0 : y,
                type: leftSign > rightSign ? 'Max' : 'Min',
            });
        }

        return deduplicatePointsByX(extrema, h * GRAPH_ANALYSIS_CONFIG.deduplicateXFactor)
            .sort((left, right) => left.x - right.x);
    }

    function findGraphInflectionPoints(rawExpr, xMin, xMax) {
        const grid = getGraphAnalysisGrid(xMin, xMax);
        if (!grid) return [];

        const { h } = grid;
        const cache = new Map();

        function f(x) {
            if (cache.has(x)) return cache.get(x);
            const value = evaluateGraphFunctionJS(rawExpr, x);
            cache.set(x, value);
            return value;
        }

        function secondDiff(x) {
            return (f(x + h) - 2 * f(x) + f(x - h)) / (h * h);
        }

        const roots = findSignChangeRoots(secondDiff, xMin, xMax, h, {
            signTolerance: GRAPH_ANALYSIS_CONFIG.inflectionSignTolerance,
            refineIterations: GRAPH_ANALYSIS_CONFIG.inflectionRefineIterations,
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

            points.push({
                x: Math.abs(xr) < GRAPH_ANALYSIS_CONFIG.cleanValueEpsilon ? 0 : xr,
                y: Math.abs(y) < GRAPH_ANALYSIS_CONFIG.cleanValueEpsilon ? 0 : y,
            });
        }

        return deduplicatePointsByX(points, h * GRAPH_ANALYSIS_CONFIG.deduplicateXFactor)
            .sort((left, right) => left.x - right.x);
    }

    function analyzeGraph(rawExpr, xMin, xMax) {
        return {
            roots: findGraphRoots(rawExpr, xMin, xMax),
            extrema: findGraphExtrema(rawExpr, xMin, xMax),
            inflectionPoints: findGraphInflectionPoints(rawExpr, xMin, xMax),
        };
    }

    function formatPointValue(value) {
        if (!Number.isFinite(value)) return 'n.def.';
        if (Math.abs(value) < 1e-9) return '0';
        const absValue = Math.abs(value);
        if (absValue < 0.001 || absValue > 99999) {
            return value.toExponential(2).replace('.', ',');
        }
        return value.toFixed(5).replace(/\.?0+$/, '').replace('.', ',');
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

    function execute(command, outputApi) {
        const input = String(command ?? '').trim();
        if (!input) {
            outputApi.setText('0', { headline: 'Bereit' });
            return;
        }

        if (/^graph\s*\(/i.test(input)) {
            const match = input.match(/^graph\s*\((.*)\)\s*$/i);
            if (!match) {
                outputApi.setText('Ungültiger Graph-Befehl', { headline: 'Fehler' });
                return;
            }
            const inner = match[1];
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
            const analysis = analyzeGraph(func, xMin, xMax);
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
                pointsHtml: formatGraphAnalysisHtml(analysis),
                resultText: 'siehe Graph-Panel',
            });
            return;
        }

        const binomMatch = input.match(/^binom\s*\((.*)\)\s*$/i);
        if (binomMatch) {
            const values = binomMatch[1].split(';').map((part) => part.trim());
            const live = getLiveBinomResult({ a: values[0], b: values[1], n: values[2], p: values[3] });
            outputApi.setText(live, { headline: 'Binom' });
            return;
        }

        if (/^lgs\s*\(/i.test(input)) {
            executeLGSCommand(input, outputApi);
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
    };
})();
