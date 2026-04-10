---
layout: null
---

Gegeben sind die Matrizen

$$
A = \begin{pmatrix} 2 & -1 & 3 \\ 0 & 4 & 1 \end{pmatrix}, \quad
B = \begin{pmatrix} 1 & 5 \\ -2 & 0 \\ 3 & 1 \end{pmatrix}.
$$

Berechne $A \cdot B$.

$A$ ist eine $2 \times 3$-Matrix und $B$ eine $3 \times 2$-Matrix. Die Spaltenanzahl von $A$ (3) stimmt mit der Zeilenanzahl von $B$ (3) überein, das Produkt ist also definiert. Das Ergebnis ist eine $2 \times 2$-Matrix.

Wir berechnen die Einträge nach dem Zeile-mal-Spalte-Prinzip:

$$
\begin{align*}
c_{11} &= 2 \cdot 1 + (-1) \cdot (-2) + 3 \cdot 3 = 2 + 2 + 9 = 13 \\
c_{12} &= 2 \cdot 5 + (-1) \cdot 0 + 3 \cdot 1 = 10 + 0 + 3 = 13 \\
c_{21} &= 0 \cdot 1 + 4 \cdot (-2) + 1 \cdot 3 = 0 - 8 + 3 = -5 \\
c_{22} &= 0 \cdot 5 + 4 \cdot 0 + 1 \cdot 1 = 0 + 0 + 1 = 1
\end{align*}
$$

Also:

$$
A \cdot B = \begin{pmatrix} 13 & 13 \\ -5 & 1 \end{pmatrix}
$$
