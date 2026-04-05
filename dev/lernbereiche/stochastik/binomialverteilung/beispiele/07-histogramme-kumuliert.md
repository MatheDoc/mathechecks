---
layout: null
---
Hier sehen wir ein Histogramm der kumulierten Wahrscheinlichkeiten. 

{% include dev/histogramm-binomial-kumuliert.html n="10" p="0.4" a="5" b="5" %}

Die Höhe jeder Säule gibt die entsprechende "höchstens $k$-Treffer"-Wahrscheinlichkeit an. Daher ist z.B:

- $P(X\leq 2)$ die Höhe der Säule über 2, also ca. $0{,}65$.
- $P(X=5)$ die Differenz der Höhen der Säulen über 5 und 4, da $P(X=5)=P(X\leq 5)-P(X\leq 4)$, also ca. $0{,}83-0{,}63=0{,}2$ (siehe Markierung).
- $P(X\geq 7)$ die Differenz von 1 und der Höhe der Säule über 6, da $P(X\geq 7)=1-P(X\leq 6)$, also ca. $1-0{,}95=0{,}05$.