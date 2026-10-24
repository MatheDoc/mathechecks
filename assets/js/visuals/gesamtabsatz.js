/**
 * Figure builders for the "Gesamtabsatz" widget (Produktlebenszyklus).
 *
 * Shows that the area under a sales rate a(t) (e.g. ME/Monat) on [t1; t2]
 * equals the total sales in that period:
 *  - buildGesamtabsatzFigure: graph of a, shaded area on [t1; t2],
 *    optional unit bars (midpoint height) and optional average rectangle
 *  - buildKumuliertFigure: cumulative function A(t) = ∫_0^t a(s) ds with
 *    the difference A(t2) − A(t1) marked at t = t2
 *
 * Requires math.js (window.math) for parsing the term (variable t).
 * No DOM access apart from theme colors, no Plotly call.
 */

import { themeTextColor, themeBorderColor } from "./plotly-defaults.js?v=20260507-plotly-hover-name-theme";

const FARBE_GRAPH = "#4363d8";
const FARBE_FLAECHE = "rgba(67, 99, 216, 0.28)";
const FARBE_BALKEN = "#f58231";
const FARBE_BALKEN_FILL = "rgba(245, 130, 49, 0.32)";
const FARBE_SCHNITT = "#3cb44b";
const SIMPSON_N = 400;
const PLOT_PUNKTE = 600;

const compileCache = new Map();

/** Compiles a term in the variable t to a JS function (NaN on errors). */
export function compileRate(term) {
    const key = String(term);
    if (compileCache.has(key)) return compileCache.get(key);
    const compiled = window.math.parse(key).compile();
    const f = (t) => {
        try {
            const y = Number(compiled.evaluate({ t }));
            return Number.isFinite(y) ? y : NaN;
        } catch {
            return NaN;
        }
    };
    compileCache.set(key, f);
    return f;
}

/** Composite Simpson rule on [a; b] with n (even) subintervals. */
export function simpson(f, a, b, n = SIMPSON_N) {
    if (b === a) return 0;
    const m = n % 2 === 0 ? n : n + 1;
    const h = (b - a) / m;
    let sum = f(a) + f(b);
    for (let i = 1; i < m; i++) sum += (i % 2 === 1 ? 4 : 2) * f(a + i * h);
    return (sum * h) / 3;
}

/** Monthly bars on [k; k+1] ⊂ [t1; t2] with midpoint height a(k + 0.5). */
function balkenListe(f, t1, t2) {
    const eps = 1e-9;
    const balken = [];
    for (let k = t1; k + 1 <= t2 + eps; k += 1) {
        balken.push({ von: k, bis: k + 1, mitte: k + 0.5, hoehe: f(k + 0.5) });
    }
    return balken;
}

/**
 * Computes all numbers the widget needs.
 * @returns {{ gesamt:number, balken:object[], balkenSumme:number, durchschnitt:number, at1:number, at2:number }}
 */
