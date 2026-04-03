/**
 * Shared graph builder for Plotly (symbolic function plotting).
 *
 * Requires math.js (window.math) for parsing and evaluating expressions.
 * Produces a Plotly figure {data, layout} from function definitions,
 * optional points and optional shaded areas.
 */

export function buildGraphFigure({
    funktionen,
    punkte = null,
    flaechen = null,
    titel = "",
    xAchse = "",
    yAchse = "",
    xMin = -5,
    xMax = 20,
    yMin = null,
    yMax = null,
}) {
    const step = 0.1;
    const xWerte = [];
    for (let x = xMin; x <= xMax; x += step) xWerte.push(x);

    const m = window.math;

    const data = funktionen.map((f) => {
        const compiled = m.parse(f.term).compile();
        const yWerte = xWerte.map((x) => {
            try {
                if (f.xmin !== undefined && x < f.xmin) return null;
                if (f.xmax !== undefined && x > f.xmax) return null;
                return compiled.evaluate({ x });
            } catch { return null; }
        });

        return {
            x: xWerte,
            y: yWerte,
            type: "scatter",
            mode: "lines",
            name: f.name,
            text: f.beschreibung || "",
            hoverinfo: "name+x+y",
        };
    });

    // Flächen (schattierte Bereiche) vor die Funktionsgraphen
    if (Array.isArray(flaechen)) {
        const flaechenDaten = flaechen.map((fl) => {
            const compiled = m.parse(fl.term).compile();
            const xVon = fl.von !== undefined ? fl.von : xMin;
            const xBis = fl.bis !== undefined ? fl.bis : xMax;
            const numPoints = Math.ceil((xBis - xVon) / step) + 1;
            const xArea = [];
            const yArea = [];
            for (let i = 0; i < numPoints; i++) {
                const x = Math.min(xVon + i * step, xBis);
                xArea.push(x);
                try { yArea.push(compiled.evaluate({ x })); }
                catch { yArea.push(null); }
            }
            return {
                x: xArea, y: yArea, type: "scatter", mode: "none",
                fill: "tozeroy", fillcolor: fl.farbe || "rgba(0,100,200,0.2)",
                line: { width: 0 }, name: fl.name || "",
                showlegend: !!fl.name, hoverinfo: "skip",
            };
        });
        data.unshift(...flaechenDaten);
    }

    // Punkte
    if (Array.isArray(punkte) && punkte.length > 0) {
        data.push({
            x: punkte.map((p) => p.x),
            y: punkte.map((p) => p.y),
            mode: "markers", showlegend: false, type: "scatter",
            name: "Punkte",
            marker: { color: "black", size: 8, symbol: "circle" },
            text: punkte.map((p) => p.text),
            hoverinfo: "text+x+y",
        });
    }

    const layout = {
        xaxis: {
            ...(xAchse ? { title: { text: xAchse, y: 0.5 } } : {}),
            range: [xMin, xMax],
        },
        yaxis: {
            ...(yAchse ? { title: { text: yAchse, y: 0.5 } } : {}),
            ...(yMin != null || yMax != null
                ? { range: [yMin ?? null, yMax ?? null] }
                : {}),
        },
        hovermode: "closest",
        legend: { orientation: "h", x: 0.5, xanchor: "center", y: -0.25 },
        margin: { t: 40, r: 50, b: 40, l: 60 },
    };

    return { data, layout };
}
