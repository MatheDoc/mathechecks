---
layout: null
---

Gegeben ist der Graph einer linearen Funktion $f$. Bestimme die Funktionsgleichung.

{% include dev/graph.html
   funktionen='[{"name":"f(x)", "term":"1*x+2"}]'
   punkte='[{"x":0,"y":2,"text":"(0 | 2)"},{"x":3,"y":5,"text":"(3 | 5)"}]'
   xmin=-1 xmax=6 ymin=-1 ymax=7
%}

- $y$-Achsenabschnitt ablesen

    Der Graph schneidet die $y$-Achse bei $y = 2$. Das ist der $y$-Achsenabschnitt $b$.

    $$b = 2$$

- Steigung ablesen

    Vom Punkt $(0 \mid 2)$ zum Punkt $(3 \mid 5)$: Wenn $x$ um $3$ wächst, wächst $y$ um $3$.

    $$m = \frac{\Delta y}{\Delta x} = \frac{5 - 2}{3 - 0} = \frac{3}{3} = 1$$

    Alternativ: Vom Gitter ablesen — ein Kästchen nach rechts, ein Kästchen nach oben.

- Funktionsgleichung aufstellen

    $$f(x) = mx + b = x + 2$$
