---
layout: null
---
Gegeben sei ein Hypothesentest mit Stichprobenumfang $n=200$ und Signifikanzniveau $\alpha=0{,}05$. Außerdem gelte

|Nullhypothese | Gegenhypothese |
| $H_0: 0{,}4$ | $H_1: p<0{,}4$ |
| $A=\\{k+1,k+2,...,200\\}$ | $\overline{A}=\\{0,1,2,...,k\\}$ |

Gesucht ist das größte $k$, so dass $P(X\leq k)<0{,}05$.

$$
\begin{align*}
P(X\leq 68)&=Bcd(0;68;200;0{,}4)\\
            &=0{,}0475<0{,}05\\
            \\
P(X\leq 69)&=Bcd(0;69;200;0{,}4)\\
            &=0{,}0639>0{,}05
\end{align*}
$$

Damit folgt $k=68$, und somit $A=\\{69,70,...,200\\}$ und $\overline{A}=\\{0,1,2,...,68\\}$.