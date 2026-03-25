Es seien $n=25$ und $p=0{,}3$. Wie groß ist die Wahrscheinlichkeit, dass $X$ um höchstens die doppelte Standardabweichung vom Erwartungswert abweicht?"

Wir berechnen $\mu=7{,}5$ und $\sigma\approx 2{,}29$. Gesucht ist:

$$
\begin{align*}
P(\mu-2\sigma\leq X\leq \mu+2\sigma)&=P(7{,}5-2\cdot 2{,}29\leq X\leq 7{,}5+2\cdot 2{,}29)\\
                        &=P(2{,}92\leq X\leq 12{,}08)\\
                        &=P(3\leq X\leq 12) \\
                        &=0{,}9736
\end{align*}
$$

Alternativ könnten wir auch nach der Wahrscheinlichkeit für 'nicht-normale' Werte fragen: Mit welcher Wahrscheinlichkeit weicht $X$ um mehr als die doppelte Standardabweichung vom Erwartungswert ab (symbolisch: $P(\|\mu-X\|>2\sigma)$)? Dies entspricht dem Gegenereignis zum oben betrachteten Ereignis, daher ist

$$
P(|\mu-X|>2\sigma)=1-0{,}9736=0{,}0264
$$
