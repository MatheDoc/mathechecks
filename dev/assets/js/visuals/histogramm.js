/**
 * Shared Histogramm (binomial distribution) builders for Plotly.
 *
 * buildHistogrammEinzelnFigure  – bar chart of P(X = k)
 * buildHistogrammKumuliertFigure – bar chart of P(X ≤ k) with optional arrows
 *
 * When a and b are provided the relevant bars are highlighted (skript mode).
 * When omitted all bars use a neutral colour (task mode).
 */

/* ------------------------------------------------------------------ */
/*  Helpers                                                            */
/* ------------------------------------------------------------------ */

function fakultaet(k) {
    if (k <= 1) return 1;
    let f = 1;
    for (let i = 2; i <= k; i++) f *= i;
    return f;
}

function binomialPmf(n, k, p) {
    return (fakultaet(n) / (fakultaet(k) * fakultaet(n - k)))
        * Math.pow(p, k) * Math.pow(1 - p, n - k);
}

function computePmf(n, p) {
    const pmf = [];
    for (let k = 0; k <= n; k++) pmf.push(binomialPmf(n, k, p));
    return pmf;
}

function computeCdf(pmf) {
    const cdf = [];
    let sum = 0;
    for (const v of pmf) { sum += v; cdf.push(sum); }
    return cdf;
}

/**
 * Return the interval probability P(a ≤ X ≤ b) for B(n,p).
 */
export function binomialIntervalProbability(n, p, a, b) {
    const cdf = computeCdf(computePmf(n, p));
    const pB = cdf[b] ?? 0;
    const pVorA = a > 0 ? cdf[a - 1] : 0;
    return a > b ? 0 : pB - pVorA;
}

/* ------------------------------------------------------------------ */
/*  Einzelwahrscheinlichkeiten  P(X = k)                              */
/* ------------------------------------------------------------------ */

export function buildHistogrammEinzelnFigure({
    n, p, a = null, b = null, titel = "", autoY = true,
}) {
    const pmf = computePmf(n, p);
    const x = Array.from({ length: n + 1 }, (_, i) => i);

    const hasRange = a != null && b != null;
    const farben = x.map((k) =>
        hasRange && k >= a && k <= b
            ? "rgba(5, 56, 166, 0.6)"
            : "rgba(54, 162, 235, 0.4)"
    );

    const data = [{
        x,
        y: pmf,
        type: "bar",
        marker: { color: farben, line: { color: "rgba(0, 0, 0, 0.5)", width: 1 } },
        name: "P(X = k)",
    }];

    const layout = {
        title: titel ? { text: titel, y: 0.85 } : undefined,
        xaxis: { title: "k", tickmode: "linear" },
        yaxis: { title: "P(X = k)", range: autoY ? undefined : [0, 1] },
        bargap: 0,
        dragmode: false,
    };

    return { data, layout };
}

/* ------------------------------------------------------------------ */
/*  Kumulierte Wahrscheinlichkeiten  P(X ≤ k)                        */
/* ------------------------------------------------------------------ */

export function buildHistogrammKumuliertFigure({
    n, p, a = null, b = null, titel = "",
}) {
    const pmf = computePmf(n, p);
    const cdf = computeCdf(pmf);
    const x = Array.from({ length: n + 1 }, (_, i) => i);

    const hasRange = a != null && b != null;
    const farben = x.map((k) => {
        if (hasRange) {
            if (k === b) return "rgba(255, 160, 160, 0.6)";
            if (k === a - 1) return "rgba(255, 160, 160, 0.6)";
        }
        return "rgba(100, 100, 100, 0.2)";
    });

    const data = [{
        x,
        y: cdf,
        type: "bar",
        marker: { color: farben, line: { color: "rgba(50, 50, 50, 0.5)", width: 1 } },
        name: "P(X ≤ k)",
    }];

    const shapes = [];
    if (hasRange && a > 0) {
        const xPfeil = a - 1;
        const yUnten = cdf[a - 1];
        const yOben = cdf[b];
        shapes.push(
            {
                type: "line", x0: xPfeil, x1: xPfeil, y0: yUnten, y1: yOben,
                line: { color: "black", width: 2, dash: "solid" }
            },
            {
                type: "path",
                path: `M ${xPfeil - 0.05} ${yOben - 0.02} L ${xPfeil} ${yOben} L ${xPfeil + 0.05} ${yOben - 0.02} Z`,
                fillcolor: "black", line: { color: "black" }
            },
            {
                type: "path",
                path: `M ${xPfeil - 0.05} ${yUnten + 0.02} L ${xPfeil} ${yUnten} L ${xPfeil + 0.05} ${yUnten + 0.02} Z`,
                fillcolor: "black", line: { color: "black" }
            },
            {
                type: "line", x0: xPfeil, x1: b, y0: yOben, y1: yOben,
                line: { color: "black", width: 2, dash: "dash" }
            },
        );
    }

    const layout = {
        title: titel ? { text: titel, y: 0.85 } : undefined,
        xaxis: { title: "k", tickmode: "linear" },
        yaxis: { title: "P(X ≤ k)", range: [0, 1.05] },
        bargap: 0,
        dragmode: false,
        shapes: shapes.length > 0 ? shapes : undefined,
    };

    return { data, layout };
}
