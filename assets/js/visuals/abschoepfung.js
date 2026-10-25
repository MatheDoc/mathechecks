/**
 * Figure builders for the "Abschöpfung der Konsumentenrente" widget
 * (Marktgleichgewicht – Vertiefung, Preisdifferenzierung).
 *
 * On a sub-market the price p2 = pN(x2) > pG is charged. The consumers with
 * willingness to pay ≥ p2 (quantity x2) pay p2, the remaining ones up to xG
 * pay pG. The skimmed amount is the rectangle A(x2) = x2 · (pN(x2) − pG).
 *  - berechneMarkt: equilibrium (xG, pG) and maximum of A on [0; xG]
 *  - buildAbschoepfungMarktFigure: quantity-price diagram with pN, pA,
 *    KR2, KR1, hatched skimmed rectangle and helper lines x2/p2, xG/pG
 *  - buildAbschoepfungZielFigure: target function A(x2) with current point
 *    and optional maximum
 *
 * Requires math.js (window.math) for parsing the terms (variable x).
 * No DOM access apart from theme colors, no Plotly call.
 */

import { themeTextColor, themeBorderColor } from "./plotly-defaults.js?v=20260507-plotly-hover-name-theme";

const FARBE_NACHFRAGE = "#1f77b4";
const FARBE_ANGEBOT = "#d62728";
const FARBE_KR2 = "rgba(59,130,246,0.25)";
const FARBE_KR1 = "rgba(16,185,129,0.25)";
const FARBE_ABSCHOEPFUNG = "rgba(120,120,120,0.6)";
const FARBE_ZIEL = "#7f7f7f";
const FARBE_MAXIMUM = "#ff7f0e";
const PLOT_PUNKTE = 400;

const compileCache = new Map();

/** Compiles a term in the variable x to a JS function (NaN on errors). */
export function compileTerm(term) {
    const key = String(term);
    if (compileCache.has(key)) return compileCache.get(key);
    const compiled = window.math.parse(key).compile();
    const f = (x) => {
        try {
            const y = Number(compiled.evaluate({ x }));
            return Number.isFinite(y) ? y : NaN;
        } catch {
            return NaN;
        }
    };
    compileCache.set(key, f);
    return f;
}

/** Bisection for a sign change of g on [a; b]. */
function bisektion(g, a, b) {
    let ga = g(a);
    for (let i = 0; i < 100; i++) {
        const m = (a + b) / 2;
        const gm = g(m);
        if (!Number.isFinite(gm)) break;
        if ((ga <= 0 && gm <= 0) || (ga > 0 && gm > 0)) {
            a = m;
            ga = gm;
        } else {
            b = m;
        }
        if (b - a < 1e-12) break;
    }
    return (a + b) / 2;
}

/** Golden-section search for the maximum of a unimodal f on [a; b]. */
function goldenerSchnittMax(f, a, b) {
    const r = (Math.sqrt(5) - 1) / 2;
    let c = b - r * (b - a);
    let d = a + r * (b - a);
    for (let i = 0; i < 120 && b - a > 1e-10; i++) {
        if (f(c) > f(d)) b = d;
        else a = c;
        c = b - r * (b - a);
        d = a + r * (b - a);
    }
    return (a + b) / 2;
}

/**
 * Equilibrium (first intersection of pN and pA on [0; xSuche]) and maximum
 * of A(x2) = x2 · (pN(x2) − pG) on [0; xG].
 * @returns {{ xG:number, pG:number, xMax:number, pMax:number, aMax:number } | null}
 */
export function berechneMarkt({ termN, termA, xSuche = 100 }) {
    const pN = compileTerm(termN);
    const pA = compileTerm(termA);
    const d = (x) => pN(x) - pA(x);
    const schritte = 2000;
    let xG = NaN;
    let xAlt = 0;
    let dAlt = d(0);
    for (let i = 1; i <= schritte; i++) {
        const x = (xSuche * i) / schritte;
        const dx = d(x);
        if (Number.isFinite(dAlt) && Number.isFinite(dx) && (dAlt === 0 || dAlt * dx < 0)) {
            xG = dAlt === 0 ? xAlt : bisektion(d, xAlt, x);
            break;
        }
        xAlt = x;
        dAlt = dx;
    }
    if (!Number.isFinite(xG) || xG <= 0) return null;
    const pG = pN(xG);
    const a = (x) => x * (pN(x) - pG);

    // Grobe Rasterung, dann Feinsuche um das beste Rasterintervall
    const n = 400;
    let iBest = 0;
    for (let i = 1; i <= n; i++) {
        if (a((xG * i) / n) > a((xG * iBest) / n)) iBest = i;
    }
    const xMax = goldenerSchnittMax(a, (xG * Math.max(iBest - 1, 0)) / n, (xG * Math.min(iBest + 1, n)) / n);
    return { xG, pG, xMax, pMax: pN(xMax), aMax: a(xMax) };
}

/** Values for the current x2. */
export function berechneAbschoepfung({ termN, x2, pG }) {
    const p2 = compileTerm(termN)(x2);
    return { x2, p2, betrag: x2 * (p2 - pG) };
}

function stuetzstellen(von, bis, anzahl) {
    const xs = [];
    for (let i = 0; i <= anzahl; i++) xs.push(von + ((bis - von) * i) / anzahl);
    return xs;
}

function titelLayout(titel) {
    return titel
        ? { title: { text: titel, x: 0.5, xanchor: "center", font: { color: themeTextColor(), size: 16 } } }
        : {};
}

/** Closed polygon between curve f and constant level on [von; bis]. */
function flaecheZwischen(f, level, von, bis) {
    const anzahl = Math.max(2, Math.round(Math.abs(bis - von) * 10));
    const xs = stuetzstellen(von, bis, anzahl);
    const ys = xs.map(f);
    return { x: [...xs, bis, von, von], y: [...ys, level, level, ys[0]] };
}

/**
 * Helper lines from both axes to (x, y). Labels sit just inside the plot
 * area next to the axes so they never collide with the tick labels.
 */
function hilfslinien(punkte) {
    const linie = { color: themeBorderColor(), dash: "dot", width: 1.5 };
    const shapes = [];
    const annotations = [];
    const schrift = { color: themeTextColor(), size: 13 };
    punkte.forEach((h) => {
        shapes.push(
            { type: "line", x0: h.x, x1: h.x, y0: 0, y1: h.y, line: linie },
            { type: "line", x0: 0, x1: h.x, y0: h.y, y1: h.y, line: linie }
        );
        if (h.xLabel) {
            annotations.push({
                x: h.x, y: 0, xref: "x", yref: "y", yanchor: "bottom", yshift: 2,
                xanchor: h.xAnchor || "left", xshift: h.xAnchor === "right" ? -3 : 3,
                text: h.xLabel, showarrow: false, font: schrift,
            });
        }
        if (h.yLabel) {
            annotations.push({
                x: 0, y: h.y, xref: "x", yref: "y", xanchor: "left", xshift: 4,
                yanchor: h.yAnchor || "bottom", yshift: h.yAnchor === "top" ? -1 : 1,
                text: h.yLabel, showarrow: false, font: schrift,
            });
        }
    });
    return { shapes, annotations };
}

export function buildAbschoepfungMarktFigure({
    termN,
    termA,
    x2,
    xG,
    pG,
    xMax = 40,
    yMax = 42,
    einheitX = "ME",
    einheitP = "GE/ME",
    titel = "",
    xAchse = "",
    yAchse = "",
}) {
    const pN = compileTerm(termN);
    const pA = compileTerm(termA);
    const p2 = pN(x2);

    const xs = stuetzstellen(0, xMax, PLOT_PUNKTE);
    // Kurven nicht unter p = 0 zeichnen
    const kurve = (f) => xs.map((x) => {
        const y = f(x);
        return Number.isFinite(y) && y >= 0 ? y : null;
    });

    const kr2 = flaecheZwischen(pN, p2, 0, x2);
    const kr1 = flaecheZwischen(pN, pG, x2, xG);

    const flaeche = (poly, name, fill) => ({
        ...poly,
        type: "scatter",
        mode: "lines",
        fill: "toself",
        ...fill,
        line: { width: 0, color: "rgba(0,0,0,0)" },
        name,
        hoverinfo: "skip",
    });

    const data = [
        flaeche(kr2, "KR2", { fillcolor: FARBE_KR2 }),
        flaeche(kr1, "KR1", { fillcolor: FARBE_KR1 }),
        flaeche(
            { x: [0, x2, x2, 0, 0], y: [pG, pG, p2, p2, pG] },
            "abgeschöpfter Betrag",
            {
                fillcolor: "rgba(0,0,0,0)",
                fillpattern: { shape: "/", fgcolor: FARBE_ABSCHOEPFUNG, bgcolor: "rgba(0,0,0,0)", size: 6, solidity: 0.4 },
            }
        ),
        {
            x: xs,
            y: kurve(pN),
            type: "scatter",
            mode: "lines",
            name: "p<sub>N</sub>(x)",
            line: { width: 2.5, color: FARBE_NACHFRAGE },
            hovertemplate: `x = %{x:.2f} ${einheitX}<br>p<sub>N</sub>(x) = %{y:.2f} ${einheitP}<extra></extra>`,
        },
        {
            x: xs,
            y: kurve(pA),
            type: "scatter",
            mode: "lines",
            name: "p<sub>A</sub>(x)",
            line: { width: 2.5, color: FARBE_ANGEBOT },
            hovertemplate: `x = %{x:.2f} ${einheitX}<br>p<sub>A</sub>(x) = %{y:.2f} ${einheitP}<extra></extra>`,
        },
        {
            x: [x2],
            y: [p2],
            type: "scatter",
            mode: "markers",
            showlegend: false,
            name: "Teilmarkt",
            marker: { color: themeTextColor(), size: 8, line: { color: "white", width: 1 } },
            hovertemplate: `x<sub>2</sub> = %{x:.2f} ${einheitX}<br>p<sub>2</sub> = %{y:.2f} ${einheitP}<extra></extra>`,
            cliponaxis: false,
        },
    ];

    // x2 links, xG rechts der jeweiligen Hilfslinie; p2 oberhalb, pG unterhalb
    // ihrer Linie – so überlappen die Beschriftungen auch bei x2 ≈ xG nicht.
    const { shapes, annotations } = hilfslinien([
        { x: x2, y: p2, xLabel: "x<sub>2</sub>", yLabel: "p<sub>2</sub>", xAnchor: "right", yAnchor: "bottom" },
        { x: xG, y: pG, xLabel: "x<sub>G</sub>", yLabel: "p<sub>G</sub>", xAnchor: "left", yAnchor: "top" },
    ]);

    const layout = {
        ...titelLayout(titel),
        separators: ",.",
        xaxis: {
            ...(xAchse ? { title: { text: xAchse } } : {}),
            range: [0, xMax],
            layer: "below traces",
        },
        yaxis: {
            ...(yAchse ? { title: { text: yAchse } } : {}),
            range: [0, yMax],
            layer: "below traces",
        },
        hovermode: "closest",
        showlegend: true,
        legend: { orientation: "h", x: 0.5, xanchor: "center", y: -0.28 },
        margin: { t: titel ? 50 : 20, r: 20, b: 60, l: 70 },
        shapes,
        annotations,
    };

    return { data, layout };
}

