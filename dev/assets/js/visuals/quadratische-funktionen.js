/**
 * Figure builder for the quadratic function widget (Normalform).
 * f(x) = ax² + bx + c
 */

import { themeTextColor } from "./plotly-defaults.js";

export function buildQuadratischeFunktionenFigure({ a, b, c, xMin = -6, xMax = 6, yMin = -8, yMax = 12 }) {
    const step = 0.05;
    const xWerte = [];
    for (let x = xMin; x <= xMax + step / 2; x += step) xWerte.push(x);

    const yWerte = xWerte.map((x) => a * x * x + b * x + c);

    const data = [
        {
            x: xWerte,
            y: yWerte,
            type: "scatter",
            mode: "lines",
            name: "f",
            line: { width: 2.5 },
            hoverinfo: "name+x+y",
        },
    ];

    // Scheitelpunkt markieren (falls a ≠ 0)
    if (a !== 0) {
        const sx = -b / (2 * a);
        const sy = a * sx * sx + b * sx + c;
        if (sx >= xMin && sx <= xMax && sy >= yMin && sy <= yMax) {
            data.push({
                x: [sx],
                y: [sy],
                mode: "markers",
                type: "scatter",
                showlegend: false,
                marker: { color: themeTextColor(), size: 7, symbol: "circle", line: { color: "white", width: 1 } },
                hoverinfo: "x+y",
                cliponaxis: false,
            });
        }
    }

    const layout = {
        xaxis: { range: [xMin, xMax], dtick: 1, layer: "below traces" },
        yaxis: { range: [yMin, yMax], dtick: 2, layer: "below traces" },
        hovermode: "closest",
        legend: { orientation: "h", x: 0.5, xanchor: "center", y: -0.25 },
        margin: { t: 20, r: 30, b: 30, l: 45 },
    };

    return { data, layout };
}
