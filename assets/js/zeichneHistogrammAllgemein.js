function getPlotlyAxisDefaults() {
  const textColor =
    getComputedStyle(document.documentElement).getPropertyValue("--text").trim() ||
    "#1a1a2e";

  return {
    tickfont: { color: textColor },
    titlefont: { color: textColor },
    gridcolor: `${textColor}22`,
    zeroline: true,
    zerolinecolor: `${textColor}aa`,
    zerolinewidth: 3,
  };
}

function zeichneHistogrammAllgemein(
  div,
  xWerte,
  yWerte,
  titel,
  balkenbreite = null
) {
  const trace = {
    x: xWerte,
    y: yWerte,
    type: "bar",
    name: "P(X = x)",
    marker: {
      color: "rgba(54, 162, 235, 0.3)",
      line: {
        color: "rgba(162, 162, 162, 0.7)",
        width: 1,
      },
    },
  };

  // Falls eine Balkenbreite angegeben wurde, füge sie hinzu
  if (balkenbreite !== null) {
    trace.width = Number(balkenbreite);
  }

  const data = [trace];

  const layout = {
    title: {
      text: titel,
      y: 0.85,
    },
    xaxis: {
      ...getPlotlyAxisDefaults(),
      title: "x",
      tickmode: "array",
      tickvals: xWerte,
      type: "linear",
    },
    yaxis: {
      ...getPlotlyAxisDefaults(),
      title: "P(X = x)",
      range: [0, Math.max(...yWerte) * 1.1],
    },
    bargap: 0, // Abstand nur, wenn keine width gesetzt ist
    showlegend: false,
    margin: { t: 100, r: 20, b: 40, l: 50 },
    dragmode: false,
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
  };

  const config = {
    scrollZoom: false,
    staticPlot: false,
    displayModeBar: false,
    doubleClick: false,
    responsive: true,
  };

  Plotly.newPlot(div, data, layout, config);
}
