---
layout: null
---
Das Diagramm zeigt die Funktionen $E(x)$, $K(x)$, $G(x)$ und $p(x)$ für ein Angebotspolypol sowie die ökonomischen Kennzahlen. 

{% include dev/graph.html
   funktionen='[
    {"name":"E(x)", "term":"-5x^2+60x", "beschreibung":"Erlösfunktion"},
    {"name":"K(x)", "term":"0.5*x^3-6*x^2+30*x+48", "beschreibung":"Kostenfunktion"},
    {"name":"G(x)", "term":"-0.5*x^3+x^2+30*x-48", "beschreibung":"Gewinnfunktion"},
    {"name":"p(x)", "term":"-5x+60", "beschreibung":"Preisfunktion"}
   ]'
   punkte='[
     {"x":0,"y":60,"text":"Höchstpreis"},
     {"x":12,"y":0,"text":"Sättigungsmenge"},
     {"x":6,"y":180,"text":"erlösmaximale Menge und maximaler Erlös"},
     {"x":0,"y":48,"text":"Fixkosten"},
     {"x":4,"y":104,"text":"Übergang vom degressiven zum progressiven Kostenwachstum"},
     {"x":1.58,"y":0,"text":"Gewinnschwelle"},
     {"x":8,"y":0,"text":"Gewinngrenze"},
     {"x":5.19,"y":64.74,"text":"gewinnmaximale Menge und maximaler Gewinn"},
     {"x":5.19,"y":34.05,"text":"Cournotscher Punkt: gewinnmaximale Menge und gewinnmaximaler Preis"},
     {"x":1.58,"y":82.32,"text":"Break-even Point"},
     {"x":8,"y":160,"text":"Break-even Point"}
   ]'
   titel="Ökonomische Funktionen"
   xachse="Menge x in ME"
   yachse="Betrag y in GE"
   xmin=0
   xmax=12.5
   ymin=-100
   ymax=250
%}
