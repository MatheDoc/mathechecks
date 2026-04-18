---
layout: null
---

Im Diagramm sind vier Graphen quadratischer Funktionen (a–d) dargestellt. Gefragt ist nach dem Graphen der Funktion $f(x) = x^2 - 2x - 3$.

{% include dev/graph.html
   funktionen='[{"name":"a", "term":"-(x-1)*(x-3)", "color":"#e6194b"},{"name":"b", "term":"(x+1)*(x-3)", "color":"#3cb44b"},{"name":"c", "term":"x*(x+2)", "color":"#4363d8"},{"name":"d", "term":"-(x+1)*(x-3)", "color":"#f58231"}]'
   xmin=-4 xmax=6 ymin=-5 ymax=5
%}

- Öffnungsrichtung bestimmen

    Der Koeffizient vor $x^2$ ist $a = 1 > 0$. Die Parabel öffnet nach **oben**. Damit scheiden die nach unten geöffneten Graphen **a** und **d** aus.

- $y$-Achsenabschnitt bestimmen

    Einsetzen von $x = 0$: $f(0) = 0 - 0 - 3 = -3$. Der gesuchte Graph schneidet die $y$-Achse bei $-3$. Von den beiden nach oben geöffneten Graphen (**b** und **c**) verläuft nur **b** durch den Punkt $(0 \mid -3)$.

- Zuordnung

    Der nach oben geöffnete Graph mit $y$-Achsenabschnitt $-3$ ist **Graph b**.
