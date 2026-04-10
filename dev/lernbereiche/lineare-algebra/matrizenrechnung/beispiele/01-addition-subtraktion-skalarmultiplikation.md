---
layout: null
---

Gegeben sind die Matrizen

$$
A = \begin{pmatrix} 3 & -1 \\ 2 & 4 \\ 0 & 5 \end{pmatrix}, \quad
B = \begin{pmatrix} 1 & 2 \\ -3 & 0 \\ 4 & -1 \end{pmatrix}
$$

und der Skalar $\lambda = -2$.

Berechne $\lambda \cdot (A + B) - A$.

**Schritt 1:** Addition $A + B$

$$
A + B = \begin{pmatrix} 3+1 & -1+2 \\ 2+(-3) & 4+0 \\ 0+4 & 5+(-1) \end{pmatrix} = \begin{pmatrix} 4 & 1 \\ -1 & 4 \\ 4 & 4 \end{pmatrix}
$$

**Schritt 2:** Skalarmultiplikation $\lambda \cdot (A+B)$

$$
-2 \cdot \begin{pmatrix} 4 & 1 \\ -1 & 4 \\ 4 & 4 \end{pmatrix} = \begin{pmatrix} -8 & -2 \\ 2 & -8 \\ -8 & -8 \end{pmatrix}
$$

**Schritt 3:** Subtraktion $\lambda \cdot (A+B) - A$

$$
\begin{pmatrix} -8 & -2 \\ 2 & -8 \\ -8 & -8 \end{pmatrix} - \begin{pmatrix} 3 & -1 \\ 2 & 4 \\ 0 & 5 \end{pmatrix} = \begin{pmatrix} -11 & -1 \\ 0 & -12 \\ -8 & -13 \end{pmatrix}
$$
