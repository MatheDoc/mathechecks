import { themeTextColor } from "./plotly-defaults.js?v=20260507-plotly-hover-name-theme";

const REGRESSION_TYPES = [
    {
        key: "linear",
        label: "Lineare Regression",
        sample: sampleLinearPoints,
        fit: fitLinearRegression,
        xFloor: null,
    },
    {
        key: "quadratic",
        label: "Quadratische Regression",
        sample: sampleQuadraticPoints,
        fit: fitQuadraticRegression,
        xFloor: null,
    },
    {
        key: "cubic",
        label: "Kubische Regression",
        sample: sampleCubicPoints,
        fit: fitCubicRegression,
        xFloor: null,
    },
    {
        key: "exponential",
        label: "Exponentielle Regression",
        sample: sampleExponentialPoints,
        fit: fitExponentialRegression,
        xFloor: 0,
    },
    {
        key: "sqrt",
        label: "Wurzel-Regression",
        sample: sampleRootPoints,
        fit: fitRootRegression,
        xFloor: 0,
    },
    {
        key: "logarithmic",
        label: "Logarithmische Regression",
        sample: sampleLogarithmicPoints,
        fit: fitLogarithmicRegression,
        xFloor: 0.1,
    },
];

function randomBetween(min, max) {
    return min + Math.random() * (max - min);
}

function randomInt(min, max) {
    return Math.floor(randomBetween(min, max + 1));
}

function randomSigned(minMagnitude, maxMagnitude) {
    const magnitude = randomBetween(minMagnitude, maxMagnitude);
    return Math.random() < 0.5 ? -magnitude : magnitude;
}

function sum(values) {
    return values.reduce((total, value) => total + value, 0);
}

function linspace(min, max, count = 220) {
    if (count <= 1) return [min];
    return Array.from({ length: count }, (_, index) => (
        min + ((max - min) * index) / (count - 1)
    ));
}

function solveLinearSystem(matrix, rhs) {
    const size = matrix.length;
    const augmented = matrix.map((row, index) => [...row, rhs[index]]);

    for (let pivot = 0; pivot < size; pivot += 1) {
        let maxRow = pivot;
        for (let row = pivot + 1; row < size; row += 1) {
            if (Math.abs(augmented[row][pivot]) > Math.abs(augmented[maxRow][pivot])) {
                maxRow = row;
            }
        }

        if (Math.abs(augmented[maxRow][pivot]) < 1e-9) {
            throw new Error("Singuläres Gleichungssystem");
        }

        [augmented[pivot], augmented[maxRow]] = [augmented[maxRow], augmented[pivot]];

        for (let row = pivot + 1; row < size; row += 1) {
            const factor = augmented[row][pivot] / augmented[pivot][pivot];
            for (let column = pivot; column <= size; column += 1) {
                augmented[row][column] -= factor * augmented[pivot][column];
            }
        }
    }

    const solution = new Array(size).fill(0);
    for (let row = size - 1; row >= 0; row -= 1) {
        let value = augmented[row][size];
        for (let column = row + 1; column < size; column += 1) {
            value -= augmented[row][column] * solution[column];
        }
        solution[row] = value / augmented[row][row];
    }

    return solution;
}

function formatNumberTex(value, digits = 2) {
    const normalized = Math.abs(value) < 5e-4 ? 0 : value;
    return normalized.toFixed(digits).replace(".", "{,}");
}

function formatSignedTex(value, isFirst = false) {
    const absValue = formatNumberTex(Math.abs(value));
    if (isFirst) {
        return value < 0 ? `-${absValue}` : absValue;
    }
    return value < 0 ? ` - ${absValue}` : ` + ${absValue}`;
}

function computeBounds(points, curvePoints, xFloor = null) {
    const allPoints = [...points, ...curvePoints];
    const xs = allPoints.map((point) => point.x);
    const ys = allPoints.map((point) => point.y);
    const rawXMin = Math.min(...xs);
    const rawXMax = Math.max(...xs);
    const rawYMin = Math.min(...ys);
    const rawYMax = Math.max(...ys);
    const xSpan = Math.max(rawXMax - rawXMin, 1);
    const ySpan = Math.max(rawYMax - rawYMin, 1);

    return {
        xMin: xFloor == null ? rawXMin - xSpan * 0.12 : Math.max(xFloor, rawXMin - xSpan * 0.12),
        xMax: rawXMax + xSpan * 0.12,
        yMin: rawYMin - ySpan * 0.16,
        yMax: rawYMax + ySpan * 0.16,
    };
}

function sampleLinearPoints() {
    const slope = randomSigned(0.7, 2.8);
    const intercept = randomBetween(-5, 5);
    const count = randomInt(16, 24);
    return Array.from({ length: count }, () => {
        const x = randomBetween(-5.5, 5.5);
        return { x, y: slope * x + intercept + randomBetween(-2.2, 2.2) };
    });
}

function sampleQuadraticPoints() {
    const a = randomSigned(0.35, 1.15);
    const b = randomBetween(-2.2, 2.2);
    const c = randomBetween(-4, 4);
    const count = randomInt(18, 25);
    return Array.from({ length: count }, () => {
        const x = randomBetween(-4.4, 4.4);
        return { x, y: a * x * x + b * x + c + randomBetween(-3, 3) };
    });
}

function sampleCubicPoints() {
    const a = randomSigned(0.08, 0.24);
    const b = randomBetween(-0.9, 0.9);
    const c = randomBetween(-2.1, 2.1);
    const d = randomBetween(-3.2, 3.2);
    const count = randomInt(18, 24);
    return Array.from({ length: count }, () => {
        const x = randomBetween(-3.8, 3.8);
        return { x, y: a * x * x * x + b * x * x + c * x + d + randomBetween(-3.2, 3.2) };
    });
}

function sampleExponentialPoints() {
    const a = randomBetween(1.4, 5.5);
    const b = randomSigned(0.18, 0.42);
    const count = randomInt(18, 24);
    return Array.from({ length: count }, () => {
        const x = randomBetween(0, 6.2);
        const y = a * Math.exp(b * x);
        return { x, y: y * (1 + randomBetween(-0.16, 0.16)) };
    });
}

function sampleRootPoints() {
    const a = randomSigned(1.4, 4.8);
    const b = randomBetween(-3, 3);
    const count = randomInt(18, 24);
    return Array.from({ length: count }, () => {
        const x = randomBetween(0.15, 9.5);
        return { x, y: a * Math.sqrt(x) + b + randomBetween(-1.5, 1.5) };
    });
}

function sampleLogarithmicPoints() {
    const a = randomSigned(1.4, 4.3);
    const b = randomBetween(-2.8, 2.8);
    const count = randomInt(18, 24);
    return Array.from({ length: count }, () => {
        const x = randomBetween(0.6, 10);
        return { x, y: a * Math.log(x) + b + randomBetween(-1.4, 1.4) };
    });
}

function fitLinearRegression(points) {
    const xs = points.map((point) => point.x);
    const ys = points.map((point) => point.y);
    const count = points.length;
    const sx = sum(xs);
    const sy = sum(ys);
    const sxx = sum(xs.map((x) => x * x));
    const sxy = sum(points.map((point) => point.x * point.y));
    const denominator = count * sxx - sx * sx;
    if (Math.abs(denominator) < 1e-9) throw new Error("Ungültige lineare Regression");

    const a = (count * sxy - sx * sy) / denominator;
    const b = (sy - a * sx) / count;
    const xMin = Math.min(...xs);
    const xMax = Math.max(...xs);

    return {
        curvePoints: linspace(xMin, xMax).map((x) => ({ x, y: a * x + b })),
        formulaLatex: `$y = ${formatSignedTex(a, true)}x${formatSignedTex(b)}$`,
    };
}

function fitQuadraticRegression(points) {
    const xs = points.map((point) => point.x);
    const s0 = points.length;
    const s1 = sum(xs);
    const s2 = sum(xs.map((x) => x ** 2));
    const s3 = sum(xs.map((x) => x ** 3));
    const s4 = sum(xs.map((x) => x ** 4));
    const t0 = sum(points.map((point) => point.y));
    const t1 = sum(points.map((point) => point.x * point.y));
    const t2 = sum(points.map((point) => point.x ** 2 * point.y));
    const [c, b, a] = solveLinearSystem(
        [[s0, s1, s2], [s1, s2, s3], [s2, s3, s4]],
        [t0, t1, t2]
    );
    const xMin = Math.min(...xs);
    const xMax = Math.max(...xs);

    return {
        curvePoints: linspace(xMin, xMax).map((x) => ({ x, y: a * x * x + b * x + c })),
        formulaLatex: `$y = ${formatSignedTex(a, true)}x^2${formatSignedTex(b)}x${formatSignedTex(c)}$`,
    };
}

function fitCubicRegression(points) {
    const xs = points.map((point) => point.x);
    const sums = Array.from({ length: 7 }, (_, power) => sum(xs.map((x) => x ** power)));
    const targets = Array.from({ length: 4 }, (_, power) => (
        sum(points.map((point) => point.y * (point.x ** power)))
    ));
    const [d, c, b, a] = solveLinearSystem(
        [
            [sums[0], sums[1], sums[2], sums[3]],
            [sums[1], sums[2], sums[3], sums[4]],
            [sums[2], sums[3], sums[4], sums[5]],
            [sums[3], sums[4], sums[5], sums[6]],
        ],
        targets
    );
    const xMin = Math.min(...xs);
    const xMax = Math.max(...xs);

    return {
        curvePoints: linspace(xMin, xMax).map((x) => ({ x, y: a * x ** 3 + b * x ** 2 + c * x + d })),
        formulaLatex: `$y = ${formatSignedTex(a, true)}x^3${formatSignedTex(b)}x^2${formatSignedTex(c)}x${formatSignedTex(d)}$`,
    };
}

function fitExponentialRegression(points) {
    const positivePoints = points.filter((point) => point.y > 0);
    if (positivePoints.length < 6) throw new Error("Zu wenige positive Punkte für Exponentialfit");
    const xs = positivePoints.map((point) => point.x);
    const logYs = positivePoints.map((point) => Math.log(point.y));
    const count = positivePoints.length;
    const sx = sum(xs);
    const slogy = sum(logYs);
    const sxx = sum(xs.map((x) => x * x));
    const sxlogy = sum(xs.map((x, index) => x * logYs[index]));
    const denominator = count * sxx - sx * sx;
    if (Math.abs(denominator) < 1e-9) throw new Error("Ungültige exponentielle Regression");

    const b = (count * sxlogy - sx * slogy) / denominator;
    const lnA = (slogy - b * sx) / count;
    const a = Math.exp(lnA);
    const xMin = Math.min(...xs);
    const xMax = Math.max(...xs);

    return {
        curvePoints: linspace(xMin, xMax).map((x) => ({ x, y: a * Math.exp(b * x) })),
        formulaLatex: `$y = ${formatSignedTex(a, true)} \\cdot e^{${formatSignedTex(b, true)}x}$`,
    };
}

function fitRootRegression(points) {
    const validPoints = points.filter((point) => point.x >= 0);
    if (validPoints.length < 6) throw new Error("Zu wenige Punkte für Wurzelfit");
    const rootXs = validPoints.map((point) => Math.sqrt(point.x));
    const ys = validPoints.map((point) => point.y);
    const count = validPoints.length;
    const sx = sum(rootXs);
    const sy = sum(ys);
    const sxx = sum(rootXs.map((value) => value * value));
    const sxy = sum(rootXs.map((value, index) => value * ys[index]));
    const denominator = count * sxx - sx * sx;
    if (Math.abs(denominator) < 1e-9) throw new Error("Ungültige Wurzel-Regression");

    const a = (count * sxy - sx * sy) / denominator;
    const b = (sy - a * sx) / count;
    const xMin = Math.min(...validPoints.map((point) => point.x));
    const xMax = Math.max(...validPoints.map((point) => point.x));

    return {
        curvePoints: linspace(xMin, xMax).map((x) => ({ x, y: a * Math.sqrt(Math.max(x, 0)) + b })),
        formulaLatex: `$y = ${formatSignedTex(a, true)}\\sqrt{x}${formatSignedTex(b)}$`,
    };
}

function fitLogarithmicRegression(points) {
    const validPoints = points.filter((point) => point.x > 0);
    if (validPoints.length < 6) throw new Error("Zu wenige Punkte für Logarithmusfit");
    const logXs = validPoints.map((point) => Math.log(point.x));
    const ys = validPoints.map((point) => point.y);
    const count = validPoints.length;
    const sx = sum(logXs);
    const sy = sum(ys);
    const sxx = sum(logXs.map((value) => value * value));
    const sxy = sum(logXs.map((value, index) => value * ys[index]));
    const denominator = count * sxx - sx * sx;
    if (Math.abs(denominator) < 1e-9) throw new Error("Ungültige logarithmische Regression");

    const a = (count * sxy - sx * sy) / denominator;
    const b = (sy - a * sx) / count;
    const xMin = Math.min(...validPoints.map((point) => point.x));
    const xMax = Math.max(...validPoints.map((point) => point.x));

    return {
        curvePoints: linspace(xMin, xMax).map((x) => ({ x, y: a * Math.log(Math.max(x, 0.1)) + b })),
        formulaLatex: `$y = ${formatSignedTex(a, true)}\\ln(x)${formatSignedTex(b)}$`,
    };
}

function buildFallbackScenario() {
    const points = [
        { x: -4, y: -7.6 },
        { x: -2, y: -2.8 },
        { x: -1, y: -0.4 },
        { x: 1, y: 3.1 },
        { x: 2.5, y: 6.6 },
        { x: 4, y: 10.2 },
    ];

    return {
        typeLabel: "Lineare Regression",
        formulaLatex: "$y = 2{,}24x + 1{,}50$",
        xFloor: null,
        points,
        curvePoints: linspace(-4, 4).map((x) => ({ x, y: 2.24 * x + 1.5 })),
    };
}

export function createPunktwolkeRegressionScenario() {
    for (let attempt = 0; attempt < 12; attempt += 1) {
        const type = REGRESSION_TYPES[Math.floor(Math.random() * REGRESSION_TYPES.length)];
        try {
            const points = type.sample();
            const fit = type.fit(points);
            if (fit.curvePoints.some((point) => !Number.isFinite(point.y))) {
                throw new Error("Nicht endliche Regressionswerte");
            }
            return {
                typeLabel: type.label,
                formulaLatex: fit.formulaLatex,
                xFloor: type.xFloor,
                points,
                curvePoints: fit.curvePoints,
            };
        } catch {
            // Retry with a new random sample.
        }
    }

    return buildFallbackScenario();
}

export function buildPunktwolkeRegressionFigure({ scenario, showCurve = false }) {
    const lineColor = themeTextColor();
    const curvePoints = showCurve ? scenario.curvePoints : [];
    const bounds = computeBounds(scenario.points, curvePoints, scenario.xFloor);

    const data = [
        {
            x: scenario.points.map((point) => point.x),
            y: scenario.points.map((point) => point.y),
            type: "scatter",
            mode: "markers",
            showlegend: false,
            marker: {
                color: lineColor,
                size: 8,
                opacity: 0.52,
            },
            hovertemplate: "x = %{x:.2f}<br>y = %{y:.2f}<extra></extra>",
            cliponaxis: false,
        },
    ];

    if (curvePoints.length > 0) {
        data.push({
            x: curvePoints.map((point) => point.x),
            y: curvePoints.map((point) => point.y),
            type: "scatter",
            mode: "lines",
            showlegend: false,
            line: {
                color: lineColor,
                width: 3,
            },
            hoverinfo: "skip",
        });
    }

    return {
        data,
        layout: {
            margin: { t: 26, r: 18, b: 46, l: 58 },
            hovermode: "closest",
            xaxis: {
                title: { text: "x" },
                range: [bounds.xMin, bounds.xMax],
            },
            yaxis: {
                title: { text: "y" },
                range: [bounds.yMin, bounds.yMax],
            },
        },
    };
}