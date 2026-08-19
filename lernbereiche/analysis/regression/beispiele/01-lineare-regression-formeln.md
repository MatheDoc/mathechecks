---
layout: null
permalink: /lernbereiche/analysis/regression/beispiele/01-lineare-regression-formeln.html
---
Gegeben sind folgende Werte:

| x   | 1   | 2   | 3   | 4    |
| y   | 5,5 | 6,5 | 8,5 | 11,5 |

Die Gleichung der Regressionsgeraden $f(x)=m\cdot x+b$ soll mit den Regressionsformeln berechnet werden:

$$m=\frac{\sum (x_i-\bar{x})(y_i-\bar{y})}{\sum (x_i-\bar{x})^2}, \qquad b=\bar{y}-m\cdot\bar{x}$$

**Schritt 1: Mittelwerte berechnen**

$$\begin{aligned}
\bar{x} &= \frac{1+2+3+4}{4}=\frac{10}{4}=2{,}5 \\
\bar{y} &= \frac{5{,}5+6{,}5+8{,}5+11{,}5}{4}=\frac{32}{4}=8
\end{aligned}$$

**Schritt 2: Abweichungstabelle anlegen**

Für jeden Datenpunkt werden die Abweichungen von den Mittelwerten, deren Produkt und das Quadrat der x-Abweichung berechnet:

| $x_i-\bar{x}$              | $-1{,}5$ | $-0{,}5$ | $0{,}5$ | $1{,}5$ |
| $y_i-\bar{y}$              | $-2{,}5$ | $-1{,}5$ | $0{,}5$ | $3{,}5$ |
| $(x_i-\bar{x})(y_i-\bar{y})$ | $3{,}75$ | $0{,}75$ | $0{,}25$ | $5{,}25$ |
| $(x_i-\bar{x})^2$          | $2{,}25$ | $0{,}25$ | $0{,}25$ | $2{,}25$ |

Die benötigten Summen sind

$$\begin{aligned}
\sum (x_i-\bar{x})(y_i-\bar{y}) &= 3{,}75+0{,}75+0{,}25+5{,}25 = 10 \\
\sum (x_i-\bar{x})^2 &= 2{,}25+0{,}25+0{,}25+2{,}25 = 5
\end{aligned}$$

**Schritt 3: Formeln anwenden**

$$\begin{aligned}
m &= \frac{\sum (x_i-\bar{x})(y_i-\bar{y})}{\sum (x_i-\bar{x})^2} = \frac{10}{5} = 2 \\
b &= \bar{y}-m\cdot\bar{x} = 8-2\cdot 2{,}5 = 3
\end{aligned}$$

Die Regressionsgerade lautet also $f(x)=2x+3$.

**Schritt 4: Kontrolle mit dem Schwerpunkt**

Die Regressionsgerade muss durch den Schwerpunkt $(\bar{x} \mid \bar{y})=(2{,}5 \mid 8)$ laufen. Einsetzen von $\bar{x}=2{,}5$:

$$f(2{,}5)=2\cdot 2{,}5+3=8=\bar{y}$$

Die Kontrolle stimmt – das Ergebnis ist plausibel.
