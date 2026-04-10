---
layout: null
---
Gegeben ist das folgende LGS:

$$
\begin{align}
x_1 + x_2 + 2x_3 &= 5 \\
2x_1 + x_2 + 3x_3 &= 8 \\
3x_1 + 2x_2 + 5x_3 &= 13
\end{align}
$$

Das LGS hat unendlich viele Lösungen. Setzen Sie $x_3 = t$ mit $t \in \mathbb{R}$ und bestimmen Sie $x_1$ und $x_2$ in Abhängigkeit von $t$.

**Lösung:**

Wir überführen das LGS in Matrixform und wenden den Gauß-Algorithmus an:

$$
\begin{pmatrix}
1 & 1 & 2 & | & 5 \\
2 & 1 & 3 & | & 8 \\
3 & 2 & 5 & | & 13
\end{pmatrix}
\quad
\begin{matrix}
\\
II - 2 \cdot I \\
III - 3 \cdot I
\end{matrix}
$$

$$
\begin{pmatrix}
1 & 1 & 2 & | & 5 \\
0 & -1 & -1 & | & -2 \\
0 & -1 & -1 & | & -2
\end{pmatrix}
\quad
\begin{matrix}
\\
\\
III - II
\end{matrix}
$$

$$
\begin{pmatrix}
1 & 1 & 2 & | & 5 \\
0 & -1 & -1 & | & -2 \\
0 & 0 & 0 & | & 0
\end{pmatrix}
$$

Die dritte Zeile liefert $0 = 0$, also ist $x_3$ frei wählbar. Wir setzen $x_3 = t$.

$$
\begin{align}
II: \quad & {-x_2 - t = -2} \Rightarrow x_2 = 2 - t \\
I: \quad & x_1 + (2 - t) + 2t = 5 \Rightarrow x_1 = 3 - t
\end{align}
$$

Die Lösung lautet: $x_1 = 3 - t$, $x_2 = 2 - t$, $x_3 = t$ mit $t \in \mathbb{R}$.
