import { buildBaumdiagrammFigure } from "../visuals/baumdiagramm.js";
import { buildBaumdiagrammBinomialFigure } from "../visuals/baumdiagramm-binomial.js";
import { buildHistogrammEinzelnFigure, buildHistogrammKumuliertFigure, binomialIntervalProbability } from "../visuals/histogramm.js";
import { buildHistogrammAllgemeinFigure } from "../visuals/histogramm-allgemein.js";
import { buildGraphFigure } from "../visuals/graph.js";
import { buildVerflechtungsdiagrammFigure } from "../visuals/verflechtungsdiagramm.js";
import { plotlyRender, themeTextColor } from "../visuals/plotly-defaults.js";

function parseNum(raw) {
    if (raw == null || raw === "") return null;
    return parseFloat(String(raw).replace(",", "."));
}

function parseSlots(raw) {
    if (raw == null || String(raw).trim() === "") return [];

    const text = String(raw).trim();

    if (text.startsWith("[") && text.endsWith("]")) {
        try {
            const parsed = JSON.parse(text);
            if (Array.isArray(parsed)) {
                return parsed
                    .map(Number)
                    .filter((n) => Number.isInteger(n) && n >= 1 && n <= 10);
            }
        } catch {
            // Fall back to separator-based parsing below.
        }
    }

    return text
        .replace(/[{}\[\]]/g, "")
        .split(/[\s,;]+/)
        .map(Number)
        .filter((n) => Number.isInteger(n) && n >= 1 && n <= 10);
}

function ensureEqualColumns(table) {
    if (!table) return;

    const hasManualColgroup = Array.from(table.children).some(
        (c) => c.tagName === "COLGROUP"
    );
    if (hasManualColgroup) return;

    const firstRow = table.querySelector("tr");
    if (!firstRow) return;

    const cols = [...firstRow.children].reduce((sum, cell) => {
        const colspan = parseInt(cell.getAttribute("colspan") || "1", 10);
        return sum + (Number.isFinite(colspan) && colspan > 0 ? colspan : 1);
    }, 0);

    if (cols < 1) return;

    const cg = document.createElement("colgroup");
    for (let i = 0; i < cols; i++) {
        cg.appendChild(document.createElement("col"));
    }
    table.insertBefore(cg, table.firstChild);
}

function wrapTablesForHorizontalScroll(root) {
    if (!root) return;

    root.querySelectorAll("table").forEach((table) => {
        ensureEqualColumns(table);

        if (table.parentElement.classList.contains("table-scroll")) return;
        if (table.closest(".skript-widget")) return;  // widget tables have own layout

        const wrapper = document.createElement("div");
        wrapper.classList.add("table-scroll");
        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);
    });
}

