---
layout: null
permalink: /lernbereiche/stochastik/hypothesentests/beispiele/01-hypothesenergebnis-linksseitig.html
---
Gegeben ist ein Hypothesentest mit:

- $n=200$
- $H_0$: $p=0{,}4$
- $H_1$: $p<0{,}4$
- $A=\\{71,72,...,200\\}$ und $\overline{A}=\\{0,1,...,70\\}$
- Stichprobenergebnis: $k=69$

Anwendung der Entscheidungsregel: Da $69\in\overline{A}$ wird die Nullhypothese abgelehnt und die Gegenhypothese angenommen.

Bestimmung der Wahrscheinlichkeit des Fehlers 1. Art:

$$
\begin{align*}
P(X\leq 70) &= Bcd(0;70;200;0{,}4) \\
            &= 0{,}0844
\end{align*}
$$

Ist nun bekannt, dass $H_1$: $p=0{,}3$ gilt, beträgt die Wahrscheinlichkeit für den Fehler 2. Art:

$$
\begin{align*}
P(X\geq 71) &= Bcd(71;200;200;0{,}3) \\
            &= 0{,}0542
\end{align*}
$$