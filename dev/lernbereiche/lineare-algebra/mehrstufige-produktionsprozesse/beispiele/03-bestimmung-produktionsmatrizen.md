---
layout: null
---
Gegeben:

$$
RZ = \begin{pmatrix} 5 & 2 & 1 \\ 0 & 4 & 0 \\ 1 & 0 & 6 \end{pmatrix}, \quad
RE = \begin{pmatrix} 13 & 21 \\ 4 & 8 \\ 8 & 15 \end{pmatrix}
$$

**Frage:** Berechnen Sie die Zwischenprodukt-Endprodukt-Matrix $ZE$.

**Lösung:** Es gilt $RE = RZ \cdot ZE$, also

$$
\begin{align*}
ZE &= RZ^{-1} \cdot RE\\
    &=\begin{pmatrix} 5 & 2 & 1 \\ 0 & 4 & 0 \\ 1 & 0 & 6 \end{pmatrix}^{-1}\cdot \begin{pmatrix} 13 & 21 \\ 4 & 8 \\ 8 & 15 \end{pmatrix}\\
    & =\begin{pmatrix} 2 & 3 \\ 1 & 2 \\ 1 & 2 \end{pmatrix}.
\end{align*}
$$

