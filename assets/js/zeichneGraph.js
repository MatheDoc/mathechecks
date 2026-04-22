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
        if (f.xmin !== undefined && x < f.xmin) return null;
        if (f.xmax !== undefined && x > f.xmax) return null;
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

  // Flächen (schattierte Bereiche) hinzufügen, falls vorhanden
  if (Array.isArray(optionen.flaechen)) {
    const flaechenDaten = optionen.flaechen.map((fl) => {
      const expr = math.parse(fl.term);
      const compiled = expr.compile();
      const xVon = fl.von !== undefined ? fl.von : min;
      const xBis = fl.bis !== undefined ? fl.bis : max;

      const xArea = [];
      const yArea = [];
      const numPoints = Math.ceil((xBis - xVon) / step) + 1;
      for (let i = 0; i < numPoints; i++) {
        const x = Math.min(xVon + i * step, xBis);
        xArea.push(x);
        try {
          yArea.push(compiled.evaluate({ x: x }));
        } catch (e) {
          yArea.push(null);
        }
      }

      return {
        x: xArea,
        y: yArea,
        type: "scatter",
        mode: "none",
        fill: "tozeroy",
        fillcolor: fl.farbe || "rgba(0,100,200,0.2)",
        line: { width: 0 },
        name: fl.name || "",
        showlegend: !!fl.name,
        hoverinfo: "skip",
      };
    });
    // Flächen vor die Funktionsgraphen einfügen (damit sie dahinter liegen)
    daten.unshift(...flaechenDaten);
  }

  const layout = {
    xaxis: {
      ...getPlotlyAxisDefaults(),
      ...(optionen.xAchse ? { title: { text: optionen.xAchse, y: 0.5 } } : {}),
      range:
        optionen.xMin !== undefined && optionen.xMax !== undefined
          ? [optionen.xMin, optionen.xMax]
          : undefined,
    },
    yaxis: {
      ...getPlotlyAxisDefaults(),
      ...(optionen.yAchse ? { title: { text: optionen.yAchse, y: 0.5 } } : {}),
      // Allow setting yMin or yMax independently - use null for auto
      ...(optionen.yMin !== undefined || optionen.yMax !== undefined
        ? {
          range: [
            optionen.yMin !== undefined ? optionen.yMin : null,
            optionen.yMax !== undefined ? optionen.yMax : null,
          ],
        }
        : {}),
    },
    hovermode: "closest",
    legend: {
      orientation: "h",
      x: 0.5,
      xanchor: "center",
      y: -0.25,
    },
    margin: { t: 40, r: 50, b: 40, l: 60 },
    dragmode: false,
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
  };

  const config = {
    modeBarButtonsToRemove: [],
    displayModeBar: false,
    displaylogo: false,
    scrollZoom: false,
    staticPlot: false,
    doubleClick: false,
    responsive: true,
  };

  Plotly.newPlot(containerId, daten, layout, config);
}
