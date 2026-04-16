/**
 * Figure builder for a general histogram (arbitrary x/y data).
 *
 * Used in Skript pages where a discrete probability distribution is
 * visualised with freely specified x and y values (not binomial).
 */

import { themeTextColor } from "./plotly-defaults.js";

export function buildHistogrammAllgemeinFigure({
    x,
    y,
    titel = "",
    balkenbreite = null,
}) {
    const trace = {
        x,
        y,
        type: "bar",
        offset: 0,
        name: "P(X = x)",
        marker: {
            color: "rgba(54, 162, 235, 0.3)",
            line: {
                color: "rgba(162, 162, 162, 0.7)",
                width: 1,
            },
        },
    };

    if (balkenbreite != null) {
        trace.width = Number(balkenbreite);
    }

    const data = [trace];

    const layout = {
        title: titel ? { text: titel, y: 0.85 } : undefined,
        xaxis: {
            title: "x",
            tickmode: "array",
            tickvals: x,
            type: "linear",
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
