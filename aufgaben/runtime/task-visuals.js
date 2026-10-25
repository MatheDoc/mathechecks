import { buildBaumdiagrammFigure } from "../../assets/js/visuals/baumdiagramm.js";
import { buildHistogrammEinzelnFigure, buildHistogrammKumuliertFigure } from "../../assets/js/visuals/histogramm.js";
import { plotlyRender } from "../../assets/js/visuals/plotly-defaults.js?v=20260512-plotly-hover-name-theme";
import { buildVerflechtungsdiagrammFigure } from "../../assets/js/visuals/verflechtungsdiagramm.js?v=20260917-edge-labels";

function toNumber(value, fallback) {
    const numeric = Number(value);
    return Number.isFinite(numeric) ? numeric : fallback;
}

function evaluatePolynomial(coefficients, xValue) {
    const safeCoefficients = Array.isArray(coefficients) ? coefficients : [];
    let result = 0;
    safeCoefficients.forEach((coefficient) => {
        result = result * xValue + toNumber(coefficient, 0);
    });
    return Math.abs(result) < 1e-12 ? 0 : result;
}

function applyTraceOptions(target, source) {
    if (!source || typeof source !== "object") return;
    if (source.line != null) target.line = source.line;
    if (source.marker != null) target.marker = source.marker;
    if (source.fill != null) target.fill = source.fill;
    if (source.fillcolor != null) target.fillcolor = source.fillcolor;
    if (source.text != null) target.text = source.text;
    if (source.textposition != null) target.textposition = source.textposition;
    if (source.textfont != null) target.textfont = source.textfont;
    if (source.showlegend != null) target.showlegend = source.showlegend;
    if (source.opacity != null) target.opacity = source.opacity;
    if (source.hoverinfo != null) target.hoverinfo = source.hoverinfo;
}

function buildPolynomialCurvesFigure(spec) {
    const figure = { data: [], layout: {} };
    const layout = typeof spec?.layout === "object" && spec.layout ? spec.layout : {};
    const xAxis = typeof layout.xaxis === "object" && layout.xaxis ? layout.xaxis : {};
    const xRangeRaw = Array.isArray(xAxis.range) ? xAxis.range : [-8, 8];
    let xMin = toNumber(xRangeRaw[0], -8);
    let xMax = toNumber(xRangeRaw[1], 8);
    if (xMax <= xMin) {
        xMin = -8;
        xMax = 8;
    }

    const points = Math.max(40, Math.trunc(toNumber(spec?.points, 241)));
    const xValues = [];
    for (let index = 0; index < points; index += 1) {
        const xValue = xMin + ((xMax - xMin) * index) / (points - 1);
        xValues.push(roundNumber(xValue, 4));
    }

    const curves = Array.isArray(spec?.curves) ? spec.curves : [];
    curves.forEach((curve) => {
        const coefficients = Array.isArray(curve?.coefficients) ? curve.coefficients : [];
        const plotlyTrace = {
            x: xValues,
            y: xValues.map((xValue) => roundNumber(evaluatePolynomial(coefficients, xValue), 6)),
            mode: curve?.mode ?? "lines",
            name: curve?.name,
            type: curve?.kind ?? "scatter",
        };
        applyTraceOptions(plotlyTrace, curve);
        figure.data.push(plotlyTrace);
    });

    const extraTraces = Array.isArray(spec?.extraTraces) ? spec.extraTraces : [];
    extraTraces.forEach((trace) => {
        if (!trace || typeof trace !== "object") return;
        const plotlyTrace = {
            x: Array.isArray(trace.x) ? trace.x : [],
            y: Array.isArray(trace.y) ? trace.y : [],
            mode: trace.mode ?? "lines",
            name: trace.name,
            type: trace.kind ?? "scatter",
        };
        applyTraceOptions(plotlyTrace, trace);
        figure.data.push(plotlyTrace);
    });

    const rawLayout = typeof spec?.layout === "object" && spec.layout ? spec.layout : {};
    figure.layout = { ...rawLayout };

    return figure;
}

function roundNumber(value, digits) {
    const factor = 10 ** digits;
    return Math.round(toNumber(value, 0) * factor) / factor;
}

// Übersetzt einen Term (Zahlen, Variable, + - * / ^, Klammern, exp(...)) in vollständig
// geklammertes JS. Mathematische Konvention: -t^2 = -(t^2), ^ rechtsassoziativ.
// Reines Ersetzen von ^ durch ** scheitert an "-t**2" (SyntaxError in JS).
function translateExpressionToJs(sourceTerm, variableName) {
    const tokens = sourceTerm.match(/\d+(?:\.\d+)?(?:[eE][+-]?\d+)?|\.\d+|[a-zA-Z_]+|[+\-*/^()]|\S/g) || [];
    let position = 0;
    const peek = () => tokens[position];
    const take = () => tokens[position++];
    const fail = () => { throw new Error(`Ungültiger Term: ${sourceTerm}`); };

    function parseSum() {
        let left = parseProduct();
        while (peek() === "+" || peek() === "-") {
            const operator = take();
            left = `(${left}${operator}${parseProduct()})`;
        }
        return left;
    }
    function parseProduct() {
        let left = parseUnary();
        while (peek() === "*" || peek() === "/") {
            const operator = take();
            left = `(${left}${operator}${parseUnary()})`;
        }
        return left;
    }
    function parseUnary() {
        if (peek() === "-") { take(); return `(-${parseUnary()})`; }
        if (peek() === "+") { take(); return parseUnary(); }
        return parsePower();
    }
    function parsePower() {
        const base = parsePrimary();
        if (peek() === "^") { take(); return `Math.pow(${base},${parseUnary()})`; }
        return base;
    }
    function parsePrimary() {
        const token = take();
        if (token == null) fail();
        if (/^(?:\d|\.\d)/.test(token)) return `(${token})`;
        if (token === variableName) return token;
        if (token === "exp" && peek() === "(") {
            take();
            const inner = parseSum();
            if (take() !== ")") fail();
            return `Math.exp(${inner})`;
        }
        if (token === "(") {
            const inner = parseSum();
            if (take() !== ")") fail();
            return inner;
        }
        return fail();
    }

    const result = parseSum();
    if (position !== tokens.length) fail();
    return result;
}

function buildExpressionFunction(term, variableName = "x") {
    const sourceTerm = String(term ?? "").trim();
    const safeVariable = /^[a-zA-Z]$/.test(variableName) ? variableName : "x";
    if (!sourceTerm) return null;

    let executable;
    try {
        executable = translateExpressionToJs(sourceTerm, safeVariable);
    } catch (error) {
        console.error("[task-visuals] Term nicht darstellbar:", sourceTerm, error);
        return null;
    }

    try {
        const evaluator = new Function(safeVariable, `"use strict"; return ${executable};`);
        return (value) => {
            const result = Number(evaluator(value));
            if (!Number.isFinite(result)) return null;
            return Math.abs(result) < 1e-12 ? 0 : result;
        };
    } catch {
        return null;
    }
}

function buildExpressionCurvesFigure(spec) {
    const figure = { data: [], layout: {} };
    const layout = typeof spec?.layout === "object" && spec.layout ? spec.layout : {};
    const xAxis = typeof layout.xaxis === "object" && layout.xaxis ? layout.xaxis : {};
    const xRangeRaw = Array.isArray(xAxis.range) ? xAxis.range : [0, 10];
    let xMin = toNumber(xRangeRaw[0], 0);
    let xMax = toNumber(xRangeRaw[1], 10);
    if (xMax <= xMin) {
        xMin = 0;
        xMax = 10;
    }

    const points = Math.max(40, Math.trunc(toNumber(spec?.points, 241)));
    const xValues = [];
    for (let index = 0; index < points; index += 1) {
        const xValue = xMin + ((xMax - xMin) * index) / (points - 1);
        xValues.push(roundNumber(xValue, 4));
    }

    const curves = Array.isArray(spec?.curves) ? spec.curves : [];
    curves.forEach((curve) => {
        const variableName = String(curve?.variable || spec?.variable || "x").trim() || "x";
        const evaluateExpression = buildExpressionFunction(curve?.term, variableName);
        if (typeof evaluateExpression !== "function") return;

        const yValues = xValues.map((xValue) => {
            const result = evaluateExpression(xValue);
            return result == null ? null : roundNumber(result, 6);
        });

        const plotlyTrace = {
            x: xValues,
            y: yValues,
            mode: curve?.mode ?? "lines",
            name: curve?.name,
            type: curve?.kind ?? "scatter",
        };
        applyTraceOptions(plotlyTrace, curve);
        figure.data.push(plotlyTrace);
    });

    const extraTraces = Array.isArray(spec?.extraTraces) ? spec.extraTraces : [];
    extraTraces.forEach((trace) => {
        if (!trace || typeof trace !== "object") return;
        const plotlyTrace = {
            x: Array.isArray(trace.x) ? trace.x : [],
            y: Array.isArray(trace.y) ? trace.y : [],
            mode: trace.mode ?? "lines",
            name: trace.name,
            type: trace.kind ?? "scatter",
        };
        applyTraceOptions(plotlyTrace, trace);
        figure.data.push(plotlyTrace);
    });

    figure.layout = { ...layout };
    return figure;
}

function buildPlotlyFigure(spec) {
    const figure = { data: [], layout: {} };
    const specType = String(spec?.type ?? "plotly").toLowerCase();

    if (specType === "linear-function" || specType === "quadratic-function") {
        const fixedSpec = {
            ...spec,
            layout: {
                title: spec?.title ?? "",
                xaxis: { title: "x", range: [-8, 8], dtick: 1, zeroline: true },
                yaxis: { title: "y", range: [-8, 8], dtick: 1, zeroline: true },
            },
        };
        return buildPolynomialCurvesFigure(fixedSpec);
    } else if (specType === "polynomial-curves") {
        return buildPolynomialCurvesFigure(spec);
    } else if (specType === "expression-curves") {
        return buildExpressionCurvesFigure(spec);
    } else if (specType === "economic-curves") {
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
            { x, y: gk, mode: "lines", name: "K\u2032(x)", line: { color: "#1f77b4" } },
            { x, y: k, mode: "lines", name: "k(x)", line: { color: "#d62728" } },
            { x, y: kv, mode: "lines", name: "k<sub>v</sub>(x)", line: { color: "#2ca02c" } }
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
            { x, y: supply, mode: "lines", name: "p<sub>A</sub>(x)", line: { color: "#d62728" } },
            { x, y: demand, mode: "lines", name: "p<sub>N</sub>(x)", line: { color: "#1f77b4" } }
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

        const specLayout = typeof spec?.layout === "object" && spec.layout ? spec.layout : {};
        const xTitle = specLayout?.xaxis?.title || "Menge x in ME";
        const yTitle = specLayout?.yaxis?.title || "Preis p in GE/ME";

        if (specType === "market-abschoepfung") {
            // Situation: Teilmarkt mit festem Preis P (price) -> Menge xP auf p_N.
            const xP = toNumber(params.xP ?? params.x2, 5);
            const price = toNumber(params.price ?? params.p2, 15);
            const priceLabel = String(Math.round(price * 100) / 100).replace(".", ",");

            const kr2CurveX = Array.from({ length: 81 }, (_, i) => (xP * i) / 80);
            const kr2CurveY = kr2CurveX.map((xi) => evalFn(demandP, xi));
            const kr2X = [0, xP, ...kr2CurveX.slice().reverse()];
            const kr2Y = [price, price, ...kr2CurveY.slice().reverse()];

            const kr1CurveX = Array.from({ length: 81 }, (_, i) => xP + ((eqX - xP) * i) / 80);
            const kr1CurveY = kr1CurveX.map((xi) => evalFn(demandP, xi));
            const kr1X = [xP, eqX, ...kr1CurveX.slice().reverse()];
            const kr1Y = [eqP, eqP, ...kr1CurveY.slice().reverse()];

            const visibleDemandX = [];
            const visibleDemand = [];
            xDemand.forEach((xi, i) => {
                if (demand[i] >= 0) {
                    visibleDemandX.push(xi);
                    visibleDemand.push(demand[i]);
                }
            });

            figure.data.push(
                {
                    x: kr2X,
                    y: kr2Y,
                    mode: "lines",
                    name: "KR<sub>2</sub>",
                    line: { width: 0 },
                    fill: "toself",
                    fillcolor: "rgba(59, 130, 246, 0.25)",
                    hoverinfo: "skip",
                },
                {
                    x: [0, xP, xP, 0, 0],
                    y: [eqP, eqP, price, price, eqP],
                    mode: "lines",
                    name: "abgeschöpfter Betrag",
                    line: { width: 1, color: "rgba(120,120,120,0.6)" },
                    fill: "toself",
                    fillcolor: "rgba(0,0,0,0)",
                    fillpattern: {
                        shape: "/",
                        fgcolor: "rgba(120,120,120,0.6)",
                        bgcolor: "rgba(0,0,0,0)",
                        size: 6,
                        solidity: 0.4,
                    },
                    hoverinfo: "skip",
                },
                {
                    x: kr1X,
                    y: kr1Y,
                    mode: "lines",
                    name: "KR<sub>1</sub>",
                    line: { width: 0 },
                    fill: "toself",
                    fillcolor: "rgba(16, 185, 129, 0.25)",
                    hoverinfo: "skip",
                },
                { x, y: supply, mode: "lines", name: "Angebot p<sub>A</sub>(x)", line: { color: "#d62728" } },
                {
                    x: visibleDemandX,
                    y: visibleDemand,
                    mode: "lines",
                    name: "Nachfrage p<sub>N</sub>(x)",
                    line: { color: "#1f77b4" },
                }
            );
            const maxY = Math.max(toNumber(params.maxY, 30), price * 1.12);
            const guide = { color: "#6b7280", width: 1.5, dash: "dash" };
            figure.layout = {
                title: specLayout.title || "Abschöpfung durch einen Teilmarkt",
                // Nur die relevanten Werte werden an den Achsen beschriftet.
                xaxis: {
                    title: xTitle,
                    range: [0, maxX],
                    tickmode: "array",
                    tickvals: [eqX],
                    ticktext: ["x<sub>G</sub>"],
                    ticks: "outside",
                    ticklen: 5,
                    automargin: true,
                },
                yaxis: {
                    title: yTitle,
                    range: [0, maxY],
                    tickmode: "array",
                    tickvals: [eqP, price],
                    ticktext: ["p<sub>G</sub>", priceLabel],
                    ticks: "outside",
                    ticklen: 5,
                    automargin: true,
                },
                shapes: [
                    { type: "line", x0: xP, x1: xP, y0: 0, y1: price, line: guide },
                    { type: "line", x0: eqX, x1: eqX, y0: 0, y1: eqP, line: guide },
                    { type: "line", x0: 0, x1: xP, y0: price, y1: price, line: guide },
                    { type: "line", x0: 0, x1: eqX, y0: eqP, y1: eqP, line: guide },
                ],
            };
        } else {
            figure.data.push(
                { x, y: supply, mode: "lines", name: "Angebot p<sub>A</sub>(x)", line: { color: "#d62728" } },
                {
                    x: xDemand,
                    y: demand,
                    mode: "lines",
                    name: "Nachfrage p<sub>N</sub>(x)",
                    line: { color: "#1f77b4" },
                }
            );
            const maxY = toNumber(params.maxY, Math.max(eqP, evalFn(demandP, 0)) * 1.12);
            figure.layout = {
                title: specLayout.title || "Angebots- und Nachfragefunktion",
                xaxis: { title: xTitle, range: [0, maxX] },
                yaxis: { title: yTitle, range: [0, maxY] },
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
            applyTraceOptions(plotlyTrace, trace);
            figure.data.push(plotlyTrace);
        });
    }

    if (spec?.layout && typeof spec.layout === "object") {
        const builderLayout = figure.layout || {};
        figure.layout = { ...builderLayout, ...spec.layout };
        // Marktdiagramme: Achsen tief mischen, damit vom Builder gesetzte
        // Achsenbeschriftungen (tickvals/ticktext, range) erhalten bleiben.
        if (specType === "market-abschoepfung" || specType === "market-equilibrium") {
            ["xaxis", "yaxis"].forEach((axis) => {
                if (spec.layout[axis] && typeof spec.layout[axis] === "object") {
                    figure.layout[axis] = { ...(builderLayout[axis] || {}), ...spec.layout[axis] };
                }
            });
        }
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

    // Types without multi-trace legends use the builder's own layout as-is.
    const noLegendTypes = ["ab-tree", "binomial-histogramm-einzeln", "binomial-histogramm-kumuliert"];
    if (noLegendTypes.includes(specType)) {
        plotlyRender(plotContainer, figure.data, figure.layout);
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
