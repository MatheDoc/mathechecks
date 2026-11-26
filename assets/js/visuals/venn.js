/**
 * Venn-Diagramm mit zwei Ereignissen A und B in einer Ergebnismenge (Rechteck).
 *
 * Die Ergebnismenge zerfällt in vier Teilflächen (Schlüssel):
 *   "a"  = A ∩ B̅   (nur A)
 *   "ab" = A ∩ B   (A und B)
 *   "b"  = A̅ ∩ B   (nur B)
 *   "n"  = A̅ ∩ B̅   (weder A noch B)
 *
 * Jede Kombination dieser Teilflächen ist ein Ereignis. VENN_EREIGNISSE ordnet allen
 * 16 Kombinationen ihre symbolischen Darstellungen und eine Beschreibung zu.
 * Der Python-Generator (aufgaben/generators/stochastik/methoden/venn_ohne_bedingt.py)
 * nutzt dieselben Schlüssel.
 */

import { themeTextColor } from "./plotly-defaults.js?v=20260507-plotly-hover-name-theme";

export const VENN_REGIONEN = ["a", "ab", "b", "n"];

const REGION_REIHENFOLGE = new Map(VENN_REGIONEN.map((key, index) => [key, index]));

/** Kanonischer Schlüssel einer Flächenauswahl, z. B. ["b", "a"] → "a,b". */
export function vennKey(regionen) {
    const unique = [...new Set((regionen || []).map((r) => String(r).trim()).filter((r) => REGION_REIHENFOLGE.has(r)))];
    unique.sort((x, y) => REGION_REIHENFOLGE.get(x) - REGION_REIHENFOLGE.get(y));
    return unique.join(",");
}

/** Akzeptiert "a,ab", ["a","ab"] oder JSON-Arrays. */
export function parseVennRegionen(raw) {
    if (Array.isArray(raw)) return vennKey(raw).split(",").filter(Boolean);
    const text = String(raw ?? "").trim();
    if (!text) return [];
    if (text.startsWith("[")) {
        try { return parseVennRegionen(JSON.parse(text)); } catch { /* Fallback unten */ }
    }
    return vennKey(text.split(/[\s,;]+/)).split(",").filter(Boolean);
}

/**
 * Symbolische Darstellungen (LaTeX, erste = Standardform) und Beschreibung je Kombination.
 * Schlüssel = vennKey der Teilflächen.
 */
export const VENN_EREIGNISSE = {
    "": {
        latex: ["P(\\emptyset)", "P(A\\cap\\overline{A})"],
        text: "unmögliches Ereignis",
    },
    "a": {
        latex: ["P(A\\cap\\overline{B})", "P(A)-P(A\\cap B)"],
        text: "\\(A\\), aber nicht \\(B\\)",
    },
    "ab": {
        latex: ["P(A\\cap B)"],
        text: "\\(A\\) und \\(B\\)",
    },
    "b": {
        latex: ["P(\\overline{A}\\cap B)", "P(B)-P(A\\cap B)"],
        text: "\\(B\\), aber nicht \\(A\\)",
    },
    "n": {
        latex: ["P(\\overline{A}\\cap\\overline{B})", "1-P(A\\cup B)"],
        text: "weder \\(A\\) noch \\(B\\)",
    },
    "a,ab": {
        latex: ["P(A)"],
        text: "\\(A\\)",
    },
    "ab,b": {
        latex: ["P(B)"],
        text: "\\(B\\)",
    },
    "a,b": {
        latex: ["P(A\\cup B)-P(A\\cap B)", "P(A\\cap\\overline{B})+P(\\overline{A}\\cap B)"],
        text: "entweder \\(A\\) oder \\(B\\), aber nicht beide",
    },
    "a,n": {
        latex: ["P(\\overline{B})", "1-P(B)"],
        text: "nicht \\(B\\)",
    },
    "b,n": {
        latex: ["P(\\overline{A})", "1-P(A)"],
        text: "nicht \\(A\\)",
    },
    "ab,n": {
        latex: ["P(A\\cap B)+P(\\overline{A}\\cap\\overline{B})"],
        text: "beide oder keines der beiden Ereignisse",
    },
    "a,ab,b": {
        latex: ["P(A\\cup B)"],
        text: "\\(A\\) oder \\(B\\) (mindestens eines)",
    },
    "a,ab,n": {
        latex: ["P(A\\cup\\overline{B})"],
        text: "\\(A\\) oder nicht \\(B\\)",
    },
    "ab,b,n": {
        latex: ["P(\\overline{A}\\cup B)"],
        text: "nicht \\(A\\) oder \\(B\\)",
    },
    "a,b,n": {
        latex: ["P(\\overline{A}\\cup\\overline{B})", "1-P(A\\cap B)"],
        text: "nicht beide, also höchstens eines",
    },
    "a,ab,b,n": {
        latex: ["P(X)=1", "P(A\\cup\\overline{A})"],
        text: "sicheres Ereignis",
    },
};

