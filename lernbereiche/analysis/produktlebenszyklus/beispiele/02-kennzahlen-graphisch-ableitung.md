---
layout: null
permalink: /lernbereiche/analysis/produktlebenszyklus/beispiele/02-kennzahlen-graphisch-ableitung.html
---
Der monatliche Absatz eines Produkts wird durch $a(t)=t^2\cdot e^{-0{,}25t}+3$ beschrieben ($t$ in Monaten, $a(t)$ in ME/Monat). Das Diagramm zeigt den Graphen der Ableitung $a'$:

{% include graph.html
   funktionen='[
    {"name":"a\u2032(t)", "term":"(2*x-0.25*x^2)*exp(-0.25*x)", "beschreibung":"Änderungsrate des monatlichen Absatzes"}
   ]'
   punkte='[
     {"x":2.34,"y":1.84,"text":"Hochpunkt von a′: stärkster Anstieg"},
     {"x":8,"y":0,"text":"Nullstelle mit VZW + → −: höchster Absatz"},
     {"x":13.66,"y":-0.64,"text":"Tiefpunkt von a′: stärkster Rückgang"}
   ]'
   titel="Graph der Ableitung a′"
   xachse="Zeit t in Monaten"
   yachse="a′(t) in ME/Monat pro Monat"
   xmin=0
   xmax=30
   ymin=-1
   ymax=2.2
%}

Aus dem Graphen von $a'$ lesen wir ab:

- **Absatz nimmt zu bzw. ab:** Für $0<t<8$ liegt der Graph oberhalb der $t$-Achse, der Absatz steigt. Für $t>8$ liegt er unterhalb, der Absatz sinkt.
- **Zeitpunkt des höchsten Absatzes:** Nullstelle von $a'$ mit Vorzeichenwechsel von $+$ nach $-$, hier nach $8$ Monaten. Die *Höhe* des Absatzes lässt sich aus dem Graphen von $a'$ nicht ablesen.
- **Stärkster Anstieg:** Hochpunkt von $a'$, hier nach ca. $2{,}3$ Monaten. Der Absatz wächst dort um ca. $1{,}8$ ME/Monat pro Monat.
- **Stärkster Rückgang:** Tiefpunkt von $a'$, hier nach ca. $13{,}7$ Monaten. Der Absatz sinkt dort um ca. $0{,}6$ ME/Monat pro Monat.
- **Randstellen:** Ist der Graph von $a'$ bei $t=0$ am höchsten (bzw. tiefsten), liegt der stärkste Anstieg (bzw. Rückgang) bei der Markteinführung, auch ohne Hochpunkt (bzw. Tiefpunkt) von $a'$.