export function berechneGesamtabsatz({ term, t1, t2 }) {
    const f = compileRate(term);
    const gesamt = simpson(f, t1, t2);
    const balken = balkenListe(f, t1, t2);
    const balkenSumme = balken.reduce((s, b) => s + b.hoehe * (b.bis - b.von), 0);
    const durchschnitt = t2 > t1 ? gesamt / (t2 - t1) : NaN;
    const at1 = simpson(f, 0, t1);
    const at2 = simpson(f, 0, t2);
    return { gesamt, balken, balkenSumme, durchschnitt, at1, at2 };
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

/** Name of the cumulative function: a → A, otherwise "A". */
export function kumuliertName(fname = "a") {
    return fname.length === 1 && fname !== fname.toUpperCase() ? fname.toUpperCase() : "A";
}

export function buildGesamtabsatzFigure({
    term,
    tmax = 30,
    t1 = 0,
    t2 = 6,
    zeigeBalken = false,
    zeigeDurchschnitt = false,
    fname = "a",
    einheitY = "ME/Monat",
    einheitFlaeche = "ME",
    zeiteinheit = "Monat",
    balkenName = "Monatsbalken",
    titel = "",
    xAchse = "",
    yAchse = "",
}) {
    const f = compileRate(term);
    const werte = berechneGesamtabsatz({ term, t1, t2 });

    const xs = stuetzstellen(0, tmax, PLOT_PUNKTE);
    const ys = xs.map(f);
    const endlich = ys.filter(Number.isFinite);
    const yMaxWert = Math.max(0, ...endlich);
    const yMinWert = Math.min(0, ...endlich);

    const anzFlaeche = Math.max(20, Math.round(((t2 - t1) / Math.max(tmax, 1e-9)) * PLOT_PUNKTE));
    const xf = stuetzstellen(t1, t2, anzFlaeche);

    const data = [
        {
            x: xf,
            y: xf.map(f),
            type: "scatter",
            mode: "lines",
            fill: "tozeroy",
            fillcolor: FARBE_FLAECHE,
            line: { width: 0, color: "rgba(0,0,0,0)" },
            name: "Fläche = Gesamtabsatz",
            hoverinfo: "skip",
        },
    ];

    if (zeigeBalken && werte.balken.length) {
        data.push({
            x: werte.balken.map((b) => b.mitte),
            y: werte.balken.map((b) => b.hoehe),
            width: werte.balken.map((b) => b.bis - b.von),
            type: "bar",
            name: balkenName,
            marker: { color: FARBE_BALKEN_FILL, line: { color: FARBE_BALKEN, width: 1.5 } },
            customdata: werte.balken.map((b) => b.bis),
            hovertemplate: `%{customdata}. ${zeiteinheit}: %{y:.2f} ${einheitFlaeche}<extra></extra>`,
        });
    }

    if (zeigeDurchschnitt && Number.isFinite(werte.durchschnitt)) {
        const d = werte.durchschnitt;
        data.push({
            x: [t1, t1, t2, t2],
            y: [0, d, d, 0],
            type: "scatter",
            mode: "lines",
            name: "Durchschnitt",
            line: { color: FARBE_SCHNITT, width: 2.5, dash: "dash" },
            hovertemplate: `Durchschnitt: %{y:.2f} ${einheitY}<extra></extra>`,
        });
    }

    data.push({
        x: xs,
        y: ys.map((y) => (Number.isFinite(y) ? y : null)),
        type: "scatter",
        mode: "lines",
        name: `${fname}(t)`,
        line: { width: 2.5, color: FARBE_GRAPH },
        hovertemplate: `t = %{x:.2f}<br>${fname}(t) = %{y:.2f} ${einheitY}<extra></extra>`,
    });

    const layout = {
        ...titelLayout(titel),
        separators: ",.",
        barmode: "overlay",
        xaxis: {
            ...(xAchse ? { title: { text: xAchse } } : {}),
            range: [0, tmax],
            layer: "below traces",
        },
        yaxis: {
            ...(yAchse ? { title: { text: yAchse } } : {}),
            range: [yMinWert < 0 ? 1.1 * yMinWert : 0, yMaxWert > 0 ? 1.1 * yMaxWert : 1],
            layer: "below traces",
        },
        hovermode: "closest",
        showlegend: true,
        legend: { orientation: "h", x: 0.5, xanchor: "center", y: -0.25 },
        margin: { t: titel ? 50 : 20, r: 20, b: 50, l: 60 },
    };

    return { data, layout };
}

export function buildKumuliertFigure({
    term,
    tmax = 30,
    t1 = 0,
    t2 = 6,
    fname = "a",
    einheitFlaeche = "ME",
    titel = "",
    xAchse = "",
    yAchse = "",
}) {
    const f = compileRate(term);
    const { at1, at2, gesamt } = berechneGesamtabsatz({ term, t1, t2 });
    const name = kumuliertName(fname);

    // Kumulierte Werte: Simpson pro Teilintervall (Mittelpunktregel-genau)
    const xs = stuetzstellen(0, tmax, PLOT_PUNKTE);
    const ys = [0];
    for (let i = 1; i < xs.length; i++) {
        ys.push(ys[i - 1] + simpson(f, xs[i - 1], xs[i], 2));
    }
    const endlich = ys.filter(Number.isFinite);
    const yMaxWert = Math.max(0, at2, ...endlich);
    const yMinWert = Math.min(0, ...endlich);

    const textFarbe = themeTextColor();
    const hilfsLinie = { color: themeBorderColor(), dash: "dot", width: 1 };

    const data = [
        {
            x: xs,
            y: ys.map((y) => (Number.isFinite(y) ? y : null)),
            type: "scatter",
            mode: "lines",
            name: `${name}(t)`,
            line: { width: 2.5, color: FARBE_GRAPH },
            hovertemplate: `t = %{x:.2f}<br>${name}(t) = %{y:.2f} ${einheitFlaeche}<extra></extra>`,
        },
        {
            // Differenz A(t2) − A(t1) als vertikale Strecke bei t = t2
            x: [t2, t2],
            y: [at1, at2],
            type: "scatter",
            mode: "lines+markers",
            name: `${name}(t\u2082) \u2212 ${name}(t\u2081) = Gesamtabsatz`,
            line: { width: 5, color: "rgba(67, 99, 216, 0.55)" },
            marker: { symbol: ["triangle-down", "triangle-up"], size: 9, color: "rgba(67, 99, 216, 0.85)" },
            hoverinfo: "skip",
        },
        {
            x: [t1, t2],
            y: [at1, at2],
            type: "scatter",
            mode: "markers",
            showlegend: false,
            name: "Punkte",
            marker: { color: textFarbe, size: 8, line: { color: "white", width: 1 } },
            customdata: [`${name}(t\u2081)`, `${name}(t\u2082)`],
            hovertemplate: `%{customdata} = %{y:.2f} ${einheitFlaeche}<extra></extra>`,
            cliponaxis: false,
        },
    ];

    const shapes = [
        // Hilfslinien zu den Achsen
        { type: "line", x0: t1, x1: t1, y0: 0, y1: at1, line: hilfsLinie },
        { type: "line", x0: t2, x1: t2, y0: 0, y1: at1, line: hilfsLinie },
        { type: "line", x0: 0, x1: t1, y0: at1, y1: at1, line: hilfsLinie },
        { type: "line", x0: 0, x1: t2, y0: at2, y1: at2, line: hilfsLinie },
        // Waagerechte Hilfslinie von A(t1) bis t2 (Basis der Differenz)
        { type: "line", x0: t1, x1: t2, y0: at1, y1: at1, line: { color: FARBE_GRAPH, dash: "dash", width: 1.5 } },
    ];

    const fmt = (n) => n.toLocaleString("de-DE", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    const rechtsVonT2 = t2 < 0.7 * tmax;
    const annotations = [
        {
            x: t2,
            y: (at1 + at2) / 2,
            xref: "x",
            yref: "y",
            xanchor: rechtsVonT2 ? "left" : "right",
            xshift: rechtsVonT2 ? 8 : -8,
            text: `${name}(t<sub>2</sub>) \u2212 ${name}(t<sub>1</sub>)<br>\u2248 ${fmt(gesamt)} ${einheitFlaeche}`,
            showarrow: false,
            align: rechtsVonT2 ? "left" : "right",
            font: { color: textFarbe, size: 12 },
        },
    ];

    const layout = {
        ...titelLayout(titel),
        separators: ",.",
        xaxis: {
            ...(xAchse ? { title: { text: xAchse } } : {}),
            range: [0, tmax],
            layer: "below traces",
        },
        yaxis: {
            title: { text: yAchse || `Kumulierter Absatz ${name}(t) in ${einheitFlaeche}` },
            range: [yMinWert < 0 ? 1.1 * yMinWert : 0, yMaxWert > 0 ? 1.1 * yMaxWert : 1],
            layer: "below traces",
        },
        hovermode: "closest",
        showlegend: true,
        legend: { orientation: "h", x: 0.5, xanchor: "center", y: -0.25 },
        margin: { t: titel ? 50 : 20, r: 20, b: 50, l: 60 },
        shapes,
        annotations,
    };

    return { data, layout };
}
