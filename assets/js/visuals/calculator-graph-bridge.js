import { buildGraphFigure } from "./graph.js";
import { plotlyRender } from "./plotly-defaults.js?v=20260507-plotly-hover-name-theme";

export function renderCalculatorGraph(container, funktionen, optionen = {}) {
    const figure = buildGraphFigure({
        funktionen,
        punkte: Array.isArray(optionen.punkte) ? optionen.punkte : null,
        flaechen: Array.isArray(optionen.flaechen) ? optionen.flaechen : null,
        titel: optionen.titel || "",
        xAchse: optionen.xAchse || "",
        yAchse: optionen.yAchse || "",
        xMin: typeof optionen.xMin === "number" ? optionen.xMin : -5,
        xMax: typeof optionen.xMax === "number" ? optionen.xMax : 20,
        yMin: typeof optionen.yMin === "number" ? optionen.yMin : null,
        yMax: typeof optionen.yMax === "number" ? optionen.yMax : null,
    });

    return plotlyRender(container, figure.data, figure.layout);
}

window.renderCalculatorGraph = renderCalculatorGraph;