/**
 * Tilgungsplan bei Annuitätentilgung: zeilenweise auf Cent gerundet,
 * gerundete Werte werden weiterverwendet (Repo-Konvention Finanzmathematik).
 */

function rund2(value) {
    // kaufmännisch runden, Gleitkomma-Artefakte vorher glätten
    return Math.round((value + Number.EPSILON) * 100) / 100;
}

export function berechneAnnuitaet(k0, p, n) {
    const q = 1 + p / 100;
    return (k0 * Math.pow(q, n) * (q - 1)) / (Math.pow(q, n) - 1);
}

export function berechneTilgungsplan({ k0, p, n }) {
    const a = rund2(berechneAnnuitaet(k0, p, n));
    const zeilen = [];
    let rk = rund2(k0);
    for (let jahr = 1; jahr <= n; jahr += 1) {
        const zinsen = rund2(rk * p / 100);
        let tilgung;
        let annuitaet;
        if (jahr === n) {
            tilgung = rk;
            annuitaet = rund2(zinsen + tilgung);
        } else {
            tilgung = rund2(a - zinsen);
            annuitaet = a;
        }
        const rkEnde = rund2(rk - tilgung);
        zeilen.push({ jahr, rkAnfang: rk, zinsen, tilgung, annuitaet, rkEnde });
        rk = rkEnde;
    }
    return { annuitaet: a, zeilen, rundungsdifferenz: rund2(zeilen[zeilen.length - 1].annuitaet - a) };
}

export function buildTilgungsplanFigure(plan, { zinsColor = "#f472b6", tilgungColor = "#7c6aff" } = {}) {
    const jahre = plan.zeilen.map((z) => z.jahr);
    return {
        data: [
            {
                type: "bar",
                name: "Zinsen",
                x: jahre,
                y: plan.zeilen.map((z) => z.zinsen),
                marker: { color: zinsColor, opacity: 0.55 },
                hovertemplate: "Jahr %{x}<br>Zinsen: %{y:,.2f} €<extra></extra>",
            },
            {
                type: "bar",
                name: "Tilgung",
                x: jahre,
                y: plan.zeilen.map((z) => z.tilgung),
                marker: { color: tilgungColor, opacity: 0.75 },
                hovertemplate: "Jahr %{x}<br>Tilgung: %{y:,.2f} €<extra></extra>",
            },
        ],
        layout: {
            barmode: "stack",
            height: 320,
            margin: { l: 60, r: 10, t: 10, b: 40 },
            xaxis: { title: "Jahr", dtick: 1 },
            yaxis: { title: "€", separatethousands: true },
            legend: { orientation: "h", y: 1.12 },
            separators: ",.",
        },
    };
}
