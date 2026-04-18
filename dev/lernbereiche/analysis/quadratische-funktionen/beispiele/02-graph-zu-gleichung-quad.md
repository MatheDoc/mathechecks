---
layout: null
---

Gegeben ist der Graph einer quadratischen Funktion $f$. Bestimme die Gleichung in Scheitelpunktform und in faktorisierter Form.

{% include dev/graph.html
   funktionen='[{"name":"f(x)", "term":"-(x-1)*(x-1)+4"}]'
   punkte='[{"x":1,"y":4,"text":"S(1 | 4)"},{"x":-1,"y":0,"text":"x₁ = −1"},{"x":3,"y":0,"text":"x₂ = 3"}]'
   xmin=-3 xmax=5 ymin=-2 ymax=6
%}

- Scheitelpunktform bestimmen

    Aus dem Diagramm liest man den Scheitel ab: $S(1 \mid 4)$. Damit lautet der Ansatz:

    $$f(x) = a(x - 1)^2 + 4$$

- Öffnungsfaktor $a$ bestimmen

    Der Graph verläuft z. B. durch die Nullstelle $(3 \mid 0)$. Einsetzen:

    $$\begin{aligned}
    0 &= a(3 - 1)^2 + 4 \\
    0 &= 4a + 4 \\
    a &= -1
    \end{aligned}$$

- Scheitelpunktform

    $$f(x) = -(x - 1)^2 + 4$$

- Faktorisierte Form bestimmen

    Aus dem Diagramm liest man die Nullstellen ab: $x_1 = -1$ und $x_2 = 3$. Mit dem bereits bestimmten Öffnungsfaktor $a = -1$:

    $$f(x) = -(x + 1)(x - 3)$$

- Probe

    Ausmultiplizieren der faktorisierten Form:

    $$\begin{aligned}
    f(x) &= -(x + 1)(x - 3) \\
    &= -(x^2 - 3x + x - 3) \\
    &= -(x^2 - 2x - 3) \\
    &= -x^2 + 2x + 3
    \end{aligned}$$

    Ausmultiplizieren der Scheitelpunktform:

    $$\begin{aligned}
    f(x) &= -(x - 1)^2 + 4 \\
    &= -(x^2 - 2x + 1) + 4 \\
    &= -x^2 + 2x + 3 \quad \checkmark
    \end{aligned}$$
