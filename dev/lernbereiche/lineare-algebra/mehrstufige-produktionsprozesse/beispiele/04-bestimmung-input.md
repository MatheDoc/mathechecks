---
layout: null
---
Gegeben:

$$
RE = \begin{pmatrix} 13 & 21 \\ 4 & 8 \\ 8 & 15 \end{pmatrix}, \quad
\vec{m} = \begin{pmatrix} 100 \\ 200 \end{pmatrix}
$$

**Frage:** Es sollen 100 ME Alpha und 200 ME Beta produziert werden. Bestimmen Sie den benötigten Rohstoffbedarfsvektor $\vec{r}$.

**Lösung:**

$$
\begin{align*}
\vec{r} &= RE \cdot \vec{m} \\
&= \begin{pmatrix} 13 & 21 \\ 4 & 8 \\ 8 & 15 \end{pmatrix} \cdot \begin{pmatrix} 100 \\ 200 \end{pmatrix} \\
&= \begin{pmatrix} 13 \cdot 100 + 21 \cdot 200 \\ 4 \cdot 100 + 8 \cdot 200 \\ 8 \cdot 100 + 15 \cdot 200 \end{pmatrix} \\
&= \begin{pmatrix} 5500 \\ 2000 \\ 3800 \end{pmatrix}
\end{align*}
$$

Es werden **5500 ME Silizium**, **2000 ME Lithium** und **3800 ME Glas** benötigt.
