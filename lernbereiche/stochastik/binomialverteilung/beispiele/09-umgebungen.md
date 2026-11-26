---
layout: null
permalink: /lernbereiche/stochastik/binomialverteilung/beispiele/09-umgebungen.html
---
Es seien $n=25$ und $p=0{,}3$. Dann sind

$$
\mu=25\cdot 0{,}3=7{,}5 \qquad \text{und} \qquad \sigma=\sqrt{25\cdot 0{,}3\cdot 0{,}7}\approx 2{,}29.
$$

Wie groß ist die Wahrscheinlichkeit, dass $X$

1. um höchstens $2$ vom Erwartungswert abweicht,
2. um mindestens $10\,\%$ vom Erwartungswert abweicht,
3. um höchstens die doppelte Standardabweichung vom Erwartungswert abweicht?

In allen drei Teilen wird zuerst die Abweichung vom Erwartungswert bestimmt, dann werden die Grenzen $\mu$ minus und plus Abweichung berechnet und auf ganze Anzahlen im gesuchten Bereich gerundet.

**1. Absolute Abweichung.** Die Abweichung ist $2$. „Höchstens“ bedeutet: $X$ liegt innerhalb der Grenzen.

$$
\begin{align*}
P(\mu-2\leq X\leq \mu +2)&=P(5{,}5\leq X\leq 9{,}5)\\
                        &=P(6\leq X\leq 9) \\
                        &=0{,}6171
\end{align*}
$$

**2. Relative Abweichung.** Die Abweichung ist $0{,}1\cdot\mu=0{,}75$, die Grenzen sind also $6{,}75$ und $8{,}25$. „Mindestens“ bedeutet: $X$ liegt außerhalb, die Grenzen gehören dazu. Links wird abgerundet, rechts aufgerundet:

$$
\begin{align*}
P(X\leq 6{,}75 \text{ oder } X\geq 8{,}25)&=P(X\leq 6)+P(X\geq 9)\\
                        &=1-P(7\leq X\leq 8) \\
                        &=0{,}6637
\end{align*}
$$

**3. Sigma-Umgebung.** Die Abweichung ist $2\sigma\approx 4{,}58$.

$$
\begin{align*}
P(\mu-2\sigma\leq X\leq \mu+2\sigma)&=P(2{,}92\leq X\leq 12{,}08)\\
                        &=P(3\leq X\leq 12) \\
                        &=0{,}9736
\end{align*}
$$
