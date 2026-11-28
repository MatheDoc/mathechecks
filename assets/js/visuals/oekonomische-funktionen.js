/**
 * Figure builder and calculations for the widget "Ökonomische Funktionen"
 * (Lernbereich ganzrationale ökonomische Funktionen).
 *
 * Cubic cost function K(x) = k3·x³ + k2·x² + k1·x + kf and either
 *  - Angebotspolypol: p(x) = preis (constant), E(x) = preis·x, domain [0; kapazitaet]
 *  - Angebotsmonopol: p(x) = pH − (pH/sm)·x, E(x) = p(x)·x, domain [0; sm]
 * G(x) = E(x) − K(x).
 *
 *  - berechneOekonomie: functions and Kennzahlen (x_w, x_GS, x_GG, x_Gmax,
 *    G_max, E_max, …) on the economic domain
 *  - buildOekonomieFigure: p, E, K, G with optional Gewinnzone, Kennzahlen
 *    markers and the distance E(x) − K(x) at a chosen quantity x
 *
 * No DOM access apart from theme colors, no Plotly call.
 */

import { themeTextColor, themeBorderColor } from "./plotly-defaults.js?v=20261127-theme-live-switch";

// Einheitliche Farben im Lernbereich (wie die Trainingsdiagramme): E grün, K rot, G blau, p orange.
// Grenzgrößen tragen die Farbe ihrer Ausgangsfunktion. Gewinn-Balken: blau = Gewinn, grau = Verlust.
export const OF_FARBEN = {
    E: "#2ca02c",
    K: "#d62728",
    G: "#1f77b4",
    p: "#ff7f0e",
    gewinnzone: "rgba(31,119,180,0.10)",
    abstandPlus: "rgba(31,119,180,0.8)",
    abstandMinus: "rgba(127,127,127,0.85)",
};
const PLOT_PUNKTE = 300;

