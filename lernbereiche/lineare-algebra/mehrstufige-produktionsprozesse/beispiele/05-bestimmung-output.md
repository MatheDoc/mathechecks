---
layout: null
permalink: /lernbereiche/lineare-algebra/mehrstufige-produktionsprozesse/beispiele/05-bestimmung-output.html
---
Gegeben:

$$
ZE = \begin{pmatrix} 2 & 3 \\ 1 & 2 \end{pmatrix}, \quad
\vec{z} = \begin{pmatrix} 800 \\ 500 \end{pmatrix}
$$

**Frage:** Es stehen 800 Chips und 500 Akkus zur Verfügung. Bestimmen Sie den Produktionsvektor $\vec{m}$, wenn alle Zwischenprodukte aufgebraucht werden sollen.

**Lösung:** Es gilt $ZE \cdot \vec{m} = \vec{z}$. Da $ZE$ quadratisch und invertierbar ist, folgt

$$
\begin{align*}
\vec{m} &= ZE^{-1} \cdot \vec{z}\\
    &= \begin{pmatrix} 2 & 3 \\ 1 & 2 \end{pmatrix}^{-1} \cdot \begin{pmatrix} 800 \\ 500 \end{pmatrix}\\
    &= \begin{pmatrix} 100 \\ 200 \end{pmatrix}.
\end{align*}
$$

Es können **100 ME Alpha** und **200 ME Beta** produziert werden.