const VENN_KLARTEXT = {
    a: "A∩B̅ (nur A)", ab: "A∩B (A und B)", b: "A̅∩B (nur B)", n: "A̅∩B̅ (außerhalb von A und B)",
};

/** Textbeschreibung eines Venn-Diagramms für KI-Kontexte (Training, Feynman). */
export function vennKontext(markiert) {
    const regionen = parseVennRegionen(markiert);
    const teil = regionen.length > 0
        ? regionen.map((r) => VENN_KLARTEXT[r]).join(", ")
        : "keine";
    return `Venn-Diagramm: Ereignisse A und B in der Ergebnismenge X. Markierte Teilflächen: ${teil}.`;
}

/* ---------- Geometrie ---------- */

const BREITE = 10;
const HOEHE = 6;
const RADIUS = 2.2;
const ABSTAND = 1.1; // halber Mittelpunktsabstand
const MITTE_A = { x: BREITE / 2 - ABSTAND, y: HOEHE / 2 };
const MITTE_B = { x: BREITE / 2 + ABSTAND, y: HOEHE / 2 };
const T = Math.atan2(Math.sqrt(RADIUS ** 2 - ABSTAND ** 2), ABSTAND); // Winkel der Schnittpunkte bzgl. A

function bogen(mitte, von, bis, schritte = 48) {
    const pts = [];
    for (let i = 0; i <= schritte; i += 1) {
        const w = von + ((bis - von) * i) / schritte;
        pts.push([mitte.x + RADIUS * Math.cos(w), mitte.y + RADIUS * Math.sin(w)]);
    }
    return pts;
}

function kreis(mitte) {
    return bogen(mitte, 0, 2 * Math.PI, 96);
}

function polygone() {
    const PI = Math.PI;
    // Linse: rechter Bogen von A (P2 → P1), linker Bogen von B (P1 → P2)
    const ab = [...bogen(MITTE_A, -T, T), ...bogen(MITTE_B, PI - T, PI + T)];
    // nur A: großer Bogen von A (P1 → links → P2), linker Bogen von B zurück (P2 → P1)
    const a = [...bogen(MITTE_A, T, 2 * PI - T, 72), ...bogen(MITTE_B, PI + T, PI - T)];
    // nur B: großer Bogen von B (P2 → rechts → P1), rechter Bogen von A zurück (P1 → P2)
    const b = [...bogen(MITTE_B, -(PI - T), PI - T, 72), ...bogen(MITTE_A, T, -T)];
    // außen: Rechteck mit „Schlüsselloch“-Schnitt zum Rand von A ∪ B (Gegenrichtung = Loch)
    const links = [MITTE_A.x - RADIUS, HOEHE / 2];
    const n = [
        [0, HOEHE / 2], [0, 0], [BREITE, 0], [BREITE, HOEHE], [0, HOEHE], [0, HOEHE / 2],
        links,
        ...bogen(MITTE_A, PI, T, 40),
        ...bogen(MITTE_B, PI - T, -(PI - T), 72),
        ...bogen(MITTE_A, -T, -PI, 40),
        [0, HOEHE / 2],
    ];
    return { a, ab, b, n };
}

