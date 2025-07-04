function fakultaet(k) {
  if (k === 0 || k === 1) return 1;
  let f = 1;
  for (let i = 2; i <= k; i++) f *= i;
  return f;
}

function binomial(n, k, p) {
  const komb = fakultaet(n) / (fakultaet(k) * fakultaet(n - k));
  return komb * Math.pow(p, k) * Math.pow(1 - p, n - k);
}

function zeichneHistogrammEinzeln(
  n,
  p,
  a = null,
  b = null,
  divID,
  titel = "",
  autoY = true,
  anzeigeID = null
) {
  const xWerte = [];
  const yWerte = [];
  const farben = [];
  let summe = 0;
  const yKumuliert = [];

  for (let k = 0; k <= n; k++) {
    const wkt = binomial(n, k, p);
    summe += wkt;
    xWerte.push(k);
    yWerte.push(wkt);
    yKumuliert.push(summe);
    if (a !== null && b !== null && k >= a && k <= b) {
      farben.push("rgba(5, 56, 166, 0.6)");
    } else {
      farben.push("rgba(54, 162, 235, 0.4)");
    }
  }

  // Nur wenn eine Anzeige-ID übergeben wurde
  if (anzeigeID && a !== null && b !== null) {
    const element = document.getElementById(anzeigeID);
    if (element) {
      const P_b = yKumuliert[b] ?? 0;
      const P_vor_a = a > 0 ? yKumuliert[a - 1] : 0;
      let P_intervall = a > b ? 0 : P_b - P_vor_a;
      element.innerHTML = `$ P(${a} ≤ X ≤ ${b}) = ${P_intervall.toFixed(4)} $`;
      if (window.MathJax && MathJax.typesetPromise) {
        MathJax.typesetPromise([element]);
      }
    }
  }

  const spur = {
    x: xWerte,
    y: yWerte,
    type: "bar",
    marker: {
      color: farben,
      line: {
        color: "rgba(0, 0, 0, 0.5)",
        width: 1,
      },
    },
    name: "P(X = k)",
  };

  const layout = {
    title: {
      text: titel,
      y: 0.85,
    },
    xaxis: { title: "k", tickmode: "linear" },
    yaxis: { title: "P(X = k)", range: autoY ? undefined : [0, 1] },
    bargap: 0,
    dragmode: false,
  };

  const config = {
    scrollZoom: false,
    responsive: true,
  };

  Plotly.newPlot(divID, [spur], layout, config);
}

function zeichneHistogrammKumuliert(n, p, a, b, divID, titel = "") {
  const xWerte = [];
  const yKumuliert = [];
  let summe = 0;

  for (let k = 0; k <= n; k++) {
    const wkt = binomial(n, k, p);
    summe += wkt;
    xWerte.push(k);
    yKumuliert.push(summe);
  }

  const farben = xWerte.map((k) => {
    if (k === b) return "rgba(255, 160, 160, 0.6)";
    if (k === a - 1) return "rgba(255, 160, 160, 0.6)";
    return "rgba(100, 100, 100, 0.2)";
  });

  const spur = {
    x: xWerte,
    y: yKumuliert,
    type: "bar",
    marker: {
      color: farben,
      line: {
        color: "rgba(50, 50, 50, 0.5)",
        width: 1,
      },
    },
    name: "P(X ≤ k)",
  };

  const xPfeil = a - 1; // Mittig über der Säule bei k = a-1
  const yUnten = yKumuliert[a - 1]; // Unten bei 0
  const yOben = yKumuliert[b]; // Oben bei P(X ≤ b)

  const layout = {
    title: {
      text: titel,
      y: 0.85,
    },
    xaxis: { title: "k", tickmode: "linear" },
    yaxis: { title: "P(X ≤ k)", range: [0, 1.05] },
    bargap: 0,
    dragmode: false,
    shapes: [
      // Vertikale durchgezogene Linie
      {
        type: "line",
        x0: xPfeil,
        x1: xPfeil,
        y0: yUnten,
        y1: yOben,
        line: {
          color: "black",
          width: 2,
          dash: "solid",
        },
      },
      // Pfeil oben (nach oben zeigend)
      {
        type: "path",
        path: `M ${xPfeil - 0.05} ${yOben - 0.02} L ${xPfeil} ${yOben} L ${
          xPfeil + 0.05
        } ${yOben - 0.02} Z`,
        fillcolor: "black",
        line: { color: "black" },
      },
      // Pfeil unten (nach unten zeigend)
      {
        type: "path",
        path: `M ${xPfeil - 0.05} ${yUnten + 0.02} L ${xPfeil} ${yUnten} L ${
          xPfeil + 0.05
        } ${yUnten + 0.02} Z`,
        fillcolor: "black",
        line: { color: "black" },
      },
      // Horizontale Linie von der oberen Pfeilspitze bis rechts (x = n)
      {
        type: "line",
        x0: xPfeil,
        x1: b,
        y0: yOben,
        y1: yOben,
        line: {
          color: "black",
          width: 2,
          dash: "dash",
        },
      },
    ],
  };

  const config = {
    scrollZoom: false,
    responsive: true,
  };

  Plotly.newPlot(divID, [spur], layout, config);
}
