---
layout: null
---
Gegeben:

$$
ZE = \begin{pmatrix} 2 & 3 \\ 1 & 2 \\ 1 & 2 \end{pmatrix}, \quad
\vec{z} = \begin{pmatrix} 800 \\ 500 \\ 500 \end{pmatrix}
$$

**Frage:** Es stehen 800 Chips, 500 Akkus und 500 Displays zur Verfügung. Bestimmen Sie den Produktionsvektor $\vec{m}$, wenn alle Zwischenprodukte aufgebraucht werden sollen.

**Lösung:** Wir lösen das LGS $ZE \cdot \vec{m} = \vec{z}$:

$$
\begin{pmatrix} 2 & 3 \\ 1 & 2 \\ 1 & 2 \end{pmatrix} \cdot \begin{pmatrix} m_1 \\ m_2 \end{pmatrix} = \begin{pmatrix} 800 \\ 500 \\ 500 \end{pmatrix}
$$

Aus der 1. und 2. Gleichung:

$$
\begin{align*}
2m_1 + 3m_2 &= 800 \\
m_1 + 2m_2 &= 500
\end{align*}
$$

Aus der 2. Gleichung folgt $m_1 = 500 - 2m_2$. Einsetzen in die 1. Gleichung:

$$
2(500 - 2m_2) + 3m_2 = 800 \quad\Rightarrow\quad 1000 - m_2 = 800 \quad\Rightarrow\quad m_2 = 200
$$

Damit $m_1 = 500 - 400 = 100$. Probe mit der 3. Gleichung: $100 + 400 = 500$ ✓

$$
\vec{m} = \begin{pmatrix} 100 \\ 200 \end{pmatrix}
$$

Es können **100 ME Alpha** und **200 ME Beta** produziert werden.

**Hinweis:** Ist die Produktionsmatrix quadratisch und invertierbar, so kann die Lösung auch direkt über die Inverse berechnet werden: $\vec{m} = ZE^{-1} \cdot \vec{z}$. Da $ZE$ hier nicht quadratisch ist ($3 \times 2$), existiert keine Inverse und der Weg über das LGS ist notwendig.
