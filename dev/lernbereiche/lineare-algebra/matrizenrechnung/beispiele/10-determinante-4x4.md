---
layout: null
---

Berechne die Determinante der Matrix

$$
A = \begin{pmatrix} 1 & 0 & 2 & -1 \\ 3 & 0 & 0 & 5 \\ 2 & 1 & 4 & -3 \\ 1 & 0 & 0 & 0 \end{pmatrix}
$$

mit Laplace-Entwicklung.

Wir entwickeln nach der **4. Zeile**, da dort drei Nullen stehen. Nur der Eintrag $a_{41} = 1$ liefert einen Beitrag:

$$
\det(A) = (-1)^{4+1} \cdot 1 \cdot \det \begin{pmatrix} 0 & 2 & -1 \\ 0 & 0 & 5 \\ 1 & 4 & -3 \end{pmatrix}
$$

Die $3 \times 3$-Determinante berechnen wir mit der Regel von Sarrus:

Produkte von links oben nach rechts unten:

$$
0 \cdot 0 \cdot (-3) + 2 \cdot 5 \cdot 1 + (-1) \cdot 0 \cdot 4 = 0 + 10 + 0 = 10
$$

Produkte von rechts oben nach links unten:

$$
(-1) \cdot 0 \cdot 1 + 0 \cdot 5 \cdot 4 + 2 \cdot 0 \cdot (-3) = 0 + 0 + 0 = 0
$$

Also:

$$
\det \begin{pmatrix} 0 & 2 & -1 \\ 0 & 0 & 5 \\ 1 & 4 & -3 \end{pmatrix} = 10 - 0 = 10
$$

Eingesetzt:

$$
\det(A) = (-1)^5 \cdot 1 \cdot 10 = -10
$$
