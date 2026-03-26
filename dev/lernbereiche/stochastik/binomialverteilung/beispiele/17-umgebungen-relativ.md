---
layout: null
---
Es seien $n=25$ und $p=0{,}3$. Wie groß ist die Wahrscheinlichkeit, dass $X$ um höchstens $10\%$ vom Erwartungswert abweicht?

Wir berechnen $\mu=7{,}5$. Gesucht ist:

$$
\begin{align*}
P(0{,}9\cdot \mu\leq X\leq 1{,}1\cdot \mu)&=P(0{,}9\cdot 7{,}5\leq X\leq 1{,}1\cdot 7{,}5)\\
                        &=P(6{,}75\leq X\leq 8{,}25)\\
                        &=P(7\leq X\leq 8) \\
                        &=0{,}3363
\end{align*}
$$

Alternativ könnten wir auch nach der Wahrscheinlichkeit für 'nicht-normale' Werte fragen: Mit welcher Wahrscheinlichkeit weicht $X$ um mehr als $10\%$ vom Erwartungswert ab (symbolisch: $P(\|\mu-X\|>0{,}1\cdot\mu=0{,}75)$)? Dies entspricht dem Gegenereignis zum oben betrachteten Ereignis, daher ist

$$
P(|\mu-X|>0{,}75)=1-0{,}3363=0{,}6637
$$
