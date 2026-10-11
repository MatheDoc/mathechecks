---
layout: null
permalink: /lernbereiche/lineare-algebra/lineare-gleichungssysteme/beispiele/05-lgs-rangkriterium.html
---
Gegeben ist die bereits in Zeilenstufenform vorliegende erweiterte Koeffizientenmatrix

$$
(A\mid y)=
\begin{pmatrix}
2 & -1 & 3 & | & 4 \\
0 & 5 & -2 & | & 1 \\
0 & 0 & 0 & | & 6
\end{pmatrix}
$$

Bestimmen Sie $rg(A)$, $rg(A\mid y)$ und $n$ und geben Sie mit Hilfe des Rangkriteriums an, wie viele Lösungen das LGS besitzt.

**Lösung:**

Der Rang ist die Anzahl der Zeilen, in denen nicht alle Elemente 0 sind.

Koeffizientenmatrix $A$ (ohne die Spalte hinter dem Strich):

$$
A=
\begin{pmatrix}
2 & -1 & 3 \\
0 & 5 & -2 \\
0 & 0 & 0
\end{pmatrix}
$$

Die dritte Zeile von $A$ besteht nur aus Nullen, die ersten beiden Zeilen nicht. Also ist

$$
rg(A)=2.
$$

Erweiterte Koeffizientenmatrix $(A\mid y)$: Hier hat auch die dritte Zeile ein Element ungleich 0, nämlich die $6$ hinter dem Strich. Alle drei Zeilen zählen, also ist

$$
rg(A\mid y)=3.
$$

Die Anzahl der Unbekannten ist die Anzahl der Spalten von $A$:

$$
n=3.
$$

Rangkriterium:

$$
\begin{align*}
rg(A)=2 \;&<\; rg(A\mid y)=3
\end{align*}
$$

Das LGS hat **keine Lösung**. Das sieht man auch an der dritten Zeile, die die Gleichung $0 = 6$ liefert – ein Widerspruch. ✅
