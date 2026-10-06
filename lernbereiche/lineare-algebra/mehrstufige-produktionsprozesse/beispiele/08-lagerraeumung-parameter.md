---
layout: null
permalink: /lernbereiche/lineare-algebra/mehrstufige-produktionsprozesse/beispiele/08-lagerraeumung-parameter.html
---
Gegeben: Der mehrdeutige Produktionsvektor lautet

$$
\vec{m} = \begin{pmatrix} 50 + 2t \\ 80 - 3t \\ 30 - 2t \\ t \end{pmatrix}
$$

sowie $\vec{k}_v = \begin{pmatrix} 10 & 15 & 20 & 30 \end{pmatrix}$.

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

Alle vier Bedingungen sind gleichzeitig erfüllt für $0 \leq t \leq 15$, also $t \in [0;\,15]$.

**Frage:** Bestimmen Sie $t$ so, dass von E2 genau 50 ME produziert werden.

**Lösung:** Es gilt $m_2 = 80 - 3t$, also:

$$
80 - 3t = 50 \quad\Rightarrow\quad 3t = 30 \quad\Rightarrow\quad t = 10
$$

Probe: $t = 10 \in [0;\,15]$ ✓

**Frage:** Bestimmen Sie $t$ so, dass die variablen Kosten 2020 GE betragen.

**Lösung:** Aus dem vorherigen Beispiel wissen wir: $K_v = 2300 - 35t$. Damit:

$$
2300 - 35t = 2020 \quad\Rightarrow\quad 35t = 280 \quad\Rightarrow\quad t = 8
$$

Probe: $t = 8 \in [0;\,15]$ ✓

**Frage:** Bestimmen Sie $t$ so, dass von E4 doppelt so viele ME wie von E3 hergestellt werden.

**Lösung:** Bedingung: $m_4 = 2 \cdot m_3$, also:

$$
t = 2(30 - 2t) = 60 - 4t \quad\Rightarrow\quad 5t = 60 \quad\Rightarrow\quad t = 12
$$

Probe: $t = 12 \in [0;\,15]$ ✓
