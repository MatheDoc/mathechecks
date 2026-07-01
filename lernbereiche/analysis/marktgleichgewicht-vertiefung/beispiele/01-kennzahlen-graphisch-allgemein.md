---
layout: null
permalink: /lernbereiche/analysis/marktgleichgewicht-vertiefung/beispiele/01-kennzahlen-graphisch-allgemein.html
---
Das folgende Diagramm veranschaulicht die Kennzahlen zum Marktgleichgewicht bei allgemeineren Angebots- und Nachfragefunktionen.

{% include graph.html
   funktionen='[
    {"name":"p<sub>N</sub>(x)", "term":"-0.81*x+150", "beschreibung":"Nachfragefunktion"},
    {"name":"p<sub>A</sub>(x)", "term":"0.06*x^2+0.37*x+4.1", "beschreibung":"Angebotsfunktion"}
   ]'
    punkte='[
     {"x":0,"y":150,"text":"Höchstpreis"},
     {"x":0,"y":4.1,"text":"Mindestangebotspreis"},
     {"x":40.4495,"y":117.2359,"text":"Marktgleichgewicht: Gleichgewichtsmenge und Gleichgewichtspreis"},
     {"x":185.1852,"y":0,"text":"Sättigungsmenge"}
   ]'
   titel="Marktgleichgewicht"
   xachse="Menge x in ME"
   yachse="Preis p in GE"
   xmin=-2
   xmax=200
   ymin=-2
   ymax=175
%}
