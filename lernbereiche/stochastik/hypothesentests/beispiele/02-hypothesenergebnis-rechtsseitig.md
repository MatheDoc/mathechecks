---
layout: null
permalink: /lernbereiche/stochastik/hypothesentests/beispiele/02-hypothesenergebnis-rechtsseitig.html
---
Gegeben ist ein Hypothesentest mit:

- $n=200$
- $H_0$: $p=0{,}4$
- $H_1$: $p>0{,}4$
- $A=\\{0,1,2,...,90\\}$ und $\overline{A}=\\{91,92,...,200\\}$
- Stichprobenergebnis: $k=88$

Anwendung der Entscheidungsregel: Da $88\in A$ wird die Nullhypothese angenommen und die Gegenhypothese abgelehnt.

Bestimmung der Wahrscheinlichkeit des Fehlers 1. Art

$$
\begin{align*}
P(X\geq 91) &= Bcd(91;200;200;0{,}4) \\
            &= 0{,}0655
\end{align*}
$$

Ist nun bekannt, dass $H_1$: $p=0{,}5$ gilt, beträgt die Wahrscheinlichkeit für den Fehler 2. Art:

$$
\begin{align*}
P(X\leq 90) &= Bcd(0;90;200;0{,}5) \\
            &= 0{,}0895
\end{align*}
$$