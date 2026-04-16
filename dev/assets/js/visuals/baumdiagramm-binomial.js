/**
 * Shared Bernoulli-tree (multi-level binary) builder for Plotly.
 *
 * Generates an n-stage binary tree (T = Treffer, N = Niete).
 * When k is given, all paths with exactly k successes are highlighted.
 *
 * Returns {data, layout} ready for plotlyRender().
 */

import { themeTextColor } from "./plotly-defaults.js";

export function buildBaumdiagrammBinomialFigure({ n = 3, p = 0.5, k = null }) {
    const nodes = {};
    const edges = [];
    const leaves = Array.from({ length: Math.pow(2, n) }, (_, i) =>
        i.toString(2).padStart(n, "0").replace(/0/g, "T").replace(/1/g, "N")
    );

    const spacing = 1.5;
    leaves.forEach((leaf, i) => {
        nodes[leaf] = {
            x: n,
            y: ((leaves.length - 1) / 2) * spacing - i * spacing,
        };
    });

    function placeParents(path) {
        if (path.length === 0) return;
        const parent = path.slice(0, -1);
        if (!nodes[parent]) {
            const left = parent + "T";
            const right = parent + "N";
            if (nodes[left] && nodes[right]) {
                nodes[parent] = {
                    x: path.length - 1,
                    y: (nodes[left].y + nodes[right].y) / 2,
                };
            }
        }
        edges.push({
            from: parent,
            to: path,
            prob: path.endsWith("T") ? p : 1 - p,
        });
        placeParents(parent);
    }

    for (const leaf of leaves) placeParents(leaf);
    nodes[""] = { x: 0, y: (nodes["T"].y + nodes["N"].y) / 2 };

    // Highlighted edges for paths with exactly k successes
    const highlightedEdges = new Set();
    if (k !== null) {
        for (const key of Object.keys(nodes)) {
            if (key.length === n) {
                const numSuccesses = (key.match(/N/g) || []).length;
                if (numSuccesses === n - k) {
                    for (let i = 1; i <= key.length; i++) {
                        highlightedEdges.add(`${key.slice(0, i - 1)}->${key.slice(0, i)}`);
                    }
                }
            }
        }
    }

    // Node trace
    const nodeX = [];
    const nodeY = [];
    const nodeColors = [];
    for (const key of Object.keys(nodes)) {
        nodeX.push(nodes[key].x);
        nodeY.push(nodes[key].y);
        if (key === "") nodeColors.push(themeTextColor());
        else if (key.endsWith("T")) nodeColors.push("green");
        else nodeColors.push("red");
    }

    const nodeTrace = {
        x: nodeX,
        y: nodeY,
        mode: "markers",
        type: "scatter",
        marker: { size: 12, color: nodeColors },
        hoverinfo: "none",
    };

    // Edge traces
    const edgeTraces = [];
    for (const edge of edges) {
        const x0 = nodes[edge.from].x;
        const y0 = nodes[edge.from].y;
        const x1 = nodes[edge.to].x;
        const y1 = nodes[edge.to].y;
        const edgeKey = `${edge.from}->${edge.to}`;
        const hl = highlightedEdges.has(edgeKey);

        edgeTraces.push({
            x: [x0, x1],
            y: [y0, y1],
            mode: "lines",
            type: "scatter",
            line: { color: hl ? "gold" : "gray", width: hl ? 4 : 1 },
            hoverinfo: "none",
            showlegend: false,
        });

        edgeTraces.push({
            x: [(x0 + x1) / 2],
            y: [(y0 + y1) / 2],
            mode: "text",
            type: "scatter",
            text: [edge.prob.toFixed(2)],
            textposition: "middle center",
            hoverinfo: "none",
            showlegend: false,
            textfont: { size: 12, color: themeTextColor(), family: "Arial" },
        });
    }

    const yValues = Object.values(nodes).map((nd) => nd.y);
    const yMin = Math.min(...yValues);
    const yMax = Math.max(...yValues);

    const layout = {
        xaxis: { visible: false },
        yaxis: { visible: false, range: [yMin - 1, yMax + 1] },
        margin: { l: 20, r: 20, t: 40, b: 20 },
        height: 50 * Math.pow(2, n),
        showlegend: false,
    };

    return { data: [...edgeTraces, nodeTrace], layout };
}
