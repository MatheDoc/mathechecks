---
layout: null
permalink: /lernbereiche/analysis/differentialrechnung-ganzrationaler-funktionen/beispiele/05-ableitungsgraph-folgern.html
---

Das Diagramm zeigt den Graphen der ersten Ableitung $f'(x)=-x^2+2x+3$ einer ganzrationalen Funktion $f$.

{% include graph.html
   funktionen='[{"name":"f\u2032", "term":"-x^2+2*x+3", "color":"#4363d8"}]'
   xmin=-3 xmax=5 ymin=-3 ymax=5
%}

Bestimme die $x$-Werte aller Hochpunkte, Tiefpunkte und Wendestellen von $f$.

- Nullstellen von $f'$ bestimmen

    $$\begin{aligned}
    -x^2+2x+3 &= 0 \\
    x^2-2x-3 &= 0 \\
    (x-3)(x+1) &= 0
    \end{aligned}$$

    Also sind die Nullstellen von $f'$: $x=-1$ und $x=3$.

- Vorzeichen von $f'$ aus dem Graphen ablesen

    Links von $x=-1$ liegt der Graph von $f'$ unter der $x$-Achse, zwischen $-1$ und $3$ darüber, rechts von $3$ wieder darunter.

    Daher gilt:

    - bei $x=-1$: Vorzeichenwechsel von $-$ nach $+$, also **Tiefpunkt** von $f$
    - bei $x=3$: Vorzeichenwechsel von $+$ nach $-$, also **Hochpunkt** von $f$

- Wendestelle von $f$ bestimmen

    Wendestellen von $f$ entsprechen Extremstellen von $f'$. Der Graph von $f'$ ist eine nach unten geöffnete Parabel mit Hochpunkt bei

    $$x = -\frac{b}{2a} = -\frac{2}{2\cdot (-1)} = 1.$$

    Also hat $f$ bei $x=1$ eine Wendestelle. Da $f'$ dort einen Hochpunkt hat, wechselt $f$ von linksgekrümmt nach rechtsgekrümmt.

- Ergebnis

    $$\text{Tiefpunkt bei } x=-1, \qquad \text{Hochpunkt bei } x=3, \qquad \text{Wendestelle bei } x=1$$

