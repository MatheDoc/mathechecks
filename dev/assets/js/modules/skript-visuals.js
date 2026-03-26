import { buildBaumdiagrammFigure } from "../visuals/baumdiagramm.js";
import { buildHistogrammEinzelnFigure, buildHistogrammKumuliertFigure, binomialIntervalProbability } from "../visuals/histogramm.js";

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

export function initSkriptVisuals(root) {
    if (!root || !window.Plotly) return;

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
