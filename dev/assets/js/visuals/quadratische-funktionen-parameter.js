/**
 * Figure builder for the quadratic parameter widget (Scheitelpunktform).
 * f(x) = a(x - d)² + e  with reference parabola x²
 */

import { themeTextColor } from "./plotly-defaults.js";

export function buildQuadratischeParameterFigure({ a, d, e, xMin = -6, xMax = 6, yMin = -8, yMax = 12 }) {
    const step = 0.05;
    const xWerte = [];
    for (let x = xMin; x <= xMax + step / 2; x += step) xWerte.push(x);

    const yParabel = xWerte.map((x) => a * (x - d) * (x - d) + e);
    const yNormal = xWerte.map((x) => x * x);

    const data = [
        // Referenzparabel x² (gestrichelt, dezent)
        {
            x: xWerte,
            y: yNormal,
            type: "scatter",
            mode: "lines",
            name: "x²",
            line: { width: 1.5, dash: "dash", color: themeTextColor() + "50" },
            hoverinfo: "skip",
        },
        // Aktuelle Parabel
        {
            x: xWerte,
            y: yParabel,
            type: "scatter",
            mode: "lines",
            name: "f",
            line: { width: 2.5 },
            hoverinfo: "name+x+y",
        },
        // Scheitelpunkt
        {
            x: [d],
            y: [e],
            mode: "markers",
            type: "scatter",
            showlegend: false,
            name: "S",
            marker: { color: themeTextColor(), size: 7, symbol: "circle", line: { color: "white", width: 1 } },
            text: ["S(" + d + " | " + e + ")"],
            hoverinfo: "text",
            cliponaxis: false,
        },
    ];

    const layout = {
        xaxis: { range: [xMin, xMax], dtick: 1, layer: "below traces" },
        yaxis: { range: [yMin, yMax], dtick: 2, layer: "below traces" },
        hovermode: "closest",
        legend: { orientation: "h", x: 0.5, xanchor: "center", y: -0.25 },
        margin: { t: 20, r: 30, b: 30, l: 45 },
    };

    return { data, layout };
}
