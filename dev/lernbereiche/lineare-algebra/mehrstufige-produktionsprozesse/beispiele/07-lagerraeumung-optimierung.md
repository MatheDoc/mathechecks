---
layout: null
---
Gegeben: Der mehrdeutige Produktionsvektor lautet

$$
\vec{m} = \begin{pmatrix} 50 + 2t \\ 80 - 3t \\ t \\ 120 - t \end{pmatrix}, \quad t \in [0;\,26]
$$

sowie $\vec{k}_v = \begin{pmatrix} 10 & 15 & 30 & 8 \end{pmatrix}$ und $\vec{p} = \begin{pmatrix} 25 & 20 & 50 & 12 \end{pmatrix}$.

**Frage:** Bestimmen Sie die maximale Menge, die von E3 produziert werden könnte.

**Lösung:** $m_3 = t$ wird maximal für den größten zulässigen Wert von $t$:

$$
t = 26 \quad\Rightarrow\quad m_3 = 26
$$

Es können maximal **26 ME** von E3 produziert werden.

**Frage:** Bestimmen Sie die minimalen variablen Kosten.

**Lösung:**

$$
\begin{align*}
K_v &= \vec{k}_v \cdot \vec{m} = 10(50 + 2t) + 15(80 - 3t) + 30t + 8(120 - t) \\
&= 500 + 20t + 1200 - 45t + 30t + 960 - 8t \\
&= 2660 - 3t
\end{align*}
$$

$K_v$ ist eine fallende Funktion von $t$, wird also minimal für $t = 26$:

$$
K_v = 2660 - 3 \cdot 26 = 2582
$$

Die minimalen variablen Kosten betragen **2582 GE**.
