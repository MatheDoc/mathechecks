---
layout: null
permalink: /lernbereiche/lineare-algebra/lineare-gleichungssysteme/beispiele/03-lgs-loesen-4x4.html
---

Gesucht ist die Lösung des LGS

$$
\begin{align*}
x_1+x_2+x_3+x_4 &= 10 \\
2x_1+3x_2+x_3+x_4 &= 15 \\
-x_1+2x_2-3x_3-3x_4 &= -18 \\
x_1-x_2+5x_3+6x_4 &= 38
\end{align*}
$$

In Matrixform erhalten wir:

$$
\begin{pmatrix}
1 & 1 & 1 & 1 & | & 10 \\
2 & 3 & 1 & 1 & | & 15 \\
-1 & 2 & -3 & -3 & | & -18 \\
1 & -1 & 5 & 6 & | & 38
\end{pmatrix}
$$

Zuerst beseitigen wir die drei Einträge unter dem ersten Pivot:

$$
\begin{pmatrix}
1 & 1 & 1 & 1 & | & 10 \\
2 & 3 & 1 & 1 & | & 15 \\
-1 & 2 & -3 & -3 & | & -18 \\
1 & -1 & 5 & 6 & | & 38
\end{pmatrix}
\quad
\begin{matrix}
\\
II-2\cdot I \\
III+I \\
IV-I
\end{matrix}
$$

$$
\begin{pmatrix}
1 & 1 & 1 & 1 & | & 10 \\
0 & 1 & -1 & -1 & | & -5 \\
0 & 3 & -2 & -2 & | & -8 \\
0 & -2 & 4 & 5 & | & 28
\end{pmatrix}
$$

Danach beseitigen wir die beiden Einträge unter dem zweiten Pivot:

$$
\begin{pmatrix}
1 & 1 & 1 & 1 & | & 10 \\
0 & 1 & -1 & -1 & | & -5 \\
0 & 3 & -2 & -2 & | & -8 \\
0 & -2 & 4 & 5 & | & 28
\end{pmatrix}
\quad
\begin{matrix}
\\
\\
III-3\cdot II \\
IV+2\cdot II
\end{matrix}
$$

$$
\begin{pmatrix}
1 & 1 & 1 & 1 & | & 10 \\
0 & 1 & -1 & -1 & | & -5 \\
0 & 0 & 1 & 1 & | & 7 \\
0 & 0 & 2 & 3 & | & 18
\end{pmatrix}
$$

Zum Schluss beseitigen wir den Eintrag unter dem dritten Pivot:

$$
\begin{pmatrix}
1 & 1 & 1 & 1 & | & 10 \\
0 & 1 & -1 & -1 & | & -5 \\
0 & 0 & 1 & 1 & | & 7 \\
0 & 0 & 2 & 3 & | & 18
\end{pmatrix}
\quad
\begin{matrix}
\\
\\
\\
IV-2\cdot III
\end{matrix}
$$

$$
\begin{pmatrix}
1 & 1 & 1 & 1 & | & 10 \\
0 & 1 & -1 & -1 & | & -5 \\
0 & 0 & 1 & 1 & | & 7 \\
0 & 0 & 0 & 1 & | & 4
\end{pmatrix}
$$

Nun bestimmen wir die Variablen durch Rückwärtseinsetzen, beginnend mit der letzten Zeile:

$$
\begin{alignat*}{3}
IV:\quad & x_4 & = & 4 \\
III:\quad & x_3+x_4 & = & 7 \\
II:\quad & x_2-x_3-x_4 & = & -5 \\
I:\quad & x_1+x_2+x_3+x_4 & = & 10
\end{alignat*}
$$

$$
\begin{alignat*}{2}
IV:\quad & x_4=4 \\
III:\quad & x_3+4=7 \Rightarrow x_3=3 \\
II:\quad & x_2-3-4=-5 \Rightarrow x_2=2 \\
I:\quad & x_1+2+3+4=10 \Rightarrow x_1=1
\end{alignat*}
$$

Die eindeutige Lösung lautet $x_1=1$, $x_2=2$, $x_3=3$ und $x_4=4$.