function bisektion(g, a, b) {
    let ga = g(a);
    for (let i = 0; i < 100; i++) {
        const m = (a + b) / 2;
        const gm = g(m);
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

/**
 * @returns {{ marktform, p, E, K, G, Es, Ks, Gs, xEnde, kennzahlen: object }}
 */
export function berechneOekonomie({ marktform, k3, k2, k1, kf, preis, kapazitaet, pH, sm }) {
    const monopol = marktform === "monopol";
    const steigung = monopol ? pH / sm : 0;
    const e1 = monopol ? pH : preis;
    const e2 = monopol ? -steigung : 0;

    const p = (x) => (monopol ? pH - steigung * x : preis);
    const E = (x) => e2 * x * x + e1 * x;
    const K = (x) => ((k3 * x + k2) * x + k1) * x + kf;
    const G = (x) => E(x) - K(x);
    // Grenzfunktionen (Ableitungen)
    const Es = (x) => 2 * e2 * x + e1;
    const Ks = (x) => (3 * k3 * x + 2 * k2) * x + k1;
    const Gs = (x) => Es(x) - Ks(x);
    const xEnde = monopol ? sm : kapazitaet;

    // Nullstellen von G auf [0; xEnde] über Vorzeichenwechsel
    const schritte = 600;
    const nullstellen = [];
    let xAlt = 0;
    let gAlt = G(0);
    for (let i = 1; i <= schritte; i++) {
        const x = (xEnde * i) / schritte;
        let gx = G(x);
        // Rundungsrauschen um exakte Nullstellen (z. B. G(8) = 0) als 0 behandeln
        if (Math.abs(gx) < 1e-9) gx = 0;
        if (gx === 0 && gAlt !== 0) {
            nullstellen.push({ x, steigend: gAlt < 0 });
        } else if (gAlt * gx < 0) {
            nullstellen.push({ x: bisektion(G, xAlt, x), steigend: gx > gAlt });
        } else if (gAlt === 0 && gx !== 0 && nullstellen.length) {
            // Nullstelle lag genau auf dem Rasterpunkt: Richtung nachträglich bestätigen
            nullstellen[nullstellen.length - 1].steigend = gx > 0;
        }
        xAlt = x;
        gAlt = gx;
    }
    const xGS = nullstellen.find((n) => n.steigend)?.x ?? null;
    const xGG = xGS === null ? null : (nullstellen.find((n) => !n.steigend && n.x > xGS)?.x ?? null);

    // Gewinnmaximum: lokales Maximum von G (G' = 0, G'' < 0) oder Randmaximum an xEnde
    const g3 = -k3;
    const g2 = e2 - k2;
    const g1 = e1 - k1;
    const a = 3 * g3;
    const b = 2 * g2;
    const disk = b * b - 4 * a * g1;
    let xLokal = null;
    if (disk >= 0) {
        for (const x of [(-b + Math.sqrt(disk)) / (2 * a), (-b - Math.sqrt(disk)) / (2 * a)]) {
            if (x > 0 && 6 * g3 * x + 2 * g2 < 0) xLokal = x;
        }
    }
    let xGmax;
    let randmaximum = false;
    if (xLokal !== null && xLokal <= xEnde && G(xLokal) >= G(xEnde)) {
        xGmax = xLokal;
    } else {
        xGmax = xEnde;
        randmaximum = true;
    }

    const xEmax = monopol ? sm / 2 : kapazitaet;

    return {
        marktform: monopol ? "monopol" : "polypol",
        p, E, K, G, Es, Ks, Gs, xEnde,
        kennzahlen: {
            preis: monopol ? null : preis,
            kapazitaet: monopol ? null : kapazitaet,
            pH: monopol ? pH : null,
            sm: monopol ? sm : null,
            xEmax,
            eMax: E(xEmax),
            kf,
            xW: -k2 / (3 * k3),
            xGS,
            xGG,
            gewinngrenzeAmRand: xGS !== null && xGG === null,
            xGmax,
            gMax: G(xGmax),
            randmaximum,
        },
    };
}

function kurve(name, f, xEnde, farbe, extra = {}) {
    const xs = [];
    const ys = [];
    for (let i = 0; i <= PLOT_PUNKTE; i++) {
        const x = (xEnde * i) / PLOT_PUNKTE;
        xs.push(x);
        ys.push(f(x));
    }
    return {
        x: xs, y: ys, type: "scatter", mode: "lines", name,
        line: { color: farbe, width: 2.5 },
        hoverinfo: "name+x+y",
        ...extra,
    };
}

/**
 * @param {object} opts
 * @param {object} opts.werte   Ergebnis von berechneOekonomie
 * @param {number|null} opts.menge  gewählte Menge für den Abstand E − K (null: aus)
 */
export function buildOekonomieFigure({
    werte,
    menge = null,
    zeigeKennzahlen = false,
    zeigeGewinnzone = false,
    zeigeCournot = false,
    yMin = -150,
    yMax = 500,
    xAchse = "Menge x in ME",
    yAchse = "Betrag in GE",
    titel = "",
}) {
    const { p, E, K, G, xEnde, kennzahlen: kz, marktform } = werte;
    const text = themeTextColor();
    const shapes = [];
    const annotations = [];

    if (zeigeGewinnzone && kz.xGS !== null) {
        shapes.push({
            type: "rect", xref: "x", yref: "paper",
            x0: kz.xGS, x1: kz.xGG ?? xEnde, y0: 0, y1: 1,
            fillcolor: OF_FARBEN.gewinnzone, line: { width: 0 }, layer: "below",
        });
    }

    if (marktform === "polypol") {
        shapes.push({
            type: "line", xref: "x", yref: "paper", x0: xEnde, x1: xEnde, y0: 0, y1: 1,
            line: { color: themeBorderColor(), dash: "dot", width: 1.5 },
        });
        annotations.push({
            x: xEnde, y: 1, xref: "x", yref: "paper", yanchor: "bottom", xanchor: "right",
            text: "Kapazitätsgrenze", showarrow: false, font: { color: text, size: 11 },
        });
    }

    const data = [
        kurve("E(x)", E, xEnde, OF_FARBEN.E),
        kurve("K(x)", K, xEnde, OF_FARBEN.K),
        kurve("G(x)", G, xEnde, OF_FARBEN.G),
        kurve("p(x)", p, xEnde, OF_FARBEN.p),
    ];

    if (menge !== null && Number.isFinite(menge)) {
        const e = E(menge);
        const k = K(menge);
        const g = G(menge);
        const farbe = g >= 0 ? OF_FARBEN.abstandPlus : OF_FARBEN.abstandMinus;
        // Abstand zwischen Erlös und Kosten …
        shapes.push({
            type: "line", xref: "x", yref: "y", x0: menge, x1: menge, y0: k, y1: e,
            line: { color: farbe, width: 9 },
        });
        // … entspricht dem Funktionswert von G
        shapes.push({
            type: "line", xref: "x", yref: "y", x0: menge, x1: menge, y0: 0, y1: g,
            line: { color: OF_FARBEN.G, width: 1.5, dash: "dash" },
        });
        data.push({
            x: [menge, menge, menge], y: [e, k, g], type: "scatter", mode: "markers",
            marker: { color: [OF_FARBEN.E, OF_FARBEN.K, OF_FARBEN.G], size: 9, line: { color: "white", width: 1 } },
            hoverinfo: "skip", showlegend: false,
        });
    }

    if (zeigeKennzahlen) {
        const punkte = [];
        const add = (x, y, label, hover) => {
            if (x === null || !Number.isFinite(x) || !Number.isFinite(y)) return;
            punkte.push({ x, y, label, hover });
        };
        add(kz.xW, K(kz.xW), "W", "Wendepunkt von K");
        add(kz.xGS, 0, "x<sub>GS</sub>", "Gewinnschwelle");
        add(kz.xGG, 0, "x<sub>GG</sub>", "Gewinngrenze");
        add(kz.xGmax, kz.gMax, "G<sub>max</sub>", "Gewinnmaximum");
        add(kz.xEmax, kz.eMax, "E<sub>max</sub>", "Erlösmaximum");
        if (marktform === "monopol") {
            add(0, kz.pH, "p<sub>H</sub>", "Höchstpreis");
            add(kz.sm, 0, "s<sub>m</sub>", "Sättigungsmenge");
        }
        data.push({
            x: punkte.map((pt) => pt.x),
            y: punkte.map((pt) => pt.y),
            text: punkte.map((pt) => pt.label),
            hovertext: punkte.map((pt) => pt.hover),
            type: "scatter", mode: "markers+text",
            // Punkte auf der y-Achse rechts beschriften, sonst wird der Text abgeschnitten
            textposition: punkte.map((pt) => (pt.x < 1e-9 ? "middle right" : "top center")),
            textfont: { color: text, size: 12 },
            marker: { color: text, size: 8, line: { color: "white", width: 1 } },
            hoverinfo: "text+x+y", showlegend: false,
        });
    }

    // Cournotscher Punkt: gewinnmaximale Menge auf der Preis-Absatz-Funktion (nur Monopol)
    if (zeigeCournot && marktform === "monopol" && Number.isFinite(kz.xGmax)) {
        const pC = p(kz.xGmax);
        shapes.push({
            type: "line", xref: "x", yref: "y", x0: kz.xGmax, x1: kz.xGmax,
            y0: Math.min(0, kz.gMax), y1: Math.max(pC, kz.gMax),
            line: { color: OF_FARBEN.p, width: 1.5, dash: "dot" },
        });
        data.push({
            x: [kz.xGmax], y: [pC], text: ["C"], hovertext: ["Cournotscher Punkt"],
            type: "scatter", mode: "markers+text", textposition: "top right",
            textfont: { color: OF_FARBEN.p, size: 14 },
            marker: { color: OF_FARBEN.p, size: 11, symbol: "diamond", line: { color: "white", width: 1 } },
            hoverinfo: "text+x+y", showlegend: false,
        });
    }

    const layout = {
        title: titel ? { text: titel } : undefined,
        margin: { l: 55, r: 15, t: titel ? 45 : 25, b: 50 },
        xaxis: { title: { text: xAchse }, range: [0, xEnde * 1.06], zeroline: true },
        yaxis: { title: { text: yAchse }, range: [yMin, yMax], zeroline: true },
        shapes,
        annotations,
        legend: { orientation: "h", x: 0.5, xanchor: "center", y: -0.25 },
        showlegend: true,
    };

    return { data, layout };
}

/**
 * Grenzbetrachtung (GE/ME): E' und K'. Der Balken bei der
 * gewählten Menge zeigt den Grenzgewinn G'(x) = E'(x) − K'(x).
 */
export function buildGrenzFigure({
    werte,
    menge = null,
    zeigeKennzahlen = false,
    yMin = -50,
    yMax = 100,
    xAchse = "Menge x in ME",
    yAchse = "GE/ME",
    titel = "",
}) {
    const { Es, Ks, xEnde, kennzahlen: kz, marktform } = werte;
    const text = themeTextColor();
    const shapes = [];
    const data = [
        kurve("E'(x)", Es, xEnde, OF_FARBEN.E),
        kurve("K'(x)", Ks, xEnde, OF_FARBEN.K),
    ];
    if (marktform === "polypol") {
        shapes.push({
            type: "line", xref: "x", yref: "paper", x0: xEnde, x1: xEnde, y0: 0, y1: 1,
            line: { color: themeBorderColor(), dash: "dot", width: 1.5 },
        });
    }

    if (menge !== null && Number.isFinite(menge)) {
        const es = Es(menge);
        const ks = Ks(menge);
        shapes.push({
            type: "line", xref: "x", yref: "y", x0: menge, x1: menge, y0: ks, y1: es,
            line: { color: es >= ks ? OF_FARBEN.abstandPlus : OF_FARBEN.abstandMinus, width: 9 },
        });
        data.push({
            x: [menge, menge], y: [es, ks], type: "scatter", mode: "markers",
            marker: { color: [OF_FARBEN.E, OF_FARBEN.K], size: 9, line: { color: "white", width: 1 } },
            hoverinfo: "skip", showlegend: false,
        });
    }

    if (zeigeKennzahlen) {
        const punkte = [];
        const add = (x, y, label, hover) => {
            if (x === null || !Number.isFinite(x) || !Number.isFinite(y)) return;
            punkte.push({ x, y, label, hover });
        };
        add(kz.xW, Ks(kz.xW), "x<sub>w</sub>", "Tiefpunkt von K'");
        if (!kz.randmaximum) add(kz.xGmax, Ks(kz.xGmax), "x<sub>Gmax</sub>", "Schnittpunkt von E' und K'");
        if (marktform === "monopol") add(kz.xEmax, 0, "x<sub>Emax</sub>", "Nullstelle von E'");
        data.push({
            x: punkte.map((pt) => pt.x),
            y: punkte.map((pt) => pt.y),
            text: punkte.map((pt) => pt.label),
            hovertext: punkte.map((pt) => pt.hover),
            type: "scatter", mode: "markers+text", textposition: "bottom center",
            textfont: { color: text, size: 12 },
            marker: { color: text, size: 8, line: { color: "white", width: 1 } },
            hoverinfo: "text+x+y", showlegend: false,
        });
    }

    const layout = {
        title: titel ? { text: titel } : undefined,
        margin: { l: 55, r: 15, t: titel ? 45 : 25, b: 50 },
        xaxis: { title: { text: xAchse }, range: [0, xEnde * 1.06], zeroline: true },
        yaxis: { title: { text: yAchse }, range: [yMin, yMax], zeroline: true },
        shapes,
        legend: { orientation: "h", x: 0.5, xanchor: "center", y: -0.25 },
        showlegend: true,
    };
    return { data, layout };
}
