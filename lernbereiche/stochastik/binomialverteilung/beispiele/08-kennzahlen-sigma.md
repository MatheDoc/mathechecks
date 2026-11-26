---
layout: null
permalink: /lernbereiche/stochastik/binomialverteilung/beispiele/08-kennzahlen-sigma.html
---
In beiden Fällen ist die Standardabweichung $\sigma$ gegeben. Dann muss die Formel $\sigma=\sqrt{n\cdot p\cdot (1-p)}$ umgestellt werden. Zuerst wird quadriert: $\sigma^2=n\cdot p\cdot (1-p)$.

**$p$ und $\sigma$ gegeben.** Eine Maschine produziert ein Bauteil. Erfahrungsgemäß ist jedes zehnte Bauteil fehlerhaft. Bei einer Qualitätskontrolle ergibt sich eine Standardabweichung von $4{,}6476$ für die Anzahl fehlerhafter Bauteile. Wie viele Bauteile wurden kontrolliert? Wie viele fehlerhafte Bauteile werden erwartet?

Gesucht ist $n$, also wird $\sigma^2=n\cdot p\cdot (1-p)$ nach $n$ umgestellt:

$$
\begin{align*}
4{,}6476^2&=n\cdot 0{,}1\cdot 0{,}9\\
21{,}6002&=n\cdot 0{,}09\quad |:0{,}09\\
n&\approx 240\\
\mu&=240\cdot 0{,}1=24
\end{align*}
$$

**$\mu$ und $\sigma$ gegeben.** Vor einer Wahl wird untersucht, wie viele Wahlberechtigte noch unentschlossen sind. $X$ ist die Anzahl der unentschlossenen Befragten. Die Auswertung liefert $\mu=175$ und $\sigma=10{,}6653$. Mit welcher Wahrscheinlichkeit ist ein zufällig ausgewählter Wahlberechtigter unentschlossen? Wie viele Wahlberechtigte wurden befragt?

Weil $n\cdot p=\mu$ ist, gilt $\sigma^2=\mu\cdot (1-p)$. Daraus folgt zuerst $p$, danach $n$:

$$
\begin{align*}
10{,}6653^2&=175\cdot (1-p)\\
113{,}7486&=175\cdot (1-p)\quad|:175\\
0{,}65&=1-p\\
p&=0{,}35\\
n&=\frac{\mu}{p}=\frac{175}{0{,}35}=500
\end{align*}
$$
