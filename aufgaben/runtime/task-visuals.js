import { buildBaumdiagrammFigure } from "../../dev/assets/js/visuals/baumdiagramm.js";
import { buildHistogrammEinzelnFigure, buildHistogrammKumuliertFigure } from "../../dev/assets/js/visuals/histogramm.js";
import { plotlyRender } from "../../dev/assets/js/visuals/plotly-defaults.js";
import { buildVerflechtungsdiagrammFigure } from "../../dev/assets/js/visuals/verflechtungsdiagramm.js";

function toNumber(value, fallback) {
    const numeric = Number(value);
    return Number.isFinite(numeric) ? numeric : fallback;
}

function buildPlotlyFigure(spec) {
    const figure = { data: [], layout: {} };
    const specType = String(spec?.type ?? "plotly").toLowerCase();

    if (specType === "economic-curves") {
        const params = typeof spec?.params === "object" && spec.params ? spec.params : {};
        const hasMonopolyRevenue = Number.isFinite(Number(params.a2)) && Number.isFinite(Number(params.a1));
        const a2 = toNumber(params.a2, -0.15);
        const a1 = toNumber(params.a1, 2.0);
        const k3 = toNumber(params.k3, 0.05);
        const k2 = toNumber(params.k2, -1.0);
        const k1 = toNumber(params.k1, 10.0);
        const k0 = toNumber(params.k0, 80.0);
        const price = toNumber(params.price, 20.0);
        const capacity = Math.max(1, toNumber(params.capacity, 40.0));
        const xMax = Math.max(1, toNumber(params.xMax, capacity));
        const showCapacityLine = params.showCapacityLine !== false;
        const points = Math.max(40, Math.trunc(toNumber(spec?.points, 300)));

        const x = [];
        const p = [];
        const e = [];
        const k = [];
        const g = [];
        for (let i = 0; i < points; i += 1) {
            const xi = (xMax * i) / (points - 1);
            const pi = hasMonopolyRevenue ? (a2 * xi + a1) : price;
            const ei = hasMonopolyRevenue ? (pi * xi) : (price * xi);
            const ki = k3 * xi ** 3 + k2 * xi ** 2 + k1 * xi + k0;
            x.push(xi);
            p.push(pi);
            e.push(ei);
            k.push(ki);
            g.push(ei - ki);
        }

        if (hasMonopolyRevenue) {
            figure.data.push({ x, y: p, mode: "lines", name: "p(x)", line: { color: "#ff7f0e" } });
        }
        figure.data.push(
            { x, y: e, mode: "lines", name: "E(x)", line: { color: "#2ca02c" } },
            { x, y: k, mode: "lines", name: "K(x)", line: { color: "#d62728" } },
            { x, y: g, mode: "lines", name: "G(x)", line: { color: "#1f77b4" } }
        );

        const shapes = [];
        if (showCapacityLine) {
            shapes.push({
                type: "line",
                x0: capacity,
                x1: capacity,
                yref: "paper",
                y0: 0,
                y1: 1,
                line: { dash: "dot", width: 1 },
            });
        }

        figure.layout = {
            title: hasMonopolyRevenue
                ? "Preis-Absatz-, Erlös-, Kosten- und Gewinnfunktion"
                : "Erlös-, Kosten- und Gewinnfunktion",
            xaxis: { title: "Menge x" },
            yaxis: { title: "Wert" },
            shapes,
        };
    } else if (specType === "cost-curves") {
        const params = typeof spec?.params === "object" && spec.params ? spec.params : {};
        const k3 = toNumber(params.k3, 0.05);
        const k2 = toNumber(params.k2, -1.0);
        const k1 = toNumber(params.k1, 10.0);
        const k0 = toNumber(params.k0, 80.0);
        const maxX = Math.max(1, toNumber(params.maxX, 30.0));
        const startX = 0.5;
        const points = Math.max(40, Math.trunc(toNumber(spec?.points, 300)));

        const x = [];
        const gk = [];
        const k = [];
        const kv = [];
        for (let i = 0; i < points; i += 1) {
            const xi = startX + ((maxX - startX) * i) / (points - 1);
            x.push(xi);
            gk.push(3 * k3 * xi ** 2 + 2 * k2 * xi + k1);
            k.push(k3 * xi ** 2 + k2 * xi + k1 + k0 / xi);
            kv.push(k3 * xi ** 2 + k2 * xi + k1);
        }

        figure.data.push(
            { x, y: gk, mode: "lines", name: "K(x)", line: { color: "#1f77b4" } },
            { x, y: k, mode: "lines", name: "k(x)", line: { color: "#d62728" } },
            { x, y: kv, mode: "lines", name: "kv(x)", line: { color: "#2ca02c" } }
        );

        figure.layout = {
            title: "Grenzkosten-, Stückkosten- und variable Stückkostenfunktion",
            xaxis: { title: "Menge x", range: [0, maxX] },
            yaxis: { title: "Kosten" },
        };
    } else if (specType === "market-curves") {
        const params = typeof spec?.params === "object" && spec.params ? spec.params : {};
        const supplySlope = Math.max(0.01, toNumber(params.supplySlope, 1.2));
        const demandSlope = Math.max(0.01, toNumber(params.demandSlope, 1.8));
        const minPrice = toNumber(params.minPrice, 5.0);
        const maxPrice = toNumber(params.maxPrice, 20.0);
        const maxX = Math.max(5, toNumber(params.maxX, 20.0));
        const points = Math.max(40, Math.trunc(toNumber(spec?.points, 220)));

        const x = [];
        const supply = [];
        const demand = [];
        for (let i = 0; i < points; i += 1) {
            const xi = (maxX * i) / (points - 1);
            x.push(xi);
            supply.push(supplySlope * xi + minPrice);
            demand.push(-demandSlope * xi + maxPrice);
        }

        const eqX = (maxPrice - minPrice) / (supplySlope + demandSlope);
        const eqY = supplySlope * eqX + minPrice;

        figure.data.push(
            { x, y: supply, mode: "lines", name: "pA(x)", line: { color: "#d62728" } },
            { x, y: demand, mode: "lines", name: "pN(x)", line: { color: "#1f77b4" } }
        );

        figure.layout = {
            title: "Angebots- und Nachfragefunktion",
            xaxis: { title: "Menge x", range: [0, maxX] },
            yaxis: { title: "Preis p", range: [0, Math.max(maxPrice, eqY) * 1.15] },
        };
    } else if (specType === "market-equilibrium" || specType === "market-abschoepfung") {
        const params = typeof spec?.params === "object" && spec.params ? spec.params : {};
        const supplyP = params.supply ?? {};
        const demandP = params.demand ?? {};
        const eqX = toNumber(params.eqX, 10);
        const eqP = toNumber(params.eqP, 10);
        const maxX = Math.max(1, toNumber(params.maxX, 30));
        const points = Math.max(40, Math.trunc(toNumber(spec?.points, 260)));

        function evalFn(p, x) {
            if (p.type === "linear") return (p.a ?? 1) * x + (p.b ?? 0);
            if (p.type === "quadratic") return (p.a ?? 0) * x * x + (p.b ?? 0) * x + (p.c ?? 0);
            if (p.type === "exp") return (p.A ?? 1) * Math.exp(-(p.rate ?? 0.1) * x) + (p.c ?? 0);
            return 0;
        }

        const x = [];
        const supply = [];
        for (let i = 0; i < points; i += 1) {
            const xi = (maxX * i) / (points - 1);
            x.push(xi);
            supply.push(evalFn(supplyP, xi));
        }

        const satX =
            specType === "market-equilibrium" ? Math.max(eqX * 1.02, toNumber(params.satX, maxX)) : maxX;
        const demandPoints = Math.max(40, Math.round((points * satX) / maxX));
        const xDemand = [];
        const demand = [];
        for (let i = 0; i < demandPoints; i += 1) {
            const xi = (satX * i) / (demandPoints - 1);
            xDemand.push(xi);
            demand.push(evalFn(demandP, xi));
        }

        if (specType === "market-abschoepfung") {
            const x2 = toNumber(params.x2, 5);
            const p2 = toNumber(params.p2, 15);

            const kr2CurveX = Array.from({ length: 81 }, (_, i) => (x2 * i) / 80);
            const kr2CurveY = kr2CurveX.map((xi) => evalFn(demandP, xi));
            const kr2X = [0, x2, ...kr2CurveX.slice().reverse()];
            const kr2Y = [p2, p2, ...kr2CurveY.slice().reverse()];

            const kr1CurveX = Array.from({ length: 81 }, (_, i) => x2 + ((eqX - x2) * i) / 80);
            const kr1CurveY = kr1CurveX.map((xi) => evalFn(demandP, xi));
            const kr1X = [x2, eqX, ...kr1CurveX.slice().reverse()];
            const kr1Y = [eqP, eqP, ...kr1CurveY.slice().reverse()];

            figure.data.push(
                {
                    x: kr2X,
                    y: kr2Y,
                    mode: "lines",
                    name: "KR2",
                    line: { width: 0 },
                    fill: "toself",
                    fillcolor: "rgba(59, 130, 246, 0.25)",
                },
                {
                    x: kr1X,
                    y: kr1Y,
                    mode: "lines",
                    name: "KR1",
                    line: { width: 0 },
                    fill: "toself",
                    fillcolor: "rgba(16, 185, 129, 0.25)",
                },
                { x, y: supply, mode: "lines", name: "Angebot p_A(x)", line: { color: "#d62728" } },
                {
                    x,
                    y: demand,
                    mode: "lines",
                    name: "Nachfrage p_N(x)",
                    line: { color: "#1f77b4" },
                }
            );
            const maxY = Math.max(toNumber(params.maxY, 30), p2) * 1.12;
            figure.layout = {
                title: "Preisdifferenzierung mit KR1 und KR2",
                xaxis: { title: "Menge x", range: [0, maxX] },
                yaxis: { title: "Preis p", range: [0, maxY] },
                shapes: [
                    { type: "line", x0: x2, x1: x2, y0: 0, y1: p2, line: { color: "#374151", dash: "dot" } },
                    {
                        type: "line",
                        x0: eqX,
                        x1: eqX,
                        y0: 0,
                        y1: eqP,
                        line: { color: "#374151", dash: "dot" },
                    },
                    { type: "line", x0: 0, x1: x2, y0: p2, y1: p2, line: { color: "#374151", dash: "dot" } },
                    {
                        type: "line",
                        x0: 0,
                        x1: eqX,
                        y0: eqP,
                        y1: eqP,
                        line: { color: "#374151", dash: "dot" },
                    },
                ],
                annotations: [
                    { x: x2, y: -0.08, xref: "x", yref: "paper", text: "x_2", showarrow: false },
                    { x: eqX, y: -0.08, xref: "x", yref: "paper", text: "x_G", showarrow: false },
                    { x: 0, y: p2, xref: "paper", yref: "y", xanchor: "right", text: "p_2", showarrow: false },
                    {
                        x: 0,
                        y: eqP,
                        xref: "paper",
                        yref: "y",
                        xanchor: "right",
                        text: "p_G",
                        showarrow: false,
                    },
                ],
            };
        } else {
            figure.data.push(
                { x, y: supply, mode: "lines", name: "Angebot p_A(x)", line: { color: "#d62728" } },
                {
                    x: xDemand,
                    y: demand,
                    mode: "lines",
                    name: "Nachfrage p_N(x)",
                    line: { color: "#1f77b4" },
                }
            );
            const maxY = toNumber(params.maxY, Math.max(eqP, evalFn(demandP, 0)) * 1.12);
            figure.layout = {
                title: "Angebots- und Nachfragefunktion",
                xaxis: { title: "Menge x", range: [0, maxX] },
                yaxis: { title: "Preis p", range: [0, maxY] },
            };
        }
    } else if (specType === "ab-tree") {
        const treeFigure = buildBaumdiagrammFigure({
            pa: toNumber(spec?.pa, 0.5),
            pba: toNumber(spec?.pba, 0.5),
            pbna: toNumber(spec?.pbna, 0.5),
            mode: "slots",
            givenSlots: Array.isArray(spec?.givenSlots) ? spec.givenSlots : [],
            edgeDecimals: 2,
            leafDecimals: 4,
        });
        figure.data = treeFigure.data;
        figure.layout = treeFigure.layout;
    } else if (specType === "binomial-histogramm-einzeln") {
        const hFig = buildHistogrammEinzelnFigure({
            n: toNumber(spec?.n, 10),
            p: toNumber(spec?.p, 0.5),
        });
        figure.data = hFig.data;
        figure.layout = hFig.layout;
    } else if (specType === "binomial-histogramm-kumuliert") {
        const hFig = buildHistogrammKumuliertFigure({
            n: toNumber(spec?.n, 10),
            p: toNumber(spec?.p, 0.5),
        });
        figure.data = hFig.data;
        figure.layout = hFig.layout;
    } else {
        const traces = Array.isArray(spec?.traces) ? spec.traces : [];
        traces.forEach((trace) => {
            if (!trace || typeof trace !== "object") return;
            const plotlyTrace = {
                x: Array.isArray(trace.x) ? trace.x : [],
                y: Array.isArray(trace.y) ? trace.y : [],
                mode: trace.mode ?? "lines",
                name: trace.name,
                type: trace.kind ?? "scatter",
            };
            if (trace.line != null) plotlyTrace.line = trace.line;
            if (trace.marker != null) plotlyTrace.marker = trace.marker;
            if (trace.fill != null) plotlyTrace.fill = trace.fill;
            if (trace.fillcolor != null) plotlyTrace.fillcolor = trace.fillcolor;
            if (trace.text != null) plotlyTrace.text = trace.text;
            if (trace.textposition != null) plotlyTrace.textposition = trace.textposition;
            if (trace.textfont != null) plotlyTrace.textfont = trace.textfont;
            if (trace.showlegend != null) plotlyTrace.showlegend = trace.showlegend;
            if (trace.opacity != null) plotlyTrace.opacity = trace.opacity;
            if (trace.hoverinfo != null) plotlyTrace.hoverinfo = trace.hoverinfo;
            figure.data.push(plotlyTrace);
        });
    }

    if (spec?.layout && typeof spec.layout === "object") {
        figure.layout = { ...figure.layout, ...spec.layout };
    }

    return figure;
}

function ensureEqualColumns(table) {
    if (!table || table.querySelector(':scope > colgroup[data-auto-eq]')) return;
    const maxCols = Array.from(table.rows).reduce((max, row) =>
        Math.max(max, Array.from(row.cells).reduce((s, c) =>
            s + (parseInt(c.getAttribute("colspan"), 10) || 1), 0)), 0);
    if (maxCols < 1) return;
    const cg = document.createElement("colgroup");
    cg.dataset.autoEq = "";
    for (let i = 0; i < maxCols; i++) {
        cg.appendChild(document.createElement("col"));
    }
    table.insertBefore(cg, table.firstChild);
}

function buildWktTable(spec) {
    const xVals = Array.isArray(spec?.x) ? spec.x : [];
    const pVals = Array.isArray(spec?.p) ? spec.p : [];

    const table = document.createElement("table");

    const thead = document.createElement("thead");
    const rowX = document.createElement("tr");
    const thX = document.createElement("th");
    thX.innerHTML = "\\( x_i \\)";
    rowX.appendChild(thX);
    xVals.forEach((v) => {
        const th = document.createElement("th");
        th.innerHTML = v == null ? "" : `\\( ${v} \\)`;
        rowX.appendChild(th);
    });
    thead.appendChild(rowX);

    const tbody = document.createElement("tbody");
    const rowP = document.createElement("tr");
    const tdP = document.createElement("td");
    tdP.innerHTML = "\\( P(X=x_i) \\)";
    rowP.appendChild(tdP);
    pVals.forEach((v) => {
        const td = document.createElement("td");
        td.innerHTML = v == null ? "" : `\\( ${String(v).replace(".", "{,}")} \\)`;
        rowP.appendChild(td);
    });
    tbody.appendChild(rowP);

    table.appendChild(thead);
    table.appendChild(tbody);
    return table;
}

function buildVftTable(spec) {
    const slots = typeof spec?.slots === "object" && spec.slots ? spec.slots : {};
    const givenSlots = new Set(Array.isArray(spec?.givenSlots) ? spec.givenSlots.map(Number) : []);
    const circled = { 1: "①", 2: "②", 3: "③", 4: "④", 5: "⑤", 6: "⑥", 7: "⑦", 8: "⑧" };

    function cell(idx) {
        if (givenSlots.has(idx)) {
            return Number(slots[String(idx)]).toFixed(4);
        }
        return circled[idx] ?? String(idx);
    }

    const table = document.createElement("table");
    table.classList.add("vft-table");

    table.innerHTML = `
        <thead>
        <tr>
            <th></th>
            <th>\\(P(A)\\)</th>
            <th>\\(P(\\overline{A})\\)</th>
            <th class="vft-sum"></th>
        </tr>
        </thead>
        <tbody>
        <tr>
            <td>\\(P(B)\\)</td>
            <td>${cell(1)}</td>
            <td>${cell(3)}</td>
            <td class="vft-sum">${cell(7)}</td>
        </tr>
        <tr>
            <td>\\(P(\\overline{B})\\)</td>
            <td>${cell(2)}</td>
            <td>${cell(4)}</td>
            <td class="vft-sum">${cell(8)}</td>
        </tr>
        <tr class="vft-sum-row">
            <td></td>
            <td>${cell(5)}</td>
            <td>${cell(6)}</td>
            <td class="vft-sum">1</td>
        </tr>
        </tbody>`;

    return table;
}

export function renderVisual(task, wrapper) {
    const visual = task?.visual;
    const spec = visual?.spec;
    if (!spec || typeof spec !== "object") {
        return;
    }

    const specType = String(spec?.type ?? "").toLowerCase();

    if (specType === "vft") {
        const tableWrapper = document.createElement("div");
        tableWrapper.className = "intro";
        const scrollWrapper = document.createElement("div");
        scrollWrapper.className = "table-scroll";
        const tbl = buildVftTable(spec);
        ensureEqualColumns(tbl);
        scrollWrapper.appendChild(tbl);
        tableWrapper.appendChild(scrollWrapper);
        wrapper.appendChild(tableWrapper);
        return;
    }

    if (specType === "wkt-tabelle") {
        const tableWrapper = document.createElement("div");
        tableWrapper.className = "intro";
        const scrollWrapper = document.createElement("div");
        scrollWrapper.className = "table-scroll";
        const tbl = buildWktTable(spec);
        ensureEqualColumns(tbl);
        scrollWrapper.appendChild(tbl);
        tableWrapper.appendChild(scrollWrapper);
        wrapper.appendChild(tableWrapper);
        return;
    }

    if (!window.Plotly) {
        return;
    }

    const plotContainer = document.createElement("div");
    plotContainer.className = "intro";
    wrapper.appendChild(plotContainer);

    if (specType === "verflechtungsdiagramm") {
        const vdFigure = buildVerflechtungsdiagrammFigure(spec);
        if (!Array.isArray(vdFigure.data) || vdFigure.data.length === 0) return;
        plotlyRender(plotContainer, vdFigure.data, {
            ...vdFigure.layout,
            margin: { l: 10, r: 10, t: 10, b: 10 },
        });
        return;
    }

    const figure = buildPlotlyFigure(spec);
    if (!Array.isArray(figure.data) || figure.data.length === 0) {
        return;
    }

    plotlyRender(
        plotContainer,
        figure.data,
        {
            ...figure.layout,
            legend: {
                orientation: "h",
                x: 0.5,
                xanchor: "center",
                y: -0.2,
                yanchor: "top",
            },
            margin: { l: 40, r: 20, t: 35, b: 90 },
        },
    );
}
