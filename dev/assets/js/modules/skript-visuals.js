import { buildBaumdiagrammFigure } from "../visuals/baumdiagramm.js";
import { buildHistogrammEinzelnFigure, buildHistogrammKumuliertFigure, binomialIntervalProbability } from "../visuals/histogramm.js";
import { buildGraphFigure } from "../visuals/graph.js";
import { buildVerflechtungsdiagrammFigure } from "../visuals/verflechtungsdiagramm.js";
import { plotlyRender } from "../visuals/plotly-defaults.js";

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
    root.querySelectorAll(".diagramm-row").forEach((row) => {
        const nSlider = row.querySelector(".hb-nSlider");
        if (!nSlider) return;                       // not an interactive histogramm widget
        const nInput = row.querySelector(".hb-nInput");
        const pSlider = row.querySelector(".hb-pSlider");
        const pInput = row.querySelector(".hb-pInput");
        const aSlider = row.querySelector(".hb-aSlider");
        const aInput = row.querySelector(".hb-aInput");
        const bSlider = row.querySelector(".hb-bSlider");
        const bInput = row.querySelector(".hb-bInput");
        const autoYBox = row.querySelector(".hb-autoY");
        const intervallEl = row.querySelector(".hb-intervallWert");
        const plotEinzeln = row.querySelector(".hb-plotEinzeln");
        const plotKumuliert = row.querySelector(".hb-plotKumuliert");

        function parseFraction(input) {
            input = input.replace(",", ".").replace(/\s+/g, "");
            if (input.includes("/")) {
                const parts = input.split("/");
                if (parts.length !== 2) return null;
                const num = parseFloat(parts[0]);
                const den = parseFloat(parts[1]);
                if (isNaN(num) || isNaN(den) || den === 0) return null;
                return num / den;
            }
            const value = parseFloat(input);
            return isNaN(value) ? null : value;
        }

        function updateSliderRanges() {
            const n = parseInt(nSlider.value);
            aSlider.max = n;
            bSlider.max = n;
            const aRaw = parseFraction(aInput.value);
            const bRaw = parseFraction(bInput.value);
            if (aRaw !== null && Math.ceil(aRaw) > n) { aInput.value = n; aSlider.value = n; }
            if (bRaw !== null && Math.floor(bRaw) > n) { bInput.value = n; bSlider.value = n; }
        }

        function update() {
            const n = parseInt(nSlider.value);
            const p = parseFloat(pSlider.value);
            const aRaw = parseFraction(aInput.value);
            const bRaw = parseFraction(bInput.value);
            if (aRaw === null || bRaw === null) return;
            const a = Math.ceil(aRaw);
            const b = Math.floor(bRaw);
            const autoY = autoYBox.checked;

            const figE = buildHistogrammEinzelnFigure({
                n, p, a, b, titel: "Einzelwahrscheinlichkeiten", autoY,
            });

            // Compute interval probability for display
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

        // n
        nSlider.addEventListener("input", () => { nInput.value = nSlider.value; updateSliderRanges(); update(); });
        nInput.addEventListener("input", () => {
            const v = parseFraction(nInput.value); if (v === null) return;
            const n = Math.round(v); nSlider.value = n; nInput.value = n;
            updateSliderRanges(); update();
        });
        // a
        aSlider.addEventListener("input", () => { aInput.value = aSlider.value; update(); });
        aInput.addEventListener("input", () => {
            const v = parseFraction(aInput.value); if (v === null) return;
            aSlider.value = Math.ceil(v); update();
        });
        // b
        bSlider.addEventListener("input", () => { bInput.value = bSlider.value; update(); });
        bInput.addEventListener("input", () => {
            const v = parseFraction(bInput.value); if (v === null) return;
            bSlider.value = Math.floor(v); update();
        });
        // p
        pSlider.addEventListener("input", () => { pInput.value = pSlider.value; update(); });
        pInput.addEventListener("input", () => {
            const v = parseFraction(pInput.value); if (v === null || v < 0 || v > 1) return;
            pSlider.value = v.toFixed(2); update();
        });
        // autoY
        autoYBox.addEventListener("change", update);

        updateSliderRanges();
        update();
    });

    /* ---- Lineare Funktionen Explorer ---- */
    root.querySelectorAll(".diagramm-row").forEach((row) => {
        const mSlider = row.querySelector(".lf-mSlider");
        if (!mSlider) return;
        if (!window.math) return;
        const bSlider = row.querySelector(".lf-bSlider");
        const mWert = row.querySelector(".lf-mWert");
        const bWert = row.querySelector(".lf-bWert");
        const eqDisplay = row.querySelector(".lf-eqDisplay");
        const descM = row.querySelector(".lf-descM");
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

            // Description
            if (descM) {
                if (m === 0) {
                    descM.innerHTML = "Waagerechte Gerade (keine Steigung)";
                } else {
                    descM.innerHTML = "Pro $ +1 $ in $ x $ ändert sich $ y $ um $ " + (m > 0 ? "+" : "") + fmtDe(m) + " $";
                }
                if (window.MathJax?.typesetPromise) MathJax.typesetPromise([descM]);
            }

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
            figure.layout.shapes = [];
            if (m !== 0 && y0 >= yMin && y0 <= yMax && y1 >= yMin && y1 <= yMax) {
                // horizontal leg: (x0, y0) → (x0+1, y0)
                figure.layout.shapes.push({
                    type: "line", x0: x0, y0: y0, x1: x0 + 1, y1: y0,
                    line: { color: "rgba(0,0,0,0.4)", width: 1.5, dash: "dot" },
                });
                // vertical leg: (x0+1, y0) → (x0+1, y1)
                figure.layout.shapes.push({
                    type: "line", x0: x0 + 1, y0: y0, x1: x0 + 1, y1: y1,
                    line: { color: "rgba(0,0,0,0.4)", width: 1.5, dash: "dot" },
                });
                // annotations: "1" on horizontal, "m" on vertical
                figure.layout.annotations = [
                    {
                        x: x0 + 0.5, y: y0, yshift: m > 0 ? -14 : 14,
                        text: "1", showarrow: false,
                        font: { size: 12, color: "rgba(0,0,0,0.5)" },
                    },
                    {
                        x: x0 + 1, xshift: 14, y: (y0 + y1) / 2,
                        text: fmtDe(m), showarrow: false,
                        font: { size: 12, color: "rgba(0,0,0,0.5)" },
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
}
