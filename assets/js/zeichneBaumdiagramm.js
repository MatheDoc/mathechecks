function zeichneBaumdiagramm(
  div,
  pa,
  pba,
  pbna,
  titel,
  labelA,
  labelAbar,
  labelB,
  labelBbar,
  symbol
) {
  // Definition der Knoten
  const nodes = [
    { x: 0, y: 0.5, label: "", id: "start" },
    { x: 0.5, y: 0.75, label: labelA },
    { x: 0.5, y: 0.25, label: labelAbar },
    { x: 1, y: 0.875, label: labelB },
    { x: 1, y: 0.625, label: labelBbar },
    { x: 1, y: 0.375, label: labelB },
    { x: 1, y: 0.125, label: labelBbar },
  ];

  // Wahrscheinlichkeiten berechnen
  const pna = 1 - pa;
  const pAb = pa * pba;
  const pAnb = pa * (1 - pba);
  const pNAb = pna * pbna;
  const pNAnb = pna * (1 - pbna);

  // Kanten mit Labels (je nach symbol=true/false)
  const edges = symbol
    ? [
        { from: nodes[0], to: nodes[1], label: "P(A)" },
        { from: nodes[0], to: nodes[2], label: "P(A\u0305)" },
        { from: nodes[1], to: nodes[3], label: "P<sub>A</sub>(B)" },
        { from: nodes[1], to: nodes[4], label: "P<sub>A</sub>(B\u0305)" },
        { from: nodes[2], to: nodes[5], label: "P<sub>A\u0305</sub>(B)" },
        {
          from: nodes[2],
          to: nodes[6],
          label: "P<sub>A\u0305</sub>(B\u0305)",
        },
      ]
    : [
        { from: nodes[0], to: nodes[1], label: `${pa.toFixed(4)}` },
        { from: nodes[0], to: nodes[2], label: `${(1 - pa).toFixed(4)}` },
        { from: nodes[1], to: nodes[3], label: `${pba.toFixed(4)}` },
        { from: nodes[1], to: nodes[4], label: `${(1 - pba).toFixed(4)}` },
        { from: nodes[2], to: nodes[5], label: `${pbna.toFixed(4)}` },
        { from: nodes[2], to: nodes[6], label: `${(1 - pbna).toFixed(4)}` },
      ];

  // Wahrscheinlichkeiten an den Enden
  const leafProbs = [
    { node: nodes[3], prob: pAb },
    { node: nodes[4], prob: pAnb },
    { node: nodes[5], prob: pNAb },
    { node: nodes[6], prob: pNAnb },
  ];

  // Linien
  const edgeShapes = edges.map((e) => {
    return {
      type: "line",
      x0: e.from.x,
      y0: e.from.y,
      x1: e.to.x,
      y1: e.to.y,
      line: { width: 2, color: "gray" },
      layer: "below",
    };
  });

  // Kanten-Labels
  const edgeLabels = edges.map((e) => {
    const xm = (e.from.x + e.to.x) / 2;
    const ym = (e.from.y + e.to.y) / 2;
    // Erste Stufe: Startknoten (i==0 oder i==1)
    if (e.from.id === "start") {
      const yOffset = e.to.y > e.from.y ? -0.08 : 0.08;
      return {
        x: xm,
        y: ym - yOffset,
        text: e.label,
        showarrow: false,
        font: { size: 15 },
      };
    } else {
      const isUpper = e.from.y > e.to.y;
      const yOffset = isUpper ? 0.05 : -0.05;
      return {
        x: xm,
        y: ym - yOffset,
        text: e.label,
        showarrow: false,
        font: { size: 15 },
      };
    }
  });

  const leafLabels = symbol
    ? [
        {
          x: nodes[3].x + 0.25,
          y: nodes[3].y,
          text: "P(A ∩ B)",
          showarrow: false,
          font: { size: 15 },
        },
        {
          x: nodes[4].x + 0.25,
          y: nodes[4].y,
          text: "P(A ∩ B̅)",
          showarrow: false,
          font: { size: 15 },
        },
        {
          x: nodes[5].x + 0.25,
          y: nodes[5].y,
          text: "P(Ā ∩ B)",
          showarrow: false,
          font: { size: 15 },
        },
        {
          x: nodes[6].x + 0.25,
          y: nodes[6].y,
          text: "P(Ā ∩ B̅)",
          showarrow: false,
          font: { size: 15 },
        },
      ]
    : leafProbs.map((lp) => ({
        x: lp.node.x + 0.25,
        y: lp.node.y,
        text: `${lp.prob.toFixed(4)}`,
        showarrow: false,
        font: { size: 15 },
      }));

  // Knoten
  const nodeTrace = {
    x: nodes.map((n) => n.x),
    y: nodes.map((n) => n.y),
    text: nodes.map((n) => n.label),
    mode: "markers+text",
    type: "scatter",
    textposition: "middle center",
    textfont: {
      size: 20,
    },
    marker: {
      size: nodes.map((n, i) => (i === 0 ? 0 : 40)),
      color: "#b3e0ff",
      opacity: 1,
      line: { width: 2, color: "gray" },
      symbol: "circle",
    },
    hoverinfo: "none",
  };

  const layout = {
    title: {
      text: titel,
      y: 0.85,
    },
    xaxis: { visible: false, range: [0, 1.4] },
    yaxis: { visible: false, range: [0, 1] },
    shapes: edgeShapes,
    annotations: [...edgeLabels, ...leafLabels],
    margin: { l: 20, r: 20, t: 100, b: 20 },
    dragmode: false,
  };

  const config = {
    scrollZoom: false,
    responsive: true,
  };

  Plotly.newPlot(div, [nodeTrace], layout, config);
}
