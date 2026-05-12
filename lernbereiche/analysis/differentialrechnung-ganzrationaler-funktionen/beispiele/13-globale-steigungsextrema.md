---
layout: null
permalink: /lernbereiche/analysis/differentialrechnung-ganzrationaler-funktionen/beispiele/13-globale-steigungsextrema.html
---

Bestimme die Stellen maximaler und minimaler Steigung der Funktion $f(x)=x^3-3x^2+1$ auf dem Intervall $D=[0;3]$.

Gesucht sind die globalen Extremwerte der Steigungsfunktion $f'$ auf dem Intervall $[0;3]$.

- Erste Ableitung bilden

    $$f'(x)=3x^2-6x$$

- Innere Kandidaten von $f'$ bestimmen

    Dazu wird $f'$ selbst wieder abgeleitet:

    $$f''(x)=6x-6$$

    $$\begin{aligned}
    f''(x) &= 0 \\
    6x-6 &= 0 \\
    x &= 1
    \end{aligned}$$

    Als Kandidaten für maximale oder minimale Steigung kommen also $x=1$ sowie die Randpunkte $x=0$ und $x=3$ infrage.

- Werte von $f'$ vergleichen

    $$\begin{aligned}
    f'(0) &= 3\cdot 0^2-6\cdot 0 = 0 \\
    f'(1) &= 3\cdot 1^2-6\cdot 1 = -3 \\
    f'(3) &= 3\cdot 3^2-6\cdot 3 = 27-18 = 9
    \end{aligned}$$

- Ergebnis

    Die **minimale Steigung** liegt bei

    $$x=1 \quad\text{mit}\quad f'(1)=-3.$$

    Die **maximale Steigung** liegt bei

    $$x=3 \quad\text{mit}\quad f'(3)=9.$$
