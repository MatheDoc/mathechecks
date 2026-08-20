---
layout: null
permalink: /lernbereiche/analysis/regression/beispiele/02-regression-lgs.html
---
Gegeben sind folgende Werte:

| x   | 0  | 1  | 2 | 3  |
| y   | 34 | 14 | 0 | 12 |

Die quadratische Regressionsfunktion mit dem Ansatz $f(x)=ax^2+bx+c$ soll durch Aufstellen und Lösen eines linearen Gleichungssystems bestimmt werden.

**Schritt 1: Abweichungssumme aufstellen**

Für jeden Datenpunkt wird die Abweichung zwischen gemessenem Wert $y_i$ und Funktionswert $f(x_i)$ quadriert und aufsummiert:

$$\begin{aligned}
S(a,b,c)=\;&\big(34-(a\cdot 0^2+b\cdot 0+c)\big)^2+\big(14-(a\cdot 1^2+b\cdot 1+c)\big)^2 \\
+\;&\big(0-(a\cdot 2^2+b\cdot 2+c)\big)^2+\big(12-(a\cdot 3^2+b\cdot 3+c)\big)^2
\end{aligned}$$


**Schritt 2: Ableitungen null setzen**

Gesucht ist das Minimum von $S$. Dazu wird $S$ nacheinander als Funktion jeweils eines Koeffizienten betrachtet (die anderen beiden festgehalten), abgeleitet und die Ableitung gleich null gesetzt:

$$S'_{b,c}(a)=0, \qquad S'_{a,c}(b)=0, \qquad S'_{a,b}(c)=0$$

Gleichwertig dazu ist die Schreibweise

$$\frac{\partial S(a,b,c)}{\partial a}=0, \qquad \frac{\partial S(a,b,c)}{\partial b}=0, \qquad \frac{\partial S(a,b,c)}{\partial c}=0$$

Hierbei handelt es sich um ein lineares Gleichungssystem mit 3 Gleichungen und 3 Unbekannten.

<!--$$\begin{aligned}
98a+36b+14c &= 122 \\
36a+14b+6c &= 50 \\
14a+6b+4c &= 60
\end{aligned}$$-->

**Schritt 3: LGS lösen**

Das LGS kann mit dem GTR oder dem Gauß-Algorithmus gelöst werden. Die Lösung lautet

$$a=8, \qquad b=-32, \qquad c=35.$$

**Ergebnis**

Die quadratische Regressionsfunktion lautet

$$f(x)=8x^2-32x+35.$$
