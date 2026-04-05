---
layout: null
---
Gesucht ist die Lösung des LGS

$$
\begin{align*}
x_1 + x_2 + x_3 &= 3 \\
4x_1 + 2x_2 + x_3 &= 14 \\
16x_1 - 4x_2 + x_3 &= 8
\end{align*}
$$


In Matrixform erhalten wir:

$$
\begin{pmatrix}
1 & 1   & 1 & | & 3\\
4 & 2   & 1 & | & 14\\
16 & -4 & 1 & | & 8
\end{pmatrix}
$$

Wir formen diese Matrix mit Hilfe des Gauß-Algorithmus in eine obere Dreiecksform um:

$$
\begin{pmatrix}
1 & 1 & 1 & | & 3\\
4 & 2 & 1 & | & 14\\
16 & -4 & 1 &| & 8
\end{pmatrix}
\quad
\begin{matrix}
\\
II-4\cdot I\\
III-16\cdot I
\end{matrix}
$$

$$
\begin{pmatrix}
1 & 1 & 1 & | & 3\\
0 & -2 & -3 & | & 2\\
0 & -20 & -15 &| & -40
\end{pmatrix}
\quad
\begin{matrix}
\\
\\
III-10\cdot II
\end{matrix}
$$

$$
\begin{pmatrix}
1 & 1 & 1 & | & 3\\
0 & -2 & -3 & | & 2\\
0 & 0 & 15 &| & -60
\end{pmatrix}
\quad
\begin{matrix}
\\
\\
\quad\quad\quad\quad\quad
\end{matrix}
$$


Nun verwenden wir wieder die ausführliche Schreibweise, um angefangen von der letzten Gleichung alle Unbekannten nacheinander zu bestimmen.

$$
\begin{alignat*}{3}
I:\quad   & x_1+x_2+x_3 & = & 3\\
II:\quad  & -2x_2-3x_3  & = & 2\\
III:\quad & 15x_3       & = & -60\\
\end{alignat*}
$$

Auflösen nach den Unbekannten:

$$
\begin{alignat*}{2}
III:\quad & 15x_3=-60 \Rightarrow x_3=-4\quad ✅\\
II:\quad  & -2x_2-3\cdot (-4)=2 \Rightarrow -2x_2=-10 \Rightarrow x_2=5\quad ✅\\
I:\quad   & x_1+5-4=3 \Rightarrow x_1=2\quad ✅\\
\end{alignat*}
$$

