---
layout: null
---
Hier sehen wir ein Histogramm der Einzelwahrscheinlichkeiten. 

{% include dev/histogramm-binomial-einzel.html 
n="10" p="0.4" a="2" b="1"%} 

Die Höhe jeder Säule gibt die entsprechende "genau $k$-Treffer"-Wahrscheinlichkeit an. Daher ist z.B:

- $P(X=2)$ die Höhe der Säule über 2, also ca. $0{,}12$.
- $P(X\geq 7)$ die Summe der Höhen der Säulen über 7, 8, 9 und 10, also ca. $0{,}05$.