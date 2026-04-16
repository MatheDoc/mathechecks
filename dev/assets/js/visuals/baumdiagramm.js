/**
 * Shared Baumdiagramm (tree diagram) builder for Plotly.
 *
 * Modes:
 *   "numeric" – all edges and leaves show computed probability values (default).
 *   "symbol"  – edges show P(A), P_A(B) etc., leaves show P(A∩B) etc.
 *   "slots"   – circled digits for unknowns; givenSlots entries show values.
 */

import { themeTextColor } from "./plotly-defaults.js";

export function buildBaumdiagrammFigure(opts = {}) {
    const {
        pa = 0.5,
        pba = 0.5,
        pbna = 0.5,
        labelA = "A",
        labelAbar = "A\u0305",
        labelB = "B",
        labelBbar = "B\u0305",
        titel = "",
        mode = "numeric",
        givenSlots = [],
        edgeDecimals = 4,
        leafDecimals = 4,
    } = opts;

    // --- probabilities ---
    const pna = 1 - pa;
    const pnba = 1 - pba;
    const pnbna = 1 - pbna;
    const pAB = pa * pba;
    const pAnB = pa * pnba;
    const pnAB = pna * pbna;
    const pnAnB = pna * pnbna;

    // Slot mapping: 1–6 edges, 7–10 leaves
    const slotValues = {
        1: pa,
        2: pna,
        3: pba,
        4: pnba,
        5: pbna,
        6: pnbna,
        7: pAB,
        8: pAnB,
        9: pnAB,
        10: pnAnB,
    };

    // --- symbol labels (dynamic, based on actual node labels) ---
    const symbolEdgeLabels = [
        `P(${labelA})`,
        `P(${labelAbar})`,
        `P<sub>${labelA}</sub>(${labelB})`,
        `P<sub>${labelA}</sub>(${labelBbar})`,
        `P<sub>${labelAbar}</sub>(${labelB})`,
        `P<sub>${labelAbar}</sub>(${labelBbar})`,
    ];
    const symbolLeafLabels = [
        `P(${labelA} \u2229 ${labelB})`,
        `P(${labelA} \u2229 ${labelBbar})`,
        `P(${labelAbar} \u2229 ${labelB})`,
        `P(${labelAbar} \u2229 ${labelBbar})`,
    ];

    const circledDigits = {
        1: "\u2460",
        2: "\u2461",
        3: "\u2462",
        4: "\u2463",
        5: "\u2464",
        6: "\u2465",
        7: "\u2466",
        8: "\u2467",
        9: "\u2468",
        10: "\u2469",
    };
    const givenSet = new Set(givenSlots.map(Number));

    function fmtSlot(idx) {
        if (mode === "symbol") {
            return idx <= 6 ? symbolEdgeLabels[idx - 1] : symbolLeafLabels[idx - 7];
        }
        if (mode === "slots" && !givenSet.has(idx)) {
            return circledDigits[idx] ?? String(idx);
        }
        const decimals = idx <= 6 ? edgeDecimals : leafDecimals;
        return slotValues[idx].toFixed(decimals);
    }

    // --- nodes ---
    const nodes = [
        { x: 0, y: 0.5 },
        { x: 0.5, y: 0.75 },
        { x: 0.5, y: 0.25 },
        { x: 1, y: 0.875 },
        { x: 1, y: 0.625 },
        { x: 1, y: 0.375 },
        { x: 1, y: 0.125 },
    ];
    const nodeLabels = ["", labelA, labelAbar, labelB, labelBbar, labelB, labelBbar];

    // --- edges ---
    const edgePairs = [
        [0, 1],
        [0, 2],
        [1, 3],
        [1, 4],
        [2, 5],
        [2, 6],
    ];
    const edgeSlots = [1, 2, 3, 4, 5, 6];

    const edgeShapes = edgePairs.map(([fi, ti]) => ({
        type: "line",
        x0: nodes[fi].x,
        y0: nodes[fi].y,
        x1: nodes[ti].x,
        y1: nodes[ti].y,
        line: { width: 2, color: "gray" },
        layer: "below",
    }));

    const edgeAnnotations = edgePairs.map(([fi, ti], i) => {
        const xm = (nodes[fi].x + nodes[ti].x) / 2;
        const ym = (nodes[fi].y + nodes[ti].y) / 2;
        const isFirstStage = fi === 0;
        const goesUp = nodes[ti].y > nodes[fi].y;
        const yOffset = isFirstStage
            ? goesUp
                ? -0.08
                : 0.08
            : goesUp
                ? -0.05
                : 0.05;
        return {
            x: xm,
            y: ym - yOffset,
            text: fmtSlot(edgeSlots[i]),
            showarrow: false,
            font: { size: 15 },
        };
    });

    // --- leaves ---
    const leafSlots = [7, 8, 9, 10];
    const leafNodes = [3, 4, 5, 6];
    const leafAnnotations = leafNodes.map((ni, i) => ({
        x: nodes[ni].x + 0.25,
        y: nodes[ni].y,
        text: fmtSlot(leafSlots[i]),
        showarrow: false,
        font: { size: 15 },
    }));

    // --- trace ---
    const nodeTrace = {
        x: nodes.map((n) => n.x),
        y: nodes.map((n) => n.y),
        text: nodeLabels,
        mode: "markers+text",
        type: "scatter",
        textposition: "middle center",
        textfont: { size: 20, color: "#1a1a2e" },
        marker: {
            size: nodes.map((_, i) => (i === 0 ? 0 : 40)),
            color: "#b3e0ff",
            opacity: 1,
            line: { width: 2, color: "gray" },
            symbol: "circle",
        },
        hoverinfo: "none",
    };

    // --- layout ---
    const layout = {
        xaxis: { visible: false, range: [0, 1.4] },
        yaxis: { visible: false, range: [0, 1] },
        shapes: edgeShapes,
        annotations: [...edgeAnnotations, ...leafAnnotations],
        margin: { l: 20, r: 20, t: titel ? 100 : 20, b: 20 },
        dragmode: false,
    };
    if (titel) {
        layout.title = { text: titel, y: 0.85 };
    }

    return { data: [nodeTrace], layout };
}