export function initSkriptVisuals(root) {
    if (!root) return;

    // Keep table semantics intact and move horizontal scrolling to the wrapper.
    wrapTablesForHorizontalScroll(root);

    if (!window.Plotly) return;

    /* ---- Baumdiagramme ---- */
    const divs = root.querySelectorAll(".baumdiagramm-auto");
    divs.forEach((div) => {
        const opts = {
            pa: parseFloat(div.dataset.pa),
            pba: parseFloat(div.dataset.pba),
            pbna: parseFloat(div.dataset.pbna),
            titel: div.dataset.titel || "",
            labelA: div.dataset.labelA || "A",
            labelAbar: div.dataset.labelAbar || "A\u0305",
            labelB: div.dataset.labelB || "B",
            labelBbar: div.dataset.labelBbar || "B\u0305",
            mode: div.dataset.mode || "numeric",
            givenSlots: parseSlots(div.dataset.givenSlots),
        };

        const figure = buildBaumdiagrammFigure(opts);
        plotlyRender(div, figure.data, figure.layout);
    });

    /* ---- Graphen (symbolische Funktionen) ---- */
    root.querySelectorAll(".graph-auto").forEach((div) => {
        if (!window.math) return;
        let funktionen;
        try { funktionen = JSON.parse(div.dataset.funktionen); } catch { return; }
        const punkte = div.dataset.punkte ? JSON.parse(div.dataset.punkte) : null;
        const flaechen = div.dataset.flaechen ? JSON.parse(div.dataset.flaechen) : null;

        const figure = buildGraphFigure({
            funktionen,
            punkte,
            flaechen,
            titel: div.dataset.titel || "",
            xAchse: div.dataset.xachse || "",
            yAchse: div.dataset.yachse || "",
            xMin: div.dataset.xmin !== "" ? Number(div.dataset.xmin) : -5,
            xMax: div.dataset.xmax !== "" ? Number(div.dataset.xmax) : 20,
            yMin: div.dataset.ymin !== "" ? Number(div.dataset.ymin) : null,
            yMax: div.dataset.ymax !== "" ? Number(div.dataset.ymax) : null,
        });

        plotlyRender(div, figure.data, figure.layout);
    });

    /* ---- Histogramme (allgemein, frei definierte x/y) ---- */
    root.querySelectorAll(".histogramm-allgemein-auto").forEach((div) => {
        let x, y;
        try { x = JSON.parse(div.dataset.x); y = JSON.parse(div.dataset.y); } catch { return; }
        const titel = div.dataset.titel || "";
        const balkenbreite = div.dataset.balkenbreite !== "" ? Number(div.dataset.balkenbreite) : null;

        const figure = buildHistogrammAllgemeinFigure({ x, y, titel, balkenbreite });
        plotlyRender(div, figure.data, figure.layout);
    });

    /* ---- Histogramme (Einzelwahrscheinlichkeiten) ---- */
    root.querySelectorAll(".histogramm-einzel-auto").forEach((div) => {
        const n = parseNum(div.dataset.n);
        const p = parseNum(div.dataset.p);
        if (n == null || p == null) return;
        const a = parseNum(div.dataset.a);
        const b = parseNum(div.dataset.b);
        const titel = div.dataset.titel || "";

        const figure = buildHistogrammEinzelnFigure({ n, p, a, b, titel });
        plotlyRender(div, figure.data, figure.layout);
    });

    /* ---- Histogramme (Kumuliert) ---- */
    root.querySelectorAll(".histogramm-kumuliert-auto").forEach((div) => {
        const n = parseNum(div.dataset.n);
        const p = parseNum(div.dataset.p);
        if (n == null || p == null) return;
        const a = parseNum(div.dataset.a);
        const b = parseNum(div.dataset.b);
        const titel = div.dataset.titel || "";

        const figure = buildHistogrammKumuliertFigure({ n, p, a, b, titel });
        plotlyRender(div, figure.data, figure.layout);
    });

    /* ---- Verflechtungsdiagramme ---- */
    root.querySelectorAll(".verflechtungsdiagramm-auto").forEach((div) => {
        let rohstoffe, zwischenprodukte, endprodukte, stufe1, stufe2;
        try {
            rohstoffe = JSON.parse(div.dataset.rohstoffe);
            zwischenprodukte = JSON.parse(div.dataset.zwischenprodukte);
            endprodukte = JSON.parse(div.dataset.endprodukte);
            stufe1 = JSON.parse(div.dataset.stufe1);
            stufe2 = JSON.parse(div.dataset.stufe2);
        } catch { return; }

        const figure = buildVerflechtungsdiagrammFigure({
            rohstoffe, zwischenprodukte, endprodukte, stufe1, stufe2,
        });
        plotlyRender(div, figure.data, figure.layout);
    });

    /* ---- Interaktive Histogramm-Widgets ---- */
    root.querySelectorAll(".hb-widget").forEach((row) => {
        const nSlider = row.querySelector(".hb-nSlider");
        if (!nSlider) return;
        const pSlider = row.querySelector(".hb-pSlider");
        const aSlider = row.querySelector(".hb-aSlider");
        const bSlider = row.querySelector(".hb-bSlider");
        const nWert = row.querySelector(".hb-nWert");
        const pWert = row.querySelector(".hb-pWert");
        const aWert = row.querySelector(".hb-aWert");
        const bWert = row.querySelector(".hb-bWert");
        const autoYBox = row.querySelector(".hb-autoY");
        const intervallEl = row.querySelector(".hb-intervallWert");
        const plotEinzeln = row.querySelector(".hb-plotEinzeln");
        const plotKumuliert = row.querySelector(".hb-plotKumuliert");

        function updateSliderRanges() {
            const n = parseInt(nSlider.value);
            aSlider.max = n;
            bSlider.max = n;
            if (parseInt(aSlider.value) > n) aSlider.value = n;
            if (parseInt(bSlider.value) > n) bSlider.value = n;
        }

        function update() {
            const n = parseInt(nSlider.value);
            const p = parseFloat(pSlider.value);
            const a = parseInt(aSlider.value);
            const b = parseInt(bSlider.value);
            const autoY = autoYBox.checked;

            nWert.textContent = n;
            pWert.textContent = p.toFixed(2).replace(".", ",");
            aWert.textContent = a;
            bWert.textContent = b;

            const figE = buildHistogrammEinzelnFigure({
                n, p, a, b, titel: "Einzelwahrscheinlichkeiten", autoY,
            });

            if (intervallEl) {
                const pIntervall = binomialIntervalProbability(n, p, a, b);
                intervallEl.innerHTML = `$ P(${a} ≤ X ≤ ${b}) = ${pIntervall.toFixed(4)} $`;
                if (window.MathJax?.typesetPromise) MathJax.typesetPromise([intervallEl]);
            }

            plotlyRender(plotEinzeln, figE.data, figE.layout);

            const figK = buildHistogrammKumuliertFigure({
                n, p, a, b, titel: "Kumulierte Wahrscheinlichkeiten",
            });
            plotlyRender(plotKumuliert, figK.data, figK.layout);
        }

        nSlider.addEventListener("input", () => { updateSliderRanges(); update(); });
        pSlider.addEventListener("input", update);
        aSlider.addEventListener("input", update);
        bSlider.addEventListener("input", update);
        autoYBox.addEventListener("change", update);

        updateSliderRanges();
        update();
    });

    /* ---- Lineare Funktionen Explorer ---- */
    root.querySelectorAll(".lf-widget").forEach((row) => {
        const mSlider = row.querySelector(".lf-mSlider");
        if (!mSlider) return;
        if (!window.math) return;
        const bSlider = row.querySelector(".lf-bSlider");
        const mWert = row.querySelector(".lf-mWert");
        const bWert = row.querySelector(".lf-bWert");
        const eqDisplay = row.querySelector(".lf-eqDisplay");
        const plotDiv = row.querySelector(".lf-plotGraph");
        const tableBody = row.querySelector(".lf-tableBody");

        function fmt(n) {
            const r = Math.round(n * 10) / 10;
            return r % 1 === 0 ? String(r) : r.toFixed(1);
        }

        function fmtDe(n) {
            return fmt(n).replace(".", ",");
        }

        function update() {
            const m = parseFloat(mSlider.value);
            const b = parseFloat(bSlider.value);

            mWert.textContent = fmtDe(m);
            bWert.textContent = fmtDe(b);

            // Equation (LaTeX)
            const bAbs = Math.abs(b);
            const sign = b >= 0 ? "+" : "-";
            eqDisplay.innerHTML = "$ f(x) = " + fmtDe(m) + " \\cdot x " + sign + " " + fmtDe(bAbs) + " $";
            if (window.MathJax?.typesetPromise) MathJax.typesetPromise([eqDisplay]);

            // Graph via buildGraphFigure (identical rendering to dev/graph.html)
            const xMin = -6, xMax = 6, yMin = -8, yMax = 8;
            const term = "(" + m + ")*x+(" + b + ")";
            const figure = buildGraphFigure({
                funktionen: [{ name: "f", term: term }],
                punkte: [{ x: 0, y: b, text: "y-Achsenabschnitt (0 | " + fmtDe(b) + ")" }],
                xMin, xMax, yMin, yMax,
            });

            // Fixed axis scaling with integer ticks
            figure.layout.xaxis.dtick = 1;
            figure.layout.yaxis.dtick = 1;

            // Steigungsdreieck (slope triangle) at x = 1
            const x0 = 1, y0 = m * x0 + b, y1 = m * (x0 + 1) + b;
            const dimColor = themeTextColor() + "80";   // 50 % opacity
            figure.layout.shapes = [];
            if (m !== 0 && y0 >= yMin && y0 <= yMax && y1 >= yMin && y1 <= yMax) {
                // horizontal leg: (x0, y0) → (x0+1, y0)
                figure.layout.shapes.push({
                    type: "line", x0: x0, y0: y0, x1: x0 + 1, y1: y0,
                    line: { color: dimColor, width: 1.5, dash: "dot" },
                });
                // vertical leg: (x0+1, y0) → (x0+1, y1)
                figure.layout.shapes.push({
                    type: "line", x0: x0 + 1, y0: y0, x1: x0 + 1, y1: y1,
                    line: { color: dimColor, width: 1.5, dash: "dot" },
                });
                // annotations: "1" on horizontal, "m" on vertical
                figure.layout.annotations = [
                    {
                        x: x0 + 0.5, y: y0, yshift: m > 0 ? -14 : 14,
                        text: "1", showarrow: false,
                        font: { size: 12, color: dimColor },
                    },
                    {
                        x: x0 + 1, xshift: 14, y: (y0 + y1) / 2,
                        text: fmtDe(m), showarrow: false,
                        font: { size: 12, color: dimColor },
                    },
                ];
            } else {
                figure.layout.annotations = [];
            }

            plotlyRender(plotDiv, figure.data, figure.layout);

            // Value table
            const xs = [-3, -2, -1, 0, 1, 2, 3];
            let html = "";
            for (const x of xs) {
                const y = m * x + b;
                if (x === 0) {
                    html += "<tr><td><strong>" + fmtDe(x) + "</strong></td><td><strong>" + fmtDe(y) + "</strong></td></tr>";
                } else {
                    html += "<tr><td>" + fmtDe(x) + "</td><td>" + fmtDe(y) + "</td></tr>";
                }
            }
            tableBody.innerHTML = html;
        }

        mSlider.addEventListener("input", update);
        bSlider.addEventListener("input", update);
        update();
    });

    /* ---- Baumdiagramme und Vierfeldertafeln (interaktiv) ---- */
    root.querySelectorAll(".bvt-widget").forEach((row) => {
        const paSlider = row.querySelector(".bvt-paSlider");
        if (!paSlider) return;
        const pbaSlider = row.querySelector(".bvt-pbaSlider");
        const pbnaSlider = row.querySelector(".bvt-pbnaSlider");
        const paWert = row.querySelector(".bvt-paWert");
        const pbaWert = row.querySelector(".bvt-pbaWert");
        const pbnaWert = row.querySelector(".bvt-pbnaWert");
        const unabh = row.querySelector(".bvt-unabhaengigkeit");
        const plotBaum = row.querySelector(".bvt-plotBaum");
        const plotInvers = row.querySelector(".bvt-plotInvers");

        // Vierfeldertafel cells
        const c = (cls) => row.querySelector(`.bvt-${cls}`);

        function fmtDe(v, d) { return v.toFixed(d).replace(".", ","); }

        function update() {
            const pa = parseFloat(paSlider.value);
            const pba = parseFloat(pbaSlider.value);
            const pbna = parseFloat(pbnaSlider.value);

            paWert.textContent = fmtDe(pa, 2);
            pbaWert.textContent = fmtDe(pba, 2);
            pbnaWert.textContent = fmtDe(pbna, 2);

            // Baumdiagramm
            const figBaum = buildBaumdiagrammFigure({
                pa, pba, pbna,
                titel: "Baumdiagramm",
                labelA: "A", labelAbar: "A\u0305",
                labelB: "B", labelBbar: "B\u0305",
            });
            plotlyRender(plotBaum, figBaum.data, figBaum.layout);

            // Inverses Baumdiagramm
            const pb = pa * pba + (1 - pa) * pbna;
            const pab = pb > 0 ? (pa * pba) / pb : 0;
            const panb = (1 - pb) > 0 ? (pa * (1 - pba)) / (1 - pb) : 0;
            const figInvers = buildBaumdiagrammFigure({
                pa: pb, pba: pab, pbna: panb,
                titel: "Inverses Baumdiagramm",
                labelA: "B", labelAbar: "B\u0305",
                labelB: "A", labelBbar: "A\u0305",
            });
            plotlyRender(plotInvers, figInvers.data, figInvers.layout);

            // Vierfeldertafel
            const a_b = pa * pba;
            const a_nb = pa * (1 - pba);
            const na_b = (1 - pa) * pbna;
            const na_nb = (1 - pa) * (1 - pbna);

            c("ab").textContent = fmtDe(a_b, 4);
            c("anb").textContent = fmtDe(a_nb, 4);
            c("nab").textContent = fmtDe(na_b, 4);
            c("nanb").textContent = fmtDe(na_nb, 4);
            c("asum").textContent = fmtDe(a_b + a_nb, 2);
            c("nasum").textContent = fmtDe(na_b + na_nb, 2);
            c("sumb").textContent = fmtDe(a_b + na_b, 2);
            c("sumnb").textContent = fmtDe(a_nb + na_nb, 2);
            c("sumsum").textContent = "1";

            // Unabhängigkeit
            unabh.textContent = Math.abs(pba - pbna) < 1e-6 ? "unabhängig." : "abhängig.";
        }

        paSlider.addEventListener("input", update);
        pbaSlider.addEventListener("input", update);
        pbnaSlider.addEventListener("input", update);
        update();
    });

    /* ---- Baumdiagramm Binomial / Bernoulli-Formel (interaktiv) ---- */
    root.querySelectorAll(".bb-widget").forEach((row) => {
        const nSlider = row.querySelector(".bb-nSlider");
        if (!nSlider) return;
        const pSlider = row.querySelector(".bb-pSlider");
        const kSlider = row.querySelector(".bb-kSlider");
        const nWert = row.querySelector(".bb-nWert");
        const pWert = row.querySelector(".bb-pWert");
        const kWert = row.querySelector(".bb-kWert");
        const anzahlPfade = row.querySelector(".bb-anzahlPfade");
        const pfadwkeit = row.querySelector(".bb-pfadwkeit");
        const bernoulli = row.querySelector(".bb-bernoulli");
        const plotBaum = row.querySelector(".bb-plotBaum");

        function binom(n, k) {
            if (k < 0 || k > n) return 0;
            let res = 1;
            for (let i = 1; i <= k; i++) res = (res * (n - i + 1)) / i;
            return res;
        }

        function update() {
            const n = parseInt(nSlider.value, 10);
            const p = parseFloat(pSlider.value);
            kSlider.max = n;
            let k = parseInt(kSlider.value, 10);
            if (k > n) { k = n; kSlider.value = n; }

            nWert.textContent = n;
            pWert.textContent = p;
            kWert.textContent = k;

            const anz = binom(n, k);
            const pw = Math.pow(p, k) * Math.pow(1 - p, n - k);
            const bern = anz * pw;

            anzahlPfade.textContent = `$ \\binom{n}{k}=  ${anz} $`;
            pfadwkeit.textContent = `$ p^${k} \\cdot (1-p)^${n - k} =  ${pw.toLocaleString(undefined, { maximumFractionDigits: 4 })}$`;
            bernoulli.textContent = `\\begin{align*} P(X=k) &= \\binom{n}{k} \\cdot p^k \\cdot (1-p)^{n-k} \\\\ &=${anz}\\cdot ${pw.toLocaleString(undefined, { maximumFractionDigits: 4 })} \\\\ &=  ${bern.toLocaleString(undefined, { maximumFractionDigits: 4 })}\\end{align*}`;

            if (window.MathJax?.typesetPromise) {
                MathJax.typesetPromise([anzahlPfade, pfadwkeit, bernoulli]);
            }

            const figure = buildBaumdiagrammBinomialFigure({ n, p, k });
            plotlyRender(plotBaum, figure.data, figure.layout);
        }

        nSlider.addEventListener("input", update);
        pSlider.addEventListener("input", update);
        kSlider.addEventListener("input", update);
        update();
    });
}
