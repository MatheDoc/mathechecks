/**
 * Figure builder for a general histogram (arbitrary x/y data).
 *
 * Used in Skript pages where a discrete probability distribution is
 * visualised with freely specified x and y values (not binomial).
 */

import { themeTextColor } from "./plotly-defaults.js";

function inferBarWidth(x, explicitWidth) {
    if (explicitWidth != null) return Number(explicitWidth);
    if (x.length < 2) return 1;

    const numericX = x.map(Number).sort((left, right) => left - right);
    let minDistance = Infinity;

    for (let i = 1; i < numericX.length; i++) {
        const distance = numericX[i] - numericX[i - 1];
        if (distance > 0 && distance < minDistance) {
            minDistance = distance;
        }
    }

    return Number.isFinite(minDistance) ? minDistance : 1;
}

export function buildHistogrammAllgemeinFigure({
    x,
    y,
    titel = "",
    balkenbreite = null,
}) {
    const numericX = x.map(Number);
    const barWidth = inferBarWidth(x, balkenbreite);
    const trace = {
        x,
        y,
        type: "bar",
        offset: 0,
        width: barWidth,
        name: "P(X = x)",
        marker: {
            color: "rgba(54, 162, 235, 0.3)",
            line: {
                color: "rgba(162, 162, 162, 0.7)",
                width: 1,
            },
        },
    };

    const data = [trace];

    const layout = {
        title: titel ? { text: titel, y: 0.85 } : undefined,
        xaxis: {
            title: "x",
            tickmode: "array",
            tickvals: numericX.map((value) => value + barWidth / 2),
            ticktext: x.map(String),
            type: "linear",
            range: [Math.min(...numericX), Math.max(...numericX) + barWidth],
            showgrid: false,
        },
        yaxis: {
            title: "P(X = x)",
            range: [0, Math.max(...y) * 1.1],
            gridcolor: themeTextColor() + "33",
        },
        bargap: 0,
        showlegend: false,
        margin: { t: 100, r: 20, b: 40, l: 50 },
    };

    return { data, layout };
}
