/**
 * Allgemeiner Baumdiagramm-Builder für Plotly.
 *
 * Zeichnet Bäume mit beliebiger Verzweigung und unterschiedlich langen Pfaden.
 * Genutzt für die Baumwahl (`tree-choice`, nur Labels) und für Skript/Beispiele
 * (Include `baumdiagramm-allgemein.html`, optional mit Werten).
 *
 * Eingabe (wie `Baum.to_spec()` im Python-Generator):
 *   { children: [{ label: "B", children: [{ label: "R" }, { label: "V" }] }, { label: "Z" }] }
 * Optional je Knoten: `kante` (Text am Ast zu diesem Knoten), `ende` (Text am Pfadende).
 *
 * Kurzschreibweise (parseBaumKurzform): `B[0,4](R[0,8|0,32] V[0,2|0,08]) Z[0,25]`
 *   [kante] oder [kante|ende]; `[|ende]` nur Pfadende.
 *
 * Optionen:
 *   maxTiefe  – Stufenzahl für die x-Skalierung; bei mehreren Bäumen nebeneinander
 *               gleich setzen, damit gleiche Stufen übereinander liegen.
 *   zeilen    – Anzahl der Zeilen (Blätter) für die Höhe; bei mehreren Bäumen gleich setzen.
 *   breite    – verfügbare Breite in px; Knoten und Schrift werden bei schmalen
 *               Containern (Handy) kleiner, damit sich die Kreise nicht berühren.
 */

const ZEILENHOEHE = 34;

export function baumTiefe(knoten) {
    const kinder = Array.isArray(knoten?.children) ? knoten.children : [];
    return kinder.length ? 1 + Math.max(...kinder.map(baumTiefe)) : 0;
}

export function baumBlaetter(knoten) {
    const kinder = Array.isArray(knoten?.children) ? knoten.children : [];
    return kinder.length ? kinder.reduce((s, k) => s + baumBlaetter(k), 0) : 1;
}

/** Liest die Kurzschreibweise in das verschachtelte Format. */
export function parseBaumKurzform(text) {
    const wurzel = { children: [] };
    const stack = [wurzel];
    let letzter = null;
    const re = /\s*(?:(\()|(\))|([^\s()[\]]+)(?:\[([^\]]*)\])?)/gy;
    let m;
    const quelle = String(text ?? "").trim();
    while (re.lastIndex < quelle.length && (m = re.exec(quelle))) {
        if (m[1]) {
            if (!letzter) break;
            letzter.children = letzter.children || [];
            stack.push(letzter);
        } else if (m[2]) {
            stack.pop();
            if (!stack.length) break;
        } else {
            const knoten = { label: m[3] };
            if (m[4] != null) {
                const [kante, ende] = m[4].split("|");
                if (kante && kante.trim()) knoten.kante = kante.trim();
                if (ende && ende.trim()) knoten.ende = ende.trim();
            }
            stack[stack.length - 1].children.push(knoten);
            letzter = knoten;
        }
    }
    return wurzel;
}

function hatWerte(k) {
    if (k?.kante || k?.ende) return true;
    return (Array.isArray(k?.children) ? k.children : []).some(hatWerte);
}

function hatEnden(k) {
    if (k?.ende) return true;
    return (Array.isArray(k?.children) ? k.children : []).some(hatEnden);
}

export function buildAllgemeinerBaumFigure(baum, opts = {}) {
    const tiefe = Math.max(1, opts.maxTiefe ?? baumTiefe(baum));
    const blaetter = Math.max(1, baumBlaetter(baum));
    const zeilen = Math.max(blaetter, opts.zeilen ?? blaetter);

    const knoten = [];
    const kanten = [];
    let blattIndex = 0;
    // Bäume mit weniger Blättern vertikal zentrieren
    const versatz = (zeilen - blaetter) / 2;

    function platziere(k, stufe) {
        const idx = knoten.length;
        knoten.push({ label: String(k?.label ?? ""), stufe, zeile: 0, kante: k?.kante, ende: k?.ende });
        const kinder = Array.isArray(k?.children) ? k.children : [];
        if (!kinder.length) {
            knoten[idx].zeile = versatz + blattIndex;
            blattIndex += 1;
        } else {
            const zeilenKinder = kinder.map((kind) => {
                const ci = platziere(kind, stufe + 1);
                kanten.push([idx, ci]);
                return knoten[ci].zeile;
            });
            knoten[idx].zeile = (Math.min(...zeilenKinder) + Math.max(...zeilenKinder)) / 2;
        }
        return idx;
    }
    platziere(baum, 0);

    // Knotengröße an den Stufenabstand anpassen (schmal: kleiner)
    const breite = Number(opts.breite) > 0 ? Number(opts.breite) : 260;
    const stufenAbstand = (breite - 28) / (tiefe + 0.16);
    const mitWerten = hatWerte(baum);
    const knotenGroesse = Math.max(18, Math.min(mitWerten ? 30 : 28, stufenAbstand * 0.5));
    const schrift = Math.round(knotenGroesse * 0.54);
    const zeilenHoehe = mitWerten ? 46 : Math.max(26, Math.min(ZEILENHOEHE, knotenGroesse + 6));
    const xMax = hatEnden(baum) ? 1.32 : 1.1;

    const x = (n) => n.stufe / tiefe;
    const y = (n) => 1 - (n.zeile + 0.5) / zeilen;

    const shapes = kanten.map(([von, nach]) => ({
        type: "line",
        x0: x(knoten[von]),
        y0: y(knoten[von]),
        x1: x(knoten[nach]),
        y1: y(knoten[nach]),
        line: { width: 2, color: "gray" },
        layer: "below",
    }));

    // Werte an Ästen und an Pfadenden: am untersten Ast eines Knotens unter der Linie,
    // sonst darüber (wie im Standard-Baumdiagramm)
    const annotations = [];
    const unterster = new Map();
    kanten.forEach(([von, nach]) => {
        const bisher = unterster.get(von);
        if (bisher == null || y(knoten[nach]) < y(knoten[bisher])) unterster.set(von, nach);
    });
    kanten.forEach(([von, nach]) => {
        const text = knoten[nach].kante;
        if (!text) return;
        const hoch = unterster.get(von) !== nach || y(knoten[nach]) >= y(knoten[von]);
        annotations.push({
            x: (x(knoten[von]) + x(knoten[nach])) / 2,
            y: (y(knoten[von]) + y(knoten[nach])) / 2,
            text,
            showarrow: false,
            yshift: hoch ? 11 : -11,
            font: { size: 14 },
        });
    });
    knoten.forEach((n) => {
        if (!n.ende) return;
        annotations.push({
            x: x(n),
            y: y(n),
            text: n.ende,
            showarrow: false,
            xanchor: "left",
            xshift: knotenGroesse / 2 + 10,
            font: { size: 14 },
        });
    });

    const sichtbar = knoten.slice(1);
    const trace = {
        x: sichtbar.map(x),
        y: sichtbar.map(y),
        text: sichtbar.map((n) => n.label),
        mode: "markers+text",
        type: "scatter",
        textposition: "middle center",
        textfont: { size: schrift, color: "#1a1a2e" },
        marker: {
            size: knotenGroesse,
            color: "#b3e0ff",
            opacity: 1,
            line: { width: 2, color: "gray" },
            symbol: "circle",
        },
        hoverinfo: "none",
        cliponaxis: false,
    };

    const layout = {
        xaxis: { visible: false, range: [-0.06, xMax], fixedrange: true },
        yaxis: { visible: false, range: [0, 1], fixedrange: true },
        shapes,
        annotations,
        margin: { l: 14, r: 14, t: 8, b: 8 },
        height: 16 + zeilenHoehe * zeilen,
        showlegend: false,
        dragmode: false,
    };

    return { data: [trace], layout };
}

/** Lesbare Kurzform für KI-Kontexte, z. B. "B(R V) F(H K) Z". */
export function baumKurzform(knoten) {
    const kinder = Array.isArray(knoten?.children) ? knoten.children : [];
    return kinder
        .map((k) => {
            const unter = baumKurzform(k);
            return unter ? `${k.label}(${unter})` : String(k.label ?? "");
        })
        .join(" ");
}

/** KI-Kontext für die Baumwahl: jeder Baum in Kurzform, z. B. "Baum A: B(R V) F(H K) Z". */
export function treeChoiceKontext(spec) {
    const optionen = Array.isArray(spec?.options) ? spec.options : [];
    const labels = Array.isArray(spec?.labels) ? spec.labels : [];
    const zeilen = optionen.map(
        (baum, i) => `  Baum ${labels[i] ?? String.fromCharCode(65 + i)}: ${baumKurzform(baum)}`,
    );
    return [
        "Baumwahl (Kurzform: Label, in Klammern die Verzweigung danach):",
        ...zeilen,
    ].join("\n");
}
