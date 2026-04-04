---
layout: null
---
{% include dev/graph.html
   funktionen='[
    {"name":"u\u2032(t)", "term":"(0.4*x^2-8.8*x+24)*exp(-0.2*x)", "beschreibung":"Ableitung der Umsatzfunktion"}
   ]'
   punkte='[
     {"x":3.19,"y":0,"text":"Nullstelle: max. Umsatz"},
     {"x":0,"y":24,"text":"stärkster Anstieg"},
     {"x":6.73,"y":-3.16,"text":"stärkster Rückgang"}
   ]'
   titel="Ableitung der Produktlebenszyklusfunktion"
   xachse="Zeit t in Jahren"
   yachse="Veränderung u\u2032(t) in GE/Jahr"
   xmin=0
   xmax=16
   ymin=-5
   ymax=28
%}

Aus dem Graphen der Ableitungsfunktion lassen sich folgende Kennzahlen ablesen:

- Zeitpunkt des höchsten jährlichen Umsatzes: Die Nullstelle von $u^{\prime}(t)$ mit Vorzeichenwechsel von $+$ nach $-$ (hier bei $t \approx 3{,}2$). An dieser Stelle hat $u$ ein Maximum.
- Zeitpunkt des stärksten Umsatzanstiegs: Die Stelle, an der $u^{\prime}(t)$ den größten Wert annimmt (globales Maximum von $u^{\prime}$, hier bei $t=0$). Achtung: Das muss kein lokaler Hochpunkt von $u^{\prime}$ sein – oft liegt der stärkste Anstieg am Rand des Definitionsbereichs (z. B. bei der Produkteinführung).
- Zeitpunkt des stärksten Umsatzrückgangs: Die Stelle, an der $u^{\prime}(t)$ den kleinsten Wert annimmt (globales Minimum von $u^{\prime}$, hier bei $t \approx 6{,}7$). Auch hier kann der Rand relevant sein.
- Jährliche Veränderung des Umsatzes nach $t_0$ Jahren: Der Funktionswert $u^{\prime}(t_0)$.