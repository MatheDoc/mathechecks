---
layout: null
---

Gesucht ist die Inverse der Matrix

$$
A = \begin{pmatrix}
1 & 5 & 8\\
1 & 4 & 7\\
3 & 10 & 18
\end{pmatrix}.
$$

Hinweis: Da $\det(A)=1\neq 0$, ist $A$ invertierbar.

Wir starten mit der erweiterten Matrix $(A\mid E_3)$ und formen diese mit Hilfe der elementaren Zeilenumformungen zu $(E_3\mid A^{-1})$ um:

$$
\begin{pmatrix}
1 & 5 & 8 & \mid & 1 & 0 & 0\\
1 & 4 & 7 & \mid & 0 & 1 & 0\\
3 & 10 & 18 & \mid & 0 & 0 & 1
\end{pmatrix}
\quad
\begin{array}{l}
\\
II-I\\
III-3\cdot I
\end{array}
$$

$$
\begin{pmatrix}
1 & 5  & 8  & \mid & 1  & 0 & 0\\
0 & -1 & -1 & \mid & -1 & 1 & 0\\
0 & -5 & -6 & \mid & -3 & 0 & 1
\end{pmatrix}
\quad
\begin{array}{l}
\\
\\
III-5\cdot II
\end{array}
$$

$$
\begin{pmatrix}
1 & 5  & 8  & \mid & 1  & 0 & 0\\
0 & -1 & -1 & \mid & -1 & 1 & 0\\
0 & 0  & -1  & \mid & 2 & -5 & 1
\end{pmatrix}
\quad
\begin{array}{l}
I+8\cdot III\\
II -III\\
\quad\quad\quad
\end{array}
$$

$$
\begin{pmatrix}
1 & 5 & 0 & \mid & 17 & -40 & 8\\
0 & -1 & 0 & \mid & -3 & 6  & -1\\
0 & 0 & -1 & \mid & 2 & -5 & 1
\end{pmatrix}
\quad
\begin{array}{l}
I + 5\cdot II\\
\\
\quad\quad\quad
\end{array}
$$

$$
\begin{pmatrix}
1 & 0 & 0 & \mid & 2 & -10 & 3\\
0 & -1 & 0 & \mid & -3 & 6 & -1\\
0 & 0 & -1 & \mid & 2 & -5 & 1
\end{pmatrix}
\quad
\begin{array}{l}
\\
\cdot (-1)\\
\cdot (-1)\quad
\end{array}
$$

$$
\begin{pmatrix}
1 & 0 & 0 & \mid & 2 & -10 & 3\\
0 & 1 & 0 & \mid & 3 & -6 & 1\\
0 & 0 & 1 & \mid & -2 & 5 & -1
\end{pmatrix}.
$$

Damit ist

$$
A^{-1} = \begin{pmatrix}
2 & -10 & 3\\
3 & -6 & 1\\
-2 & 5 & -1
\end{pmatrix}.
$$

Zur Kontrolle gilt $A\cdot A^{-1}=E_3$.
