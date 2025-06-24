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
      title: "x",
      tickmode: "array",
      tickvals: xWerte,
      type: "linear",
    },
    yaxis: {
      title: "P(X = x)",
      range: [0, Math.max(...yWerte) * 1.1],
      gridcolor: "rgba(0, 0, 0, 0.2)",
    },
    bargap: 0, // Abstand nur, wenn keine width gesetzt ist
    showlegend: false,
    margin: { t: 100, r: 20, b: 40, l: 50 },
    dragmode: false,
  };

  const config = { scrollZoom: false };

  Plotly.newPlot(div, data, layout, config);
}
