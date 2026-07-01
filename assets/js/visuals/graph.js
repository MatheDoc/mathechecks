/**
 * Shared graph builder for Plotly (symbolic function plotting).
 *
 * Requires math.js (window.math) for parsing and evaluating expressions.
 * Produces a Plotly figure {data, layout} from function definitions,
 * optional points and optional shaded areas.
 */

import { themeTextColor, themeBorderColor } from "./plotly-defaults.js?v=20260507-plotly-hover-name-theme";

export function buildGraphFigure({
    funktionen,
    punkte = null,
    flaechen = null,
    hilfslinien = null,
    titel = "",
    xAchse = "",
    yAchse = "",
    xMin = -5,
    xMax = 20,
    yMin = null,
    yMax = null,
}) {
    const step = 0.1;
    const eps = 1e-9;
    const xWerte = [];
    for (let x = xMin; x <= xMax; x += step) xWerte.push(x);

    const m = window.math;

    const data = funktionen.map((f) => {
        const compiled = m.parse(f.term).compile();
        const yWerte = xWerte.map((x) => {
            try {
                if (f.xmin !== undefined && x < Number(f.xmin) - eps) return null;
                if (f.xmax !== undefined && x > Number(f.xmax) + eps) return null;
                const xEval = Math.abs(x) < eps ? 0 : x;
                return compiled.evaluate({ x: xEval });
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
            ...(f.color ? { line: { color: f.color } } : {}),
        };
    });

    // Flächen (schattierte Bereiche) vor die Funktionsgraphen
    if (Array.isArray(flaechen)) {
        const flaechenDaten = [];
        flaechen.forEach((fl) => {
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

            // Schraffur statt Volltonfarbe (z.B. für nicht mehr eindeutig
            // zugeordnete Flächen wie den abgeschöpften Betrag).
            const fillStyle = fl.schraffur
                ? {
                    fillpattern: {
                        shape: "/",
                        fgcolor: fl.farbe || "rgba(120,120,120,0.6)",
                        bgcolor: "rgba(0,0,0,0)",
                        size: 6,
                        solidity: 0.4,
                    },
                }
                : { fillcolor: fl.farbe || "rgba(0,100,200,0.2)" };

            // Optionale Basislinie: schattiert den Bereich zwischen `term` und
            // `basis` (Konstante oder eigener Term) statt zwischen `term` und 0.
            // Beide Traces benötigen mode:"lines" (nicht "none"), damit Plotly
            // beim Berechnen von fill:"tonexty" eine Referenzlinie findet.
            if (fl.basis !== undefined) {
                const basisCompiled = typeof fl.basis === "string" ? m.parse(fl.basis).compile() : null;
                const yBasis = xArea.map((x) => {
                    try { return basisCompiled ? basisCompiled.evaluate({ x }) : Number(fl.basis); }
                    catch { return null; }
                });
                flaechenDaten.push({
                    x: xArea, y: yBasis, type: "scatter", mode: "lines",
                    line: { width: 0, color: "rgba(0,0,0,0)" }, showlegend: false, hoverinfo: "skip",
                });
                flaechenDaten.push({
                    x: xArea, y: yArea, type: "scatter", mode: "lines",
                    fill: "tonexty", ...fillStyle,
                    line: { width: 0, color: "rgba(0,0,0,0)" }, name: fl.name || "",
                    showlegend: !!fl.name, hoverinfo: "skip",
                });
            } else {
                flaechenDaten.push({
                    x: xArea, y: yArea, type: "scatter", mode: "none",
                    fill: "tozeroy", ...fillStyle,
                    line: { width: 0 }, name: fl.name || "",
                    showlegend: !!fl.name, hoverinfo: "skip",
                });
            }
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
            marker: { color: themeTextColor(), size: 8, symbol: "circle", line: { color: "white", width: 1 } },
            text: punkte.map((p) => p.text),
            hoverinfo: "text+x+y",
            cliponaxis: false,
        });
    }

    // Hilfslinien: gestrichelte Linien von den Achsen zu einem Punkt
    // (z. B. x_2/x_G, p_2/p_G), mit Beschriftung direkt auf der Achse statt
    // einem Punktmarker im Diagramm – orientiert an der Aufgaben-Visualisierung.
    const helperShapes = [];
    const helperAnnotations = [];
    if (Array.isArray(hilfslinien)) {
        hilfslinien.forEach((h) => {
            const lineStyle = { color: themeBorderColor(), dash: "dot", width: 1 };
            helperShapes.push(
                { type: "line", x0: h.x, x1: h.x, y0: 0, y1: h.y, line: lineStyle },
                { type: "line", x0: 0, x1: h.x, y0: h.y, y1: h.y, line: lineStyle }
            );
            if (h.xLabel) {
                helperAnnotations.push({
                    x: h.x, y: 0, xref: "x", yref: "paper", yanchor: "top", yshift: -6,
                    text: h.xLabel, showarrow: false, font: { color: themeTextColor() },
                });
            }
            if (h.yLabel) {
                helperAnnotations.push({
                    x: 0, y: h.y, xref: "paper", yref: "y", xanchor: "right", xshift: -6,
                    text: h.yLabel, showarrow: false, font: { color: themeTextColor() },
                });
            }
        });
    }

    const layout = {
        ...(titel
            ? {
                title: {
                    text: titel,
                    x: 0.5,
                    xanchor: "center",
                    font: { color: themeTextColor(), size: 16 },
                },
            }
            : {}),
        xaxis: {
            ...(xAchse ? { title: { text: xAchse, y: 0.5 } } : {}),
            range: [xMin, xMax],
            layer: "below traces",
        },
        yaxis: {
            ...(yAchse ? { title: { text: yAchse, y: 0.5 } } : {}),
            ...(yMin != null || yMax != null
                ? { range: [yMin ?? null, yMax ?? null] }
                : {}),
            layer: "below traces",
        },
        hovermode: "closest",
        legend: { orientation: "h", x: 0.5, xanchor: "center", y: -0.25 },
        margin: { t: titel ? 60 : 40, r: 50, b: 40, l: 60 },
        ...(helperShapes.length ? { shapes: helperShapes } : {}),
        ...(helperAnnotations.length ? { annotations: helperAnnotations } : {}),
    };

    return { data, layout };
}
