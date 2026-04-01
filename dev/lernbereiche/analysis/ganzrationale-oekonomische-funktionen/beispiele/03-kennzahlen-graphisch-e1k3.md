---
layout: null
---
Das Diagramm zeigt die Funktionen $E(x)$, $K(x)$, $G(x)$ und $p(x)$ für ein Angebotsmonopol mit Kapazitätsgrenze bei 13 ME sowie die ökonomischen Kennzahlen. 

{% include dev/graph.html
   funktionen='[
    {"name":"E(x)", "term":"32x", "beschreibung":"Erlösfunktion"},
    {"name":"K(x)", "term":"0.5*x^3-6*x^2+30*x+48", "beschreibung":"Kostenfunktion"},
    {"name":"G(x)", "term":"-0.5*x^3+6x^2+2*x-48", "beschreibung":"Gewinnfunktion"},
    {"name":"p(x)", "term":"32", "beschreibung":"Preisfunktion"}
   ]'
   punkte='[
     {"x":0,"y":32,"text":"Marktpreis"},
     {"x":13,"y":0,"text":"Kapazitätsgrenze"},
     {"x":13,"y":416,"text":"erlösmaximale Menge und maximaler Erlös"},
     {"x":0,"y":48,"text":"Fixkosten"},
     {"x":4,"y":104,"text":"Übergang vom degressiven zum progressiven Kostenwachstum"},
     {"x":3.06,"y":0,"text":"Gewinnschwelle"},
     {"x":11.63,"y":0,"text":"Gewinngrenze"},
     {"x":8.16,"y":96.16,"text":"gewinnmaximale Menge und maximaler Gewinn"},
     {"x":3.06,"y":97.92,"text":"Break-even Point"},
     {"x":11.63,"y":372.16,"text":"Break-even Point"}
   ]'
   titel="Ökonomische Funktionen"
   xachse="Menge x in ME"
   yachse="Betrag y in GE"
   xmin=0
   xmax=14
   ymin=-100
   ymax=450
%}