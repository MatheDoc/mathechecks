---
layout: null
---

Gesucht ist die Inverse der Matrix

$$
A = \begin{pmatrix}
2 & 2 & 1 & 3\\
4 & 2 & 1 & 4\\
3 & 1 & 1 & 3\\
4 & 5 & 2 & 7
\end{pmatrix}.
$$

Hinweis: Da $\det(A)=-1\neq 0$, ist $A$ invertierbar.

Wir starten mit der erweiterten Matrix $(A\mid E_4)$ und formen diese mit Hilfe der elementaren Zeilenumformungen zu $(E_4\mid A^{-1})$ um:

$$
\begin{pmatrix}
2 & 2 & 1 & 3 & \mid & 1 & 0 & 0 & 0\\
4 & 2 & 1 & 4 & \mid & 0 & 1 & 0 & 0\\
3 & 1 & 1 & 3 & \mid & 0 & 0 & 1 & 0\\
4 & 5 & 2 & 7 & \mid & 0 & 0 & 0 & 1
\end{pmatrix}
\quad
\begin{array}{l}
\\
II-2\cdot I\\
III-I\\
IV-2\cdot I
\end{array}
$$

$$
\begin{pmatrix}
2 & 2 & 1 & 3 & \mid & 1 & 0 & 0 & 0\\
0 & -2 & -1 & -2 & \mid & -2 & 1 & 0 & 0\\
1 & -1 & 0 & 0 & \mid & -1 & 0 & 1 & 0\\
0 & 1 & 0 & 1 & \mid & -2 & 0 & 0 & 1
\end{pmatrix}
\quad
\begin{array}{l}
I\leftrightarrow III\\
\\
\\
\quad\quad\quad
\end{array}
$$

$$
\begin{pmatrix}
1 & -1 & 0 & 0 & \mid & -1 & 0 & 1 & 0\\
0 & -2 & -1 & -2 & \mid & -2 & 1 & 0 & 0\\
2 & 2 & 1 & 3 & \mid & 1 & 0 & 0 & 0\\
0 & 1 & 0 & 1 & \mid & -2 & 0 & 0 & 1
\end{pmatrix}
\quad
\begin{array}{l}
\\
\\
III-2\cdot I\\
\quad\quad\quad
\end{array}
$$

$$
\begin{pmatrix}
1 & -1 & 0 & 0 & \mid & -1 & 0 & 1 & 0\\
0 & -2 & -1 & -2 & \mid & -2 & 1 & 0 & 0\\
0 & 4 & 1 & 3 & \mid & 3 & 0 & -2 & 0\\
0 & 1 & 0 & 1 & \mid & -2 & 0 & 0 & 1
\end{pmatrix}
\quad
\begin{array}{l}
\\
II\leftrightarrow IV\\
\\
\\
\end{array}
$$

$$
\begin{pmatrix}
1 & -1 & 0 & 0 & \mid & -1 & 0 & 1 & 0\\
0 & 1 & 0 & 1 & \mid & -2 & 0 & 0 & 1\\
0 & 4 & 1 & 3 & \mid & 3 & 0 & -2 & 0\\
0 & -2 & -1 & -2 & \mid & -2 & 1 & 0 & 0
\end{pmatrix}
\quad
\begin{array}{l}
I+II\\
\\
III-4\cdot II\\
IV+2\cdot II
\end{array}
$$

$$
\begin{pmatrix}
1 & 0 & 0 & 1 & \mid & -3 & 0 & 1 & 1\\
0 & 1 & 0 & 1 & \mid & -2 & 0 & 0 & 1\\
0 & 0 & 1 & -1 & \mid & 11 & 0 & -2 & -4\\
0 & 0 & -1 & 0 & \mid & -6 & 1 & 0 & 2
\end{pmatrix}
\quad
\begin{array}{l}
\\
\\
\\
IV+III
\end{array}
$$

$$
\begin{pmatrix}
1 & 0 & 0 & 1 & \mid & -3 & 0 & 1 & 1\\
0 & 1 & 0 & 1 & \mid & -2 & 0 & 0 & 1\\
0 & 0 & 1 & -1 & \mid & 11 & 0 & -2 & -4\\
0 & 0 & 0 & -1 & \mid & 5 & 1 & -2 & -2
\end{pmatrix}
\quad
\begin{array}{l}
I+IV\\
II+IV\\
III-IV\\
\quad\quad\quad
\end{array}
$$

$$
\begin{pmatrix}
1 & 0 & 0 & 0 & \mid & 2 & 1 & -1 & -1\\
0 & 1 & 0 & 0 & \mid & 3 & 1 & -2 & -1\\
0 & 0 & 1 & 0 & \mid & 6 & -1 & 0 & -2\\
0 & 0 & 0 & -1 & \mid & 5 & 1 & -2 & -2
\end{pmatrix}
\quad
\begin{array}{l}
\\
\\
\\
\cdot (-1)
\end{array}
$$

$$
\begin{pmatrix}
1 & 0 & 0 & 0 & \mid & 2 & 1 & -1 & -1\\
0 & 1 & 0 & 0 & \mid & 3 & 1 & -2 & -1\\
0 & 0 & 1 & 0 & \mid & 6 & -1 & 0 & -2\\
0 & 0 & 0 & 1 & \mid & -5 & -1 & 2 & 2
\end{pmatrix}.
$$

Damit ist

$$
A^{-1} = \begin{pmatrix}
2 & 1 & -1 & -1\\
3 & 1 & -2 & -1\\
6 & -1 & 0 & -2\\
-5 & -1 & 2 & 2
\end{pmatrix}.
$$

Zur Kontrolle gilt $A\cdot A^{-1}=E_4$.

