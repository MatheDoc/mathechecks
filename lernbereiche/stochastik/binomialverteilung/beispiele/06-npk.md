---
layout: null
permalink: /lernbereiche/stochastik/binomialverteilung/beispiele/06-npk.html
---
Der Besitzer eines Restaurants untersucht, wie viele Gäste vegetarische Gerichte bestellen. $X$ ist die Anzahl der vegetarischen Bestellungen. In allen drei Fragen ist eine Bedingung an eine Intervallwahrscheinlichkeit gegeben, gesucht ist jeweils eine andere der drei Größen $n$, $p$ und $k$.

**$n$ gesucht.** 61 % aller Gäste bestellen vegetarisch. Wie viele Bestellungen müssen mindestens betrachtet werden, damit die Wahrscheinlichkeit für mindestens 144 vegetarische Bestellungen mindestens 29 % beträgt?

Gegeben sind $p=0{,}61$ und $k=144$. Gesucht ist das kleinste $n$ mit $P(X\geq 144)\geq 0{,}29$. Mit mehr Bestellungen wird die Wahrscheinlichkeit größer. Wir probieren:

$$
\begin{align*}
\text{für }n=228 \text{ gilt: } P(X\geq 144)&=0{,}2753<0{,}29\\
\text{für }n=229 \text{ gilt: } P(X\geq 144)&=0{,}3042\geq 0{,}29
\end{align*}
$$

Das kleinste $n$ ist also $n=229$.

**$p$ gesucht.** Der Besitzer betrachtet 200 Bestellungen. Wie groß muss der Anteil vegetarischer Bestellungen mindestens sein, damit die Wahrscheinlichkeit für mindestens 130 vegetarische Bestellungen mindestens 50 % beträgt (auf 2 NKS)?

Gegeben sind $n=200$ und $k=130$. Gesucht ist das kleinste $p$ mit $P(X\geq 130)\geq 0{,}5$. Mit größerem $p$ wird die Wahrscheinlichkeit größer. Wir probieren:

$$
\begin{align*}
\text{für }p=0{,}64 \text{ gilt: } P(X\geq 130)&=0{,}4151<0{,}5\\
\text{für }p=0{,}65 \text{ gilt: } P(X\geq 130)&=0{,}5325\geq 0{,}5
\end{align*}
$$

Das kleinste $p$ ist also $p=0{,}65$.

**$k$ gesucht.** Wieder bestellen 61 % vegetarisch, betrachtet werden 200 Bestellungen. Mit wie vielen vegetarischen Bestellungen kann der Besitzer mit einer Wahrscheinlichkeit von mindestens 90 % mindestens rechnen?

Gegeben sind $n=200$ und $p=0{,}61$. Gesucht ist das größte $k$ mit $P(X\geq k)\geq 0{,}9$. Mit größerem $k$ wird die Wahrscheinlichkeit kleiner. Wir probieren:

$$
\begin{align*}
\text{für }k=113 \text{ gilt: } P(X\geq 113)&=0{,}9151\geq 0{,}9\\
\text{für }k=114 \text{ gilt: } P(X\geq 114)&=0{,}8906<0{,}9
\end{align*}
$$

Das größte $k$ ist also $k=113$.
