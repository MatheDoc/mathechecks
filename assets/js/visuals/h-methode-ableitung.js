/**
 * Figure builder for the h-method widget.
 * Visualizes the function f(x)=x^2 together with a secant and the tangent in x0.
 */

import { themeTextColor } from "./plotly-defaults.js?v=20260507-plotly-hover-name-theme";

export function buildHMethodeAbleitungFigure({ x0, h, xMin = -4, xMax = 4, yMin = -2, yMax = 16 }) {
    const step = 0.05;
    const eps = 1e-9;
    const xWerte = [];
    for (let x = xMin; x <= xMax + step / 2; x += step) xWerte.push(x);

    const y0 = x0 * x0;
    const x1 = x0 + h;
    const y1 = x1 * x1;
    const tangentSteigung = 2 * x0;

    const data = [
        {
            x: xWerte,
            y: xWerte.map((x) => x * x),
            type: "scatter",
            mode: "lines",
            name: "f(x)=x<sup>2</sup>",
            line: { width: 2.5, color: "#4363d8" },
            hoverinfo: "name+x+y",
        },
        {
            x: xWerte,
            y: xWerte.map((x) => tangentSteigung * (x - x0) + y0),
            type: "scatter",
            mode: "lines",
            name: "Tangente in x<sub>0</sub>",
            line: { width: 2, color: "#3cb44b", dash: "dash" },
            hoverinfo: "name+x+y",
        },
    ];

    if (Math.abs(h) > eps) {
        const sekantenSteigung = (y1 - y0) / h;
        data.splice(1, 0, {
            x: xWerte,
            y: xWerte.map((x) => sekantenSteigung * (x - x0) + y0),
            type: "scatter",
            mode: "lines",
            name: "Sekante über h",
            line: { width: 2, color: "#f58231" },
            hoverinfo: "name+x+y",
        });
    }

    data.push({
        x: Math.abs(h) > eps ? [x0, x1] : [x0],
        y: Math.abs(h) > eps ? [y0, y1] : [y0],
        type: "scatter",
        mode: "markers+text",
        name: "Punkte",
        showlegend: false,
        marker: { color: themeTextColor(), size: 8, symbol: "circle", line: { color: "white", width: 1 } },
        text: Math.abs(h) > eps ? ["P", "Q"] : ["P"],
        textposition: "top center",
        hoverinfo: "text+x+y",
        cliponaxis: false,
    });

    const layout = {
        xaxis: { range: [xMin, xMax], dtick: 1, layer: "below traces" },
        yaxis: { range: [yMin, yMax], dtick: 2, layer: "below traces" },
        hovermode: "closest",
        legend: { orientation: "h", x: 0.5, xanchor: "center", y: -0.25 },
        margin: { t: 20, r: 30, b: 30, l: 45 },
    };

    return { data, layout };
}