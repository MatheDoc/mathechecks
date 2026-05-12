---
layout: null
permalink: /lernbereiche/analysis/differentialrechnung-ganzrationaler-funktionen/beispiele/06-extremstellen-bestimmen.html
---

Bestimme Hochpunkt und Tiefpunkt der Funktion $f(x)=x^3-3x+1$.

- Notwendige Bedingung prüfen

    $$\begin{aligned}
    f'(x) &= 3x^2-3 \\
    3x^2-3 &= 0 \\
    x^2-1 &= 0 \\
    x &= -1 \text{ oder } x=1
    \end{aligned}$$

    Das sind die Kandidaten für Extremstellen.

- Hinreichende Bedingung prüfen

    $$f''(x)=6x$$

    $$f''(-1)=-6<0 \quad\Rightarrow\quad \text{Hochpunkt}$$

    $$f''(1)=6>0 \quad\Rightarrow\quad \text{Tiefpunkt}$$

- Zugehörige y-Werte berechnen

    $$\begin{aligned}
    f(-1) &= (-1)^3-3\cdot(-1)+1 = -1+3+1 = 3 \\
    f(1) &= 1^3-3\cdot 1+1 = 1-3+1 = -1
    \end{aligned}$$

- Ergebnis

    $$H(-1\mid 3), \qquad T(1\mid -1)$$
