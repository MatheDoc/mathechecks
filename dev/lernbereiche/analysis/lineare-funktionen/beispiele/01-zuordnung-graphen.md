---
layout: null
---

Im Diagramm sind fünf Graphen linearer Funktionen (a–e) dargestellt. Gefragt ist nach dem Graphen der Funktion $ f(x) = -2x + 3 $.

{% include dev/graph.html
   funktionen='[{"name":"a", "term":"0.5*x+3", "color":"#e6194b"},{"name":"b", "term":"1*x-1", "color":"#3cb44b"},{"name":"c", "term":"-2*x+3", "color":"#4363d8"},{"name":"d", "term":"-1*x-2", "color":"#f58231"},{"name":"e", "term":"2*x+3", "color":"#911eb4"}]'
   xmin=-4 xmax=5 ymin=-6 ymax=7
%}

- $y$-Achsenabschnitt bestimmen

    Der Graph schneidet die $y$-Achse bei $b = 3$. Das schränkt die Auswahl auf die Graphen ein, die durch den Punkt $(0 \mid 3)$ verlaufen — das sind **a**, **c** und **e**.

- Steigung prüfen

    Die Steigung ist $m = -2 < 0$, der Graph muss also von links nach rechts fallen. Pro Schritt nach rechts geht es 2 Einheiten nach unten. Von den drei Kandidaten fällt nur einer.

- Zuordnung

    Der Graph, der bei $(0 \mid 3)$ startet und mit Steigung $-2$ fällt, ist **Graph c**.