export function buildAbschoepfungZielFigure({
    termN,
    x2,
    xG,
    pG,
    maximum = null,
    einheitX = "ME",
    einheitA = "GE",
    titel = "",
    xAchse = "",
    yAchse = "",
}) {
    const pN = compileTerm(termN);
    const a = (x) => x * (pN(x) - pG);
    const xs = stuetzstellen(0, xG, PLOT_PUNKTE);
    const ys = xs.map(a);
    const aAktuell = a(x2);
    const endlich = ys.filter(Number.isFinite);
    const yObergrenze = Math.max(1, ...endlich, maximum ? maximum.aMax : 0) * 1.18;
    const textFarbe = themeTextColor();

    const data = [
        {
            x: xs,
            y: ys.map((y) => (Number.isFinite(y) ? y : null)),
            type: "scatter",
            mode: "lines",
            name: "A(x<sub>2</sub>)",
            line: { width: 2.5, color: FARBE_ZIEL },
            hovertemplate: `x<sub>2</sub> = %{x:.2f} ${einheitX}<br>A(x<sub>2</sub>) = %{y:.2f} ${einheitA}<extra></extra>`,
        },
        {
            x: [x2],
            y: [aAktuell],
            type: "scatter",
            mode: "markers",
            name: "aktuelles x<sub>2</sub>",
            marker: { color: textFarbe, size: 10, line: { color: "white", width: 1 } },
            hovertemplate: `x<sub>2</sub> = %{x:.2f} ${einheitX}<br>A = %{y:.2f} ${einheitA}<extra></extra>`,
            cliponaxis: false,
        },
    ];

    const linie = { color: themeBorderColor(), dash: "dot", width: 1.5 };
    const shapes = [
        { type: "line", x0: x2, x1: x2, y0: 0, y1: aAktuell, line: linie },
    ];
    const annotations = [];

    if (maximum) {
        data.push({
            x: [maximum.xMax],
            y: [maximum.aMax],
            type: "scatter",
            mode: "markers",
            name: "Maximum",
            marker: { color: FARBE_MAXIMUM, size: 12, symbol: "diamond", line: { color: "white", width: 1 } },
            hovertemplate: `Maximum<br>x<sub>2</sub> = %{x:.2f} ${einheitX}<br>A = %{y:.2f} ${einheitA}<extra></extra>`,
            cliponaxis: false,
        });
        const fmt = (n) => n.toLocaleString("de-DE", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        annotations.push({
            x: maximum.xMax,
            y: maximum.aMax,
            xref: "x",
            yref: "y",
            yanchor: "bottom",
            yshift: 10,
            text: `Hochpunkt (${fmt(maximum.xMax)} | ${fmt(maximum.aMax)})`,
            showarrow: false,
            font: { color: textFarbe, size: 12 },
        });
    }

    const layout = {
        ...titelLayout(titel),
        separators: ",.",
        xaxis: {
            ...(xAchse ? { title: { text: xAchse } } : {}),
            range: [0, xG],
            layer: "below traces",
        },
        yaxis: {
            ...(yAchse ? { title: { text: yAchse } } : {}),
            range: [0, yObergrenze],
            layer: "below traces",
        },
        hovermode: "closest",
        showlegend: true,
        legend: { orientation: "h", x: 0.5, xanchor: "center", y: -0.28 },
        margin: { t: titel ? 50 : 20, r: 20, b: 60, l: 70 },
        shapes,
        annotations,
    };

    return { data, layout };
}
