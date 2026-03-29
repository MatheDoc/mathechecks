---
layout: null
---
Gegeben ist das folgende unvollständige Baumdiagramm eines mehrstufigen Zufallsexperiments:

{% include dev/baumdiagramm.html
    pa="0.4"
    pba="0.3"
    pbna="0.3"
    mode="slots"
    givenSlots="{7,8}"
%}

Wie lauten die fehlenden Wahrscheinlichkeiten?

Mit Hilfe der Pfadaddtionsregel erhalten wir $①=0{,}12+0{,}28=0{,}4$ und mit Hilfe der Pfadmultiplikationsregel $
③=\frac{0{,}12}{0{,}4}=0{,}3$ und weiter $④=1-0{,}3=0{,}7$.

**Da $A$ und $B$ stochastisch unabhängig sind**, gilt $P_A(B)=P_{\overline{A}}(B)$. Somit ist $⑤=0{,}3$ und $⑥=0{,}7$.

Das restliche Baumdiagramm kann nun wie gewohnt vervollständigt werden.

- $②=1-0{,}4=0{,}6$
- $⑨=0{,}6\cdot 0{,}3=0{,}18$
- $⑩=0{,}6\cdot 0{,}7=0{,}42$


