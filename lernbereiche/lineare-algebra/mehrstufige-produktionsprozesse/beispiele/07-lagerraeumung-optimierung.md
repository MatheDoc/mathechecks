---
layout: null
permalink: /lernbereiche/lineare-algebra/mehrstufige-produktionsprozesse/beispiele/07-lagerraeumung-optimierung.html
---
Gegeben: Der mehrdeutige Produktionsvektor lautet

$$
\vec{m} = \begin{pmatrix} 50 + 2t \\ 80 - 3t \\ 30 - 2t \\ t \end{pmatrix}
$$

sowie $\vec{k}_v = \begin{pmatrix} 10 & 15 & 20 & 30 \end{pmatrix}$ und $\vec{p} = \begin{pmatrix} 25 & 20 & 35 & 45 \end{pmatrix}$.

**Frage:** Bestimmen Sie den ökonomisch sinnvollen Bereich für $t$.

**Lösung:** Alle Komponenten von $\vec{m}$ müssen größer oder gleich null sein:

$$
\begin{align*}
50 + 2t &\geq 0 \quad\Leftrightarrow\quad t \geq -25 \\
80 - 3t &\geq 0 \quad\Leftrightarrow\quad t \leq \tfrac{80}{3} \approx 26{,}67 \\
30 - 2t &\geq 0 \quad\Leftrightarrow\quad t \leq 15 \\
t &\geq 0
\end{align*}
$$

Alle vier Bedingungen sind gleichzeitig erfüllt für $0 \leq t \leq 15$. Der ökonomisch sinnvolle Bereich ist also $t \in [0;\,15]$.

**Frage:** Bestimmen Sie die maximale Menge, die von E1 produziert werden könnte.

**Lösung:** $m_1 = 50 + 2t$ wächst mit $t$, wird also maximal für den größten zulässigen Wert $t = 15$:

$$
m_1 = 50 + 2 \cdot 15 = 80
$$

Es können maximal **80 ME** von E1 produziert werden.

**Frage:** Bestimmen Sie die minimalen variablen Kosten.

**Lösung:**

$$
\begin{align*}
K_v &= \vec{k}_v \cdot \vec{m} = 10(50 + 2t) + 15(80 - 3t) + 20(30 - 2t) + 30t \\
&= 500 + 20t + 1200 - 45t + 600 - 40t + 30t \\
&= 2300 - 35t
\end{align*}
$$

$K_v$ ist eine fallende Funktion von $t$, wird also minimal für $t = 15$:

$$
K_v = 2300 - 35 \cdot 15 = 1775
$$

Die minimalen variablen Kosten betragen **1775 GE**.
