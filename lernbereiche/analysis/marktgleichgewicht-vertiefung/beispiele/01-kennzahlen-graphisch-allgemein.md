---
layout: null
permalink: /lernbereiche/analysis/marktgleichgewicht-vertiefung/beispiele/01-kennzahlen-graphisch-allgemein.html
---
Das Diagramm zeigt die Graphen der Nachfragefunktion $p_N$ und der Angebotsfunktion $p_A$ eines Marktes. Bestimmen Sie anhand des Diagramms den Höchstpreis, die Sättigungsmenge, den Mindestangebotspreis, das Marktgleichgewicht und den Umsatz im Marktgleichgewicht.

{% include graph.html
   funktionen='[
    {"name":"p<sub>N</sub>(x)", "term":"-0.81*x+150", "beschreibung":"Nachfragefunktion", "color":"#1f77b4"},
    {"name":"p<sub>A</sub>(x)", "term":"0.06*x^2+0.37*x+4.1", "beschreibung":"Angebotsfunktion", "color":"#d62728"}
   ]'
   flaechen='[
    {"term":"117.2359", "von":0, "bis":40.4495, "farbe":"rgba(120,120,120,0.25)", "name":"Umsatz im Marktgleichgewicht"}
   ]'
   punkte='[
    {"x":0,"y":150,"text":"Höchstpreis"},
    {"x":0,"y":4.1,"text":"Mindestangebotspreis"},
    {"x":40.4495,"y":117.2359,"text":"Marktgleichgewicht"},
    {"x":185.1852,"y":0,"text":"Sättigungsmenge"}
   ]'
   hilfslinien='[
    {"x":40.4495,"y":117.2359,"xLabel":"x<sub>G</sub>","yLabel":"p<sub>G</sub>"}
   ]'
   titel="Angebot und Nachfrage"
   xachse="Menge x in ME"
   yachse="Preis p in GE/ME"
   xmin=0
   xmax=200
   ymin=0
   ymax=175
%}

- **Höchstpreis:** Der Graph von $p_N$ schneidet die $y$-Achse bei $150$. Der Höchstpreis beträgt $150$ GE/ME.
- **Sättigungsmenge:** Der Graph von $p_N$ schneidet die $x$-Achse bei etwa $185$. Die Sättigungsmenge beträgt etwa $185$ ME.
- **Mindestangebotspreis:** Der Graph von $p_A$ schneidet die $y$-Achse bei etwa $4$. Der Mindestangebotspreis beträgt etwa $4$ GE/ME.
- **Marktgleichgewicht:** Die Graphen schneiden sich etwa im Punkt $(40\mid 117)$. Die Gleichgewichtsmenge beträgt etwa $40$ ME, der Gleichgewichtspreis etwa $117$ GE/ME.
- **Umsatz im Marktgleichgewicht:** Das ist die Fläche des grauen Rechtecks mit den Seitenlängen $x_G$ und $p_G$:

  $$
  x_G\cdot p_G\approx 40\cdot 117=4680
  $$

  Der Umsatz im Marktgleichgewicht beträgt etwa $4680$ GE. Abgelesene Werte sind Näherungen; mit den exakten Werten ergibt sich $4742{,}13$ GE.
