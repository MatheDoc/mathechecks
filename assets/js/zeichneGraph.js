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

  // HIER kommen die zusätzlichen Punkte dazu
  if (Array.isArray(optionen.punkte)) {
    const punktTrace = {
      x: optionen.punkte.map((p) => p.x),
      y: optionen.punkte.map((p) => p.y),
      mode: "markers",
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
    title: {
      text: optionen.titel || "",
      y: 0.9,
    },
    xaxis: {
      title: {
        text: optionen.xAchse || "x",
        y: 0.5,
      },
      range:
        optionen.xMin !== undefined && optionen.xMax !== undefined
          ? [optionen.xMin, optionen.xMax]
          : undefined,
    },
    yaxis: {
      title: {
        text: optionen.yAchse || "f(x)",
        y: 0.5,
      },
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
    margin: { t: 100, r: 50, b: 40, l: 60 },
  };

  Plotly.newPlot(containerId, daten, layout);
}
