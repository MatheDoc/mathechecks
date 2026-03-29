---
layout: null
---
Gegeben ist das folgende unvollständige Baumdiagramm eines mehrstufigen Zufallsexperiments:

{% include dev/baumdiagramm.html
    pa="0.4"
    pba="0.8"
    pbna="0.3"
    mode="slots"
    givenSlots="{3,9,10}"
%}

Wie lauten die fehlenden Wahrscheinlichkeiten?

Mit Hilfe der Pfadaddtionsregel erhalten wir

$$
②=0{,}18+0{,}42=0{,}6
$$

Die weiteren fehlenden Wahrscheinlichkeiten sind

- $①=1-0{,}6=0{,}4$
- $④=1-0{,}8=0{,}2$
- $⑤=\frac{0{,}18}{0{,6}}=0{,}3$
- $⑥=1-0{,}3=0{,}7$
- $⑦=0{,}4\cdot 0{,}8=0{,}32$
- $⑧=0{,}4\cdot 0{,}2=0{,}08$


