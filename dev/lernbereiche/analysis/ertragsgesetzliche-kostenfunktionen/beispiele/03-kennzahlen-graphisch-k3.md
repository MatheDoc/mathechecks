---
layout: null
---
Die Kostenkennzahlen lassen wie folgt graphisch veranschaulichen.

{% include dev/graph.html
   funktionen='[
    {"name":"K\u2032(x)", "term":"1.5*x^2-12*x+30", "beschreibung":"Grenzkostenfunktion"},
    {"name":"k(x)", "term":"0.5*x^2-6*x+30+48/x", "beschreibung":"Stückkostenfunktion"},
    {"name":"k<sub>v</sub>(x)", "term":"0.5*x^2-6*x+30", "beschreibung":"variable Stückkostenfunktion"}
   ]'
   punkte='[
     {"x":4,"y":6,"text":"Übergang von einem degressiven zu einem progressiven Kostenwachstum"},
     {"x":6,"y":12,"text":"BM und LPU"},
     {"x":6.98,"y":19.36,"text":"BO und KPU"}
   ]'
   titel="Kostenfunktionen"
   xachse="Menge x in ME"
   yachse="Betrag y in GE"
   xmin=0
   xmax=12.5
   ymin=0
   ymax=80
%}