---
layout: null
---
Gegeben ist das folgende unvollständige Baumdiagramm eines mehrstufigen Zufallsexperiments:

{% include dev/baumdiagramm.html
    pa="0.3"
    pba="0.5"
    pbna="0.8"
    mode="slots"
    givenSlots="{1,3,6}"
%}

Wie lauten die fehlenden Wahrscheinlichkeiten?

Die Summe aller Wahrscheinlichkeiten aller Pfade, die von einem Knoten starten, ist immer 1. Daher ist

- $②=1-0{,}3=0{,}7$
- $④=1-0{,}5=0{,}5$
- $⑤=1-0{,}8=0{,}2$

Die fehlenden Pfadendwahrscheinlichkeiten können wir nun mithilfe der Pfadmultiplikationsregel berechnen:

- $⑦=0{,}3\cdot 0{,}5=0{,}15$
- $⑧=0{,}3\cdot 0{,}5=0{,}15$
- $⑨=0{,}7\cdot 0{,}8=0{,}56$
- $⑩=0{,}7\cdot 0{,}2=0{,}14$