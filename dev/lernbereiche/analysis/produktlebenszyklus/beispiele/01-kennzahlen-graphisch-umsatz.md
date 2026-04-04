---
layout: null
---
Das folgende Diagramm zeigt zwei typische Produktlebenszyklusfunktionen:

{% include dev/graph.html
   funktionen='[
    {"name":"u₁(t)", "term":"(-1*x^2+20*x)*exp(-0.2*x)", "beschreibung":"Marktaustritt", "xmin":0, "xmax":20},
    {"name":"u₂(t)", "term":"(3*x^2+8)*exp(-0.3*x)+2", "beschreibung":"langfristiger Umsatz", "xmin":0}
   ]'
   punkte='[
     {"x":0,"y":0,"text":"u₁(0)=0, stärkster Anstieg u₁"},
     {"x":3.82,"y":28.8,"text":"max. Umsatz u₁"},
     {"x":7.75,"y":20.14,"text":"stärkster Rückgang u₁"},
     {"x":20,"y":0,"text":"Marktaustritt"},
     {"x":0,"y":10,"text":"u₂(0)=10"},
     {"x":2.24,"y":13.79,"text":"stärkster Anstieg u₂"},
     {"x":6.24,"y":21.18,"text":"max. Umsatz u₂"},
     {"x":11.09,"y":15.54,"text":"stärkster Rückgang u₂"},
     {"x":26,"y":2.3,"text":"langfristiger Umsatz → 2"}
   ]'
   titel="Zwei Typen von Produktlebenszyklusfunktionen"
   xachse="Zeit t in Jahren"
   yachse="jährlicher Umsatz in GE"
  xmin=0
   xmax=30
   ymin=-3
   ymax=35
%}
Wir erkennen zwei unterschiedliche langfristige Verläufe von Produktlebenszyklen:

- $u_1$ (Marktaustritt): Der Umsatz sinkt bei $t=20$ auf null, da $u_1$ hier die $t$- Achse schneidet. Das Produkt wird vom Markt genommen.
- $u_2$ (langfristiger Umsatz): Der Umsatz nähert sich langfristig dem Wert $2$ GE an, da der Graph von $u_2$ sich asymptotisch der Gerade $y=2$ nähert. Das Produkt bleibt dauerhaft auf dem Markt.
