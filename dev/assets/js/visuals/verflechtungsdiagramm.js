/**
 * Shared Verflechtungsdiagramm (Gozintograph) builder for Plotly.
 *
 * Renders a 3-layer directed graph:
 *   Rohstoffe (top) → Zwischenprodukte (middle) → Endprodukte (bottom).
 *
 * Edge labels can be numeric values or circled slot markers (①②③…).
 *
 * Spec format:
 *   rohstoffe:        string[]   – node labels for top layer
 *   zwischenprodukte: string[]   – node labels for middle layer
 *   endprodukte:      string[]   – node labels for bottom layer
 *   stufe1:           [rIdx, zIdx, label][]  – edges R→Z
 *   stufe2:           [zIdx, eIdx, label][]  – edges Z→E
 */

import { themeTextColor } from "./plotly-defaults.js";

export function buildVerflechtungsdiagrammFigure(spec = {}) {
    const R = Array.isArray(spec.rohstoffe) ? spec.rohstoffe : [];
    const Z = Array.isArray(spec.zwischenprodukte) ? spec.zwischenprodukte : [];
    const E = Array.isArray(spec.endprodukte) ? spec.endprodukte : [];
    const stufe1 = Array.isArray(spec.stufe1) ? spec.stufe1 : [];
    const stufe2 = Array.isArray(spec.stufe2) ? spec.stufe2 : [];

    const nR = R.length;
    const nZ = Z.length;
    const nE = E.length;

    /* ---- node positions ---- */

    function layerPositions(count, y) {
        if (count === 0) return [];
        if (count === 1) return [{ x: 0.5, y }];
        const margin = 0.12;
        const step = (1 - 2 * margin) / (count - 1);
        return Array.from({ length: count }, (_, i) => ({
            x: margin + i * step,
            y,
        }));
    }

    const rPos = layerPositions(nR, 1.0);
    const zPos = layerPositions(nZ, 0.5);
    const ePos = layerPositions(nE, 0.0);

    const allPos = [...rPos, ...zPos, ...ePos];
    const allLabels = [...R, ...Z, ...E];

    const nodeTrace = {
        x: allPos.map((n) => n.x),
        y: allPos.map((n) => n.y),
        text: allLabels,
        mode: "markers+text",
        type: "scatter",
        textposition: "middle center",
        textfont: { size: 13 },
        marker: {
            size: 40,
            color: "#b3e0ff",
            opacity: 1,
            line: { width: 2, color: "gray" },
            symbol: "circle",
        },
        hoverinfo: "none",
    };

    /* ---- edges ---- */

    const shapes = [];
    const annotations = [];

    function addEdge(from, to, label) {
        shapes.push({
            type: "line",
            x0: from.x,
            y0: from.y,
            x1: to.x,
            y1: to.y,
            line: { width: 2, color: "gray" },
            layer: "below",
        });

        const mx = (from.x + to.x) / 2;
        const my = (from.y + to.y) / 2;
        const dx = to.x - from.x;
        const dy = to.y - from.y;
        const len = Math.sqrt(dx * dx + dy * dy) || 1;

        // Perpendicular offset – always towards the upper side of the edge.
        let nx = -dy / len;
        let ny = dx / len;
        if (ny < 0) {
            nx = -nx;
            ny = -ny;
        }
        // For vertical edges (ny ≈ 0), offset to the right.
        if (Math.abs(ny) < 0.01) {
            nx = 1;
            ny = 0;
        }

        const offset = 0.05;
        const panelColor = getComputedStyle(document.documentElement)
            .getPropertyValue("--panel-solid").trim() || "#ffffff";
        annotations.push({
            x: mx + nx * offset,
            y: my + ny * offset,
            text: String(label),
            showarrow: false,
            font: { size: 14 },
            bgcolor: panelColor + "d9",
        });
    }

    stufe1.forEach(([rIdx, zIdx, label]) => {
        if (rIdx >= 0 && rIdx < nR && zIdx >= 0 && zIdx < nZ) {
            addEdge(rPos[rIdx], zPos[zIdx], label);
        }
    });

    stufe2.forEach(([zIdx, eIdx, label]) => {
        if (zIdx >= 0 && zIdx < nZ && eIdx >= 0 && eIdx < nE) {
            addEdge(zPos[zIdx], ePos[eIdx], label);
        }
    });

    /* ---- layout ---- */

    const layout = {
        xaxis: { visible: false, range: [-0.05, 1.05] },
        yaxis: { visible: false, range: [-0.15, 1.15] },
        showlegend: false,
        shapes,
        annotations,
        margin: { l: 10, r: 10, t: 10, b: 10 },
        dragmode: false,
    };

    return { data: [nodeTrace], layout };
}
