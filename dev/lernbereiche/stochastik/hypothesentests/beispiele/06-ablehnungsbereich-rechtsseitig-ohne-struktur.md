---
layout: null
---
Gegeben sei ein Hypothesentest mit Stichprobenumfang $n=200$ und Signifikanzniveau $\alpha=0{,}02$. Außerdem gelte

|Nullhypothese | Gegenhypothese |
| $H_0: 0{,}4$ | $H_1: p>0{,}4$ |
| $A=\\{0,1,2,...,k-1\\}$ | $\overline{A}=\\{k,k+1,...,200\\}$ |

Gesucht ist das kleinste $k$, so dass $P(X\geq k)<0{,}02$.

$$
\begin{align*}
P(X\geq 94)&=Bcd(94;200;200;0{,}4)\\
            &=0{,}0263>0{,}02\\
            \\
P(X\geq 95)&=Bcd(95;200;200;0{,}4)\\
            &=0{,}0188<0{,}02
\end{align*}
$$

Damit folgt $k=95$, und somit $A=\\{0,1,2,...,94\\}$ und $\overline{A}=\\{95,96,...,200\\}$.