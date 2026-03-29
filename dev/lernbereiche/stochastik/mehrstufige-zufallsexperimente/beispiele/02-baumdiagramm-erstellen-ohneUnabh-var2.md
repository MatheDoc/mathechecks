---
layout: null
---
Gegeben ist das folgende unvollständige Baumdiagramm eines mehrstufigen Zufallsexperiments:

{% include dev/baumdiagramm.html
    pa="0.4"
    pba="0.9"
    pbna="0.2"
    mode="slots"
    givenSlots="{1,5,7}"
%}

Wie lauten die fehlenden Wahrscheinlichkeiten?

Die Summe aller Wahrscheinlichkeiten aller Pfade, die von einem Knoten starten, ist immer 1. Daher ist

- $②=1-0{,}4=0{,}6$
- $⑥=1-0{,}2=0{,}8$

Mit Hilfe der Pfadmultiplikationsregel erhalten wir außerdem

- $⑨=0{,}6\cdot 0{,}2=0{,}12$ 
- $⑩=0{,}6\cdot 0{,}8=0{,}48$


Die fehlenden Wahrscheinlichkeit ③ der zweiten Stufe können wir berechnen, indem wir die Pfadmultiplikationsregel umstellen:

$$
0{,}4\cdot ③=0{,}36 \Rightarrow ③=\frac{0{,}36}{0{,}4}=0{,}9 
$$

Die weiteren fehlenden Wahrscheinlichkeiten sind

- $④=1-0{,}9=0{,}1$
- $⑧=0{,}4\cdot 0{,}1=0{,}04$


