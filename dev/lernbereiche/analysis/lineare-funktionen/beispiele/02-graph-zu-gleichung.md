---
layout: null
---

Gegeben ist der Graph einer linearen Funktion $f$. Bestimme die Funktionsgleichung.

{% include dev/graph.html
   funktionen='[{"name":"f(x)", "term":"2*x+1"}]'
   punkte='[{"x":0,"y":1,"text":"(0 | 1)"},{"x":2,"y":5,"text":"(2 | 5)"}]'
   xmin=-1 xmax=5 ymin=-1 ymax=7
%}

- $y$-Achsenabschnitt ablesen

    Der Graph schneidet die $y$-Achse bei $y = 1$. Das ist der $y$-Achsenabschnitt $b$.

    $$b = 1$$

- Steigung ablesen

    Vom Punkt $(0 \mid 1)$ zum Punkt $(2 \mid 5)$: Wenn $x$ um $2$ wächst, wächst $y$ um $4$.

    $$m = \frac{\Delta y}{\Delta x} = \frac{5 - 1}{2 - 0} = \frac{4}{2} = 2$$

    Alternativ: Vom Gitter ablesen — ein Kästchen nach rechts, zwei Kästchen nach oben.

- Funktionsgleichung aufstellen

    $$f(x) = mx + b = 2x + 1$$
