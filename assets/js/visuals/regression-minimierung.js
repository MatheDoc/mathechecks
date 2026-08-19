/**
 * Figure builder for the regression minimization widget.
 * Shows a fixed point cloud, an adjustable line f(x) = m·x + b and the
 * squared residuals drawn as actual squares (side length = |residual|).
 */

import { themeTextColor } from "./plotly-defaults.js?v=20260507-plotly-hover-name-theme";

/** Fixed, almost linear point cloud (least squares optimum: m = 0.85, b = 1.25). */
export const REGRESSION_MINIMIERUNG_PUNKTE = [
    { x: 1, y: 2 },
    { x: 2, y: 3.5 },
    { x: 3, y: 3 },
    { x: 4, y: 5 },
    { x: 5, y: 5.5 },
];

/** Least squares fit in Summenform: m = (n·Σxy − Σx·Σy) / (n·Σx² − (Σx)²). */
export function leastSquaresFit(points) {
    const n = points.length;
    let sx = 0;
    let sy = 0;
    let sxx = 0;
    let sxy = 0;
    for (const point of points) {
        sx += point.x;
        sy += point.y;
        sxx += point.x * point.x;
        sxy += point.x * point.y;
    }
    const m = (n * sxy - sx * sy) / (n * sxx - sx * sx);
    const b = (sy - m * sx) / n;
    return { m, b };
}

/** Sum of squared errors for the line f(x) = m·x + b. */
export function sumSquaredErrors(points, m, b) {
    return points.reduce((acc, point) => {
        const residual = point.y - (m * point.x + b);
        return acc + residual * residual;
    }, 0);
}

function computeBounds(points, m, b) {
    // Minimum window keeps the view stable near the optimum.
    let xMin = -0.5;
    let xMax = 6.5;
    let yMin = -0.5;
    let yMax = 7;

    for (const point of points) {
        const fx = m * point.x + b;
        const side = Math.abs(point.y - fx);
        xMax = Math.max(xMax, point.x + side + 0.5);
        yMin = Math.min(yMin, Math.min(point.y, fx) - 0.5);
        yMax = Math.max(yMax, Math.max(point.y, fx) + 0.5);
    }

    return { xMin, xMax, yMin, yMax };
}

export function buildRegressionMinimierungFigure({ points, m, b }) {
    const textColor = themeTextColor();
    const bounds = computeBounds(points, m, b);

    // All squares in a single fill trace, separated by null gaps.
    const squareXs = [];
    const squareYs = [];
    for (const point of points) {
        const fx = m * point.x + b;
        const side = Math.abs(point.y - fx);
        if (side < 1e-9) continue;
        squareXs.push(point.x, point.x, point.x + side, point.x + side, point.x, null);
        squareYs.push(point.y, fx, fx, point.y, point.y, null);
    }

    const data = [
        {
            x: squareXs,
            y: squareYs,
            type: "scatter",
            mode: "lines",
            fill: "toself",
            fillcolor: "rgba(245, 130, 49, 0.25)",
            line: { color: "#f58231", width: 1.5 },
            showlegend: false,
            hoverinfo: "skip",
        },
        {
            x: [bounds.xMin, bounds.xMax],
            y: [m * bounds.xMin + b, m * bounds.xMax + b],
            type: "scatter",
            mode: "lines",
            showlegend: false,
            line: { color: "#4363d8", width: 3 },
            hoverinfo: "skip",
        },
        {
            x: points.map((point) => point.x),
            y: points.map((point) => point.y),
            type: "scatter",
            mode: "markers",
            showlegend: false,
            marker: {
                color: textColor,
                size: 9,
                line: { color: "white", width: 1 },
            },
            hovertemplate: "x = %{x:.1f}<br>y = %{y:.1f}<extra></extra>",
            cliponaxis: false,
        },
    ];

    return {
        data,
        layout: {
            margin: { t: 20, r: 18, b: 40, l: 48 },
            hovermode: "closest",
            xaxis: {
                title: { text: "x" },
                range: [bounds.xMin, bounds.xMax],
            },
            yaxis: {
                title: { text: "y" },
                range: [bounds.yMin, bounds.yMax],
                // Equal units on both axes so squares actually look square.
                scaleanchor: "x",
                scaleratio: 1,
            },
        },
    };
}
