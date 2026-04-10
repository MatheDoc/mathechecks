---
layout: null
---

Gesucht ist die Inverse der Matrix

$$
A = \begin{pmatrix}1 & 2 \\ 2 & 3\end{pmatrix}.
$$

Hinweis: Da $\det(A) = 1\cdot 3 - 2\cdot 2 = -1 \neq 0$, ist $A$ invertierbar.

Wir starten mit der erweiterten Matrix $(A\mid E_2)$ und formen diese mit Hilfe der elementaren Zeilenumforumgen zu $(E_2\mid A^{-1})$ um:


$$
\begin{pmatrix}
1 & 2 & \mid & 1 & 0 \\
2 & 3 & \mid & 0 & 1
\end{pmatrix}
\quad
\begin{array}{l}
\\
II-2\cdot I
\end{array}
$$

$$
\begin{pmatrix}
1 & 2 & \mid & 1 & 0 \\
0 & -1 & \mid & -2 & 1
\end{pmatrix}
\quad
\begin{array}{l}
\\
\cdot (-1)\quad\quad\\
\end{array}
$$

$$
\begin{pmatrix}
1 & 2 & \mid & 1 & 0 \\
0 & 1 & \mid & 2 & -1
\end{pmatrix}
\quad
\begin{array}{l}
I-2\cdot II\\
\\
\end{array}
$$

$$
\begin{pmatrix}
1 & 0 & \mid & -3 & 2 \\
0 & 1 & \mid & 2 & -1
\end{pmatrix}
\quad
\begin{array}{l}
\quad\quad\quad\\
\\
\end{array}
$$


Damit ist

$$
A^{-1} = \begin{pmatrix}-3 & 2 \\ 2 & -1\end{pmatrix}.
$$

Zur Kontrolle berechnen wir:

$$
\begin{pmatrix}1 & 2 \\ 2 & 3\end{pmatrix}
\begin{pmatrix}-3 & 2 \\ 2 & -1\end{pmatrix}
=
\begin{pmatrix}1 & 0 \\ 0 & 1\end{pmatrix}
= E_2.
$$
