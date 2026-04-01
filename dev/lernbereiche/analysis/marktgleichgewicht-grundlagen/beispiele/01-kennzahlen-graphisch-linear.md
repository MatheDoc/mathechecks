---
layout: null
---
Das folgende Diagramm veranschaulicht die Kennzahlen zum Marktgleichgewicht.

{% include dev/graph.html
   funktionen='[
    {"name":"p<sub>N</sub>(x)", "term":"-2*x+42", "beschreibung":"Nachfragefunktion"},
    {"name":"p<sub>A</sub>(x)", "term":"1.5x+14", "beschreibung":"Angebotsfunktion"}
   ]'
    punkte='[
     {"x":0,"y":42,"text":"Höchstpreis"},
     {"x":0,"y":14,"text":"Mindesangebotspreis"},
     {"x":8,"y":26,"text":"Marktgleichgewicht: Gleichgewichtsmenge und Gleichgewichtspreis"},
     {"x":21,"y":0,"text":"Sättigungsmenge"}
   ]'
   titel="Marktgleichgewicht"
   xachse="Menge x in ME"
   yachse="Betrag y in GE"
   xmin=-0.2
   xmax=22
   ymin=-1
   ymax=50
%}