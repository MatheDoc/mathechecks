---
layout: null
permalink: /lernbereiche/analysis/differentialrechnung-ganzrationaler-funktionen/beispiele/04-graphische-deutung-ableitungen.html
---

Die fünf Graphen $a$ bis $e$ zeigen die Funktionen $f$, $f'$, $g$, $g'$ sowie einen zusätzlichen Störgraphen. Zusätzlich ist bekannt: $g(0)=1$.

{% include graph.html
   funktionen='[{"name":"a", "term":"2*x", "color":"#e6194b"},{"name":"b", "term":"x^2-2", "color":"#3cb44b"},{"name":"c", "term":"-x^3+3*x+1", "color":"#4363d8"},{"name":"d", "term":"-3*x^2+3", "color":"#f58231"},{"name":"e", "term":"x^3-3*x", "color":"#911eb4"}]'
   xmin=-3 xmax=3 ymin=-6 ymax=6
%}

- Zuerst $g$ identifizieren

    Aus $g(0)=1$ folgt: Der Graph von $g$ muss die $y$-Achse bei $1$ schneiden. Das trifft nur auf **Graph $c$** zu.

- Dann $g'$ bestimmen

    Der Graph von $g$ ist kubisch. Seine Ableitung ist also quadratisch. Außerdem hat $g$ einen Hoch- und einen Tiefpunkt, daher muss $g'$ zwei Nullstellen besitzen. Das passt zu **Graph $d$**.

- Das verbleibende Funktions-Ableitungs-Paar untersuchen

    Übrig bleiben **Graph $a$** und **Graph $b$**. Graph $b$ ist eine Parabel, Graph $a$ eine Gerade. Das passt zu $f$ und $f'$.

    Zusätzlich hat Graph $b$ bei $x=0$ eine waagrechte Tangente. Genau dort hat Graph $a$ eine Nullstelle. Also gilt:

    $$f=b \quad\text{und}\quad f'=a$$

- Ergebnis

    $$f=b, \quad f'=a, \quad g=c, \quad g'=d$$

