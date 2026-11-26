---
layout: null
permalink: /lernbereiche/stochastik/binomialverteilung/beispiele/07-kennzahlen-mu.html
---
In allen drei Fällen sind zwei der drei Größen $n$, $p$ und $\mu$ gegeben. Die dritte folgt aus $\mu=n\cdot p$, danach wird $\sigma=\sqrt{n\cdot p\cdot (1-p)}$ berechnet.

**$n$ und $p$ gegeben.** Eine Münze wird 20-mal geworfen. Die Anzahl der Kopf-Würfe ist binomialverteilt mit $n=20$ und $p=0{,}5$. Wie viele Kopf-Würfe sind zu erwarten, und wie groß ist die Standardabweichung?

$$
\begin{align*}
\mu &= n\cdot p = 20 \cdot 0{,}5 = 10 \\
\sigma &= \sqrt{n\cdot p\cdot (1-p)}= \sqrt{20 \cdot 0{,}5 \cdot 0{,}5} \approx 2{,}2361
\end{align*}
$$

**$n$ und $\mu$ gegeben.** Polizisten kontrollieren in der Nähe einer Diskothek 200 Autofahrer. Sie gehen davon aus, dass unter diesen etwa 25 alkoholisierte Personen am Steuer sitzen. Mit welcher Wahrscheinlichkeit ist ein kontrollierter Autofahrer alkoholisiert? Wie groß ist die Standardabweichung?

$$
\begin{align*}
25 &= 200 \cdot p \quad |:200\\
p &= 0{,}125\\
\sigma &= \sqrt{200\cdot 0{,}125\cdot (1-0{,}125)}\approx 4{,}6771
\end{align*}
$$

**$p$ und $\mu$ gegeben.** Auf einem Parkplatz parken erfahrungsgemäß 15 % der Autofahrer ohne gültigen Parkschein. Eine Mitarbeiterin des Ordnungsamts hat 12 Strafzettel dabei. Wie viele Fahrzeuge kann sie kontrollieren, bis im Mittel alle 12 Strafzettel verbraucht sind? Wie groß ist die Standardabweichung der Anzahl der Falschparker?

$$
\begin{align*}
12 &= n \cdot 0{,}15 \quad |:0{,}15\\
n &= 80\\
\sigma &= \sqrt{80\cdot 0{,}15\cdot (1-0{,}15)}\approx 3{,}1937
\end{align*}
$$