const POLYGONE = polygone();

/* ---------- Farben ---------- */

export const VENN_FARBEN = {
    markiert: "rgba(31, 119, 180, 0.72)",
    unmarkiert: "rgba(31, 119, 180, 0.10)",
    hover: "rgba(255, 159, 28, 0.55)",
};

/**
 * Figure-Builder.
 *
 * @param {object}   opts
 * @param {string[]} [opts.markiert=[]]  – markierte Teilflächen ("a", "ab", "b", "n")
 * @param {boolean}  [opts.interaktiv=false] – Teilflächen reagieren auf Hover/Klick (Skript-Widget);
 *                                            sonst kein Hover, damit Aufgaben nichts verraten
 * @param {string}   [opts.hoverRegion]  – zusätzlich hervorgehobene Teilfläche (Widget)
 * @param {string}   [opts.labelA="A"], [opts.labelB="B"], [opts.labelX="X"]
 * @param {string}   [opts.titel=""]
 * @param {number}   [opts.hoehe=280]
 * @returns {{data: object[], layout: object}}
 */
export function buildVennFigure({
    markiert = [],
    interaktiv = false,
    hoverRegion = null,
    labelA = "A",
    labelB = "B",
    labelX = "X",
    titel = "",
    hoehe = 280,
} = {}) {
    const auswahl = new Set(parseVennRegionen(markiert));

    const flaechen = VENN_REGIONEN.map((key) => {
        const pts = POLYGONE[key];
        let fillcolor = auswahl.has(key) ? VENN_FARBEN.markiert : VENN_FARBEN.unmarkiert;
        if (hoverRegion === key) fillcolor = VENN_FARBEN.hover;
        return {
            type: "scatter",
            mode: "lines",
            x: pts.map((p) => p[0]),
            y: pts.map((p) => p[1]),
            fill: "toself",
            fillcolor,
            line: { width: 0 },
            name: key,
            showlegend: false,
            hoveron: "fills",
            hoverinfo: interaktiv ? "none" : "skip",
        };
    });

    // Umrisse in Textfarbe: bleiben auf markierten und unmarkierten Flächen sichtbar (hell/dunkel)
    const linie = { color: typeof document !== "undefined" ? themeTextColor() : "#1a1a2e", width: 2 };
    const outline = (pts) => ({
        type: "scatter",
        mode: "lines",
        x: pts.map((p) => p[0]),
        y: pts.map((p) => p[1]),
        line: linie,
        hoverinfo: "skip",
        showlegend: false,
    });

    const data = [
        ...flaechen,
        outline([[0, 0], [BREITE, 0], [BREITE, HOEHE], [0, HOEHE], [0, 0]]),
        outline(kreis(MITTE_A)),
        outline(kreis(MITTE_B)),
    ];

    const schrift = { size: 22 };
    const annotations = [
        { x: MITTE_A.x - 2.0, y: HOEHE / 2 + 1.9, text: labelA, showarrow: false, font: schrift },
        { x: MITTE_B.x + 2.0, y: HOEHE / 2 + 1.9, text: labelB, showarrow: false, font: schrift },
        { x: 0.45, y: HOEHE - 0.5, text: labelX, showarrow: false, font: schrift },
    ];

    const achse = {
        visible: false,
        showgrid: false,
        zeroline: false,
        fixedrange: true,
    };

    const layout = {
        height: hoehe,
        margin: { l: 6, r: 6, t: titel ? 36 : 6, b: 6 },
        showlegend: false,
        hovermode: interaktiv ? "closest" : false,
        xaxis: { ...achse, range: [-0.05, BREITE + 0.05] },
        yaxis: { ...achse, range: [-0.05, HOEHE + 0.05], scaleanchor: "x", scaleratio: 1 },
        annotations,
    };
    if (titel) layout.title = { text: titel, x: 0.5 };

    return { data, layout };
}

/** Index der Flächen-Traces in data (gleiche Reihenfolge wie VENN_REGIONEN). */
export function vennRegionAusTrace(curveNumber) {
    return VENN_REGIONEN[curveNumber] ?? null;
}
