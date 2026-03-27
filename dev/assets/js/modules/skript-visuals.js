import { buildBaumdiagrammFigure } from "../visuals/baumdiagramm.js";
import { buildHistogrammEinzelnFigure, buildHistogrammKumuliertFigure, binomialIntervalProbability } from "../visuals/histogramm.js";
import { buildGraphFigure } from "../visuals/graph.js";

const PLOTLY_CONFIG = {
    scrollZoom: false,
    staticPlot: false,
    displayModeBar: false,
    doubleClick: false,
    responsive: true,
};

function parseNum(raw) {
    if (raw == null || raw === "") return null;
    return parseFloat(String(raw).replace(",", "."));
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
        };

        const figure = buildBaumdiagrammFigure(opts);
        window.Plotly.newPlot(div, figure.data, figure.layout, PLOTLY_CONFIG);
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

        const graphConfig = { ...PLOTLY_CONFIG, displayModeBar: true, displaylogo: false };
        window.Plotly.newPlot(div, figure.data, figure.layout, graphConfig);
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
        window.Plotly.newPlot(div, figure.data, figure.layout, PLOTLY_CONFIG);
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
        window.Plotly.newPlot(div, figure.data, figure.layout, PLOTLY_CONFIG);
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

            window.Plotly.newPlot(plotEinzeln, figE.data, figE.layout, PLOTLY_CONFIG);

            const figK = buildHistogrammKumuliertFigure({
                n, p, a, b, titel: "Kumulierte Wahrscheinlichkeiten",
            });
            window.Plotly.newPlot(plotKumuliert, figK.data, figK.layout, PLOTLY_CONFIG);
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
}
