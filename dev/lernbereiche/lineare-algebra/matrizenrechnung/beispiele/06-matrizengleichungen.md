---
layout: null
---

Löse die Matrizengleichung $A \cdot X + B = C$ nach $X$ mit

$$
A = \begin{pmatrix} 1 & 2 \\ 3 & 5 \end{pmatrix}, \quad
B = \begin{pmatrix} 0 & 1 \\ -2 & 3 \end{pmatrix}, \quad
C = \begin{pmatrix} 6 & 5 \\ 11 & 6 \end{pmatrix}.
$$

**Schritt 1:** Umstellen nach $A \cdot X$

$$
A \cdot X = C - B = \begin{pmatrix} 6 & 5 \\ 11 & 6 \end{pmatrix} - \begin{pmatrix} 0 & 1 \\ -2 & 3 \end{pmatrix} = \begin{pmatrix} 6 & 4 \\ 13 & 3 \end{pmatrix}
$$

**Schritt 2:** Inverse von $A$ berechnen

Da $\det(A) = 1 \cdot 5 - 2 \cdot 3 = -1 \neq 0$, ist $A$ invertierbar. Mit dem Gauß-Jordan-Algorithmus (oder der Formel für $2 \times 2$-Matrizen) ergibt sich:

$$
A^{-1} = \begin{pmatrix} -5 & 2 \\ 3 & -1 \end{pmatrix}
$$

**Schritt 3:** Von links mit $A^{-1}$ multiplizieren

$$
\begin{align*}
X = A^{-1} \cdot (C - B) &= \begin{pmatrix} -5 & 2 \\ 3 & -1 \end{pmatrix} \cdot \begin{pmatrix} 6 & 4 \\ 13 & 3 \end{pmatrix} \\
&= \begin{pmatrix} -5 \cdot 6 + 2 \cdot 13 & -5 \cdot 4 + 2 \cdot 3 \\ 3 \cdot 6 + (-1) \cdot 13 & 3 \cdot 4 + (-1) \cdot 3 \end{pmatrix} \\
&= \begin{pmatrix} -4 & -14 \\ 5 & 9 \end{pmatrix}
\end{align*}
$$

**Probe:**

$$
A \cdot X + B = \begin{pmatrix} 1 & 2 \\ 3 & 5 \end{pmatrix} \cdot \begin{pmatrix} -4 & -14 \\ 5 & 9 \end{pmatrix} + \begin{pmatrix} 0 & 1 \\ -2 & 3 \end{pmatrix} = \begin{pmatrix} 6 & 4 \\ 13 & 3 \end{pmatrix} + \begin{pmatrix} 0 & 1 \\ -2 & 3 \end{pmatrix} = \begin{pmatrix} 6 & 5 \\ 11 & 6 \end{pmatrix} = C \quad ✅
$$
