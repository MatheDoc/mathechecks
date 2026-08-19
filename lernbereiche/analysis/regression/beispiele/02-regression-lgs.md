---
layout: null
permalink: /lernbereiche/analysis/regression/beispiele/02-regression-lgs.html
---
Gegeben sind folgende Werte:

| x   | 0 | 1 | 2 | 3 |
| y   | 8,75 | 3,75 | 0,25 | 3,25 |

Die quadratische Regressionsfunktion mit dem Ansatz $f(x)=ax^2+bx+c$ soll durch Aufstellen und Lösen eines linearen Gleichungssystems bestimmt werden.

**Schritt 1: Summentabelle anlegen**

Für die Normalengleichungen des quadratischen Ansatzes werden die folgenden Summen benötigt:

| $\sum x_i$ | $\sum x_i^2$ | $\sum x_i^3$ | $\sum x_i^4$ | $\sum y_i$ | $\sum x_i y_i$ | $\sum x_i^2 y_i$ |
| $6$ | $14$ | $36$ | $98$ | $16$ | $14$ | $34$ |

Zur Kontrolle zwei der Rechnungen im Detail:

$$\begin{aligned}
\sum x_i y_i &= 0\cdot 8{,}75+1\cdot 3{,}75+2\cdot 0{,}25+3\cdot 3{,}25 = 0+3{,}75+0{,}5+9{,}75 = 14 \\
\sum x_i^2 y_i &= 0\cdot 8{,}75+1\cdot 3{,}75+4\cdot 0{,}25+9\cdot 3{,}25 = 0+3{,}75+1+29{,}25 = 34
\end{aligned}$$

**Schritt 2: Normalengleichungen aufstellen**

Mit $n=4$ Datenpunkten lautet das 3×3-Gleichungssystem in den Unbekannten $a$, $b$ und $c$:

$$\begin{aligned}
98a+36b+14c &= 34 \\
36a+14b+6c &= 14 \\
14a+6b+4c &= 16
\end{aligned}$$

**Schritt 3: LGS lösen**

Dieses LGS kann mit dem GTR oder dem Gauß-Algorithmus gelöst werden. Die Lösung lautet

$$a=2, \qquad b=-8, \qquad c=9.$$

**Ergebnis**

Die quadratische Regressionsfunktion lautet

$$f(x)=2x^2-8x+9.$$
