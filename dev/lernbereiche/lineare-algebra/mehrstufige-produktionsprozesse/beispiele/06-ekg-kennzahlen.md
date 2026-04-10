---
layout: null
---
Gegeben:

$$
RE = \begin{pmatrix} 13 & 21 \\ 4 & 8 \\ 8 & 15 \end{pmatrix}, \quad
ZE = \begin{pmatrix} 2 & 3 \\ 1 & 2 \\ 1 & 2 \end{pmatrix}, \quad
\vec{m} = \begin{pmatrix} 100 \\ 200 \end{pmatrix}
$$

$$
\vec{k}_R = \begin{pmatrix} 2 & 8 & 3 \end{pmatrix}, \quad
\vec{k}_Z = \begin{pmatrix} 10 & 15 & 5 \end{pmatrix}, \quad
\vec{k}_E = \begin{pmatrix} 20 & 25 \end{pmatrix}, \quad
\vec{p} = \begin{pmatrix} 500 & 800 \end{pmatrix}, \quad
K_f = 10000
$$

**Frage:** Berechnen Sie die variablen Stückkosten, die variablen Kosten, die Erlöse, den Deckungsbeitrag und den Gewinn.

**Lösung:**

Variable Stückkosten:

$$
\begin{align*}
\vec{k}_v &= \vec{k}_R \cdot RE + \vec{k}_Z \cdot ZE + \vec{k}_E \\
&= \begin{pmatrix} 2 & 8 & 3 \end{pmatrix} \cdot \begin{pmatrix} 13 & 21 \\ 4 & 8 \\ 8 & 15 \end{pmatrix} + \begin{pmatrix} 10 & 15 & 5 \end{pmatrix} \cdot \begin{pmatrix} 2 & 3 \\ 1 & 2 \\ 1 & 2 \end{pmatrix} + \begin{pmatrix} 20 & 25 \end{pmatrix} \\
&= \begin{pmatrix} 82 & 151 \end{pmatrix} + \begin{pmatrix} 40 & 70 \end{pmatrix} + \begin{pmatrix} 20 & 25 \end{pmatrix} = \begin{pmatrix} 142 & 246 \end{pmatrix}
\end{align*}
$$

Variable Kosten:

$$
K_v = \vec{k}_v \cdot \vec{m} = 142 \cdot 100 + 246 \cdot 200 = 63400
$$

Erlöse:

$$
E = \vec{p} \cdot \vec{m} = 500 \cdot 100 + 800 \cdot 200 = 210000
$$

Stückdeckungsbeitrag:

$$
\vec{db} = \vec{p} - \vec{k}_v = \begin{pmatrix} 358 & 554 \end{pmatrix}
$$

Deckungsbeitrag:

$$
DB = \vec{db} \cdot \vec{m} = 358 \cdot 100 + 554 \cdot 200 = 146600
$$

Gewinn:

$$
G = DB - K_f = 146600 - 10000 = 136600
$$
