function zeichneGraph(containerId, funktionen, optionen = {}) {
  // X-Achsenbereich: entweder übergeben oder Standardwerte verwenden
  const min = typeof optionen.xMin === "number" ? optionen.xMin : -5;
  const max = typeof optionen.xMax === "number" ? optionen.xMax : 20;
  const step = 0.1;
  const xWerte = [];

  for (let x = min; x <= max; x += step) {
    xWerte.push(x);
  }

  const daten = funktionen.map((f) => {
    const expr = math.parse(f.term);
    const compiled = expr.compile();

    const yWerte = xWerte.map((x) => {
      try {
        return compiled.evaluate({ x: x });
      } catch (e) {
        return null;
      }
    });

    return {
      x: xWerte,
      y: yWerte,
      type: "scatter",
      mode: "lines",
      name: f.name,
      text: f.beschreibung || "",
      hoverinfo: "name+x+y",
    };
  });

  // Punkte hinzufügen, falls vorhanden
  if (Array.isArray(optionen.punkte)) {
    const punktTrace = {
      x: optionen.punkte.map((p) => p.x),
      y: optionen.punkte.map((p) => p.y),
      mode: "markers",
      showlegend: false,
      type: "scatter",
      name: "Punkte",
      marker: {
        color: "black",
        size: 8,
        symbol: "circle",
      },
      text: optionen.punkte.map((p) => p.text),
      hoverinfo: "text+x+y",
    };
    daten.push(punktTrace);
  }

  const layout = {
    xaxis: {
      ...(optionen.xAchse ? { title: { text: optionen.xAchse, y: 0.5 } } : {}),
      range:
        optionen.xMin !== undefined && optionen.xMax !== undefined
          ? [optionen.xMin, optionen.xMax]
          : undefined,
    },
    yaxis: {
      ...(optionen.yAchse ? { title: { text: optionen.yAchse, y: 0.5 } } : {}),
      range:
        optionen.yMin !== undefined && optionen.yMax !== undefined
          ? [optionen.yMin, optionen.yMax]
          : undefined,
    },
    hovermode: "closest",
    legend: {
      orientation: "h",
      x: 0.5,
      xanchor: "center",
      y: -0.25,
    },
    margin: { t: 40, r: 50, b: 40, l: 60 },
    dragmode: 'pan',
  };

  const config = {
    modeBarButtonsToRemove: [],
    displayModeBar: true,
    displaylogo: false,
  };

  Plotly.newPlot(containerId, daten, layout, config);
}
