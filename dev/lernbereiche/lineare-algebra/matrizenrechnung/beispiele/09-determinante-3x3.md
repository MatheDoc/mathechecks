---
layout: null
---

Berechne die Determinante der Matrix

$$
A = \begin{pmatrix} 2 & 1 & 3 \\ 0 & -1 & 4 \\ 1 & 2 & -1 \end{pmatrix}
$$

mit der Regel von Sarrus.

Wir schreiben die ersten beiden Spalten rechts neben die Matrix und bilden die Diagonalprodukte:

Produkte von links oben nach rechts unten (addieren):

$$
\begin{align*}
&2 \cdot (-1) \cdot (-1) = 2 \\
&1 \cdot 4 \cdot 1 = 4 \\
&3 \cdot 0 \cdot 2 = 0
\end{align*}
$$

Produkte von rechts oben nach links unten (subtrahieren):

$$
\begin{align*}
&3 \cdot (-1) \cdot 1 = -3 \\
&2 \cdot 4 \cdot 2 = 16 \\
&1 \cdot 0 \cdot (-1) = 0
\end{align*}
$$

Damit:

$$
\det(A) = (2 + 4 + 0) - (-3 + 16 + 0) = 6 - 13 = -7
$$
