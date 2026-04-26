---
layout: null
---

Einer Aufgabenstellung entnehmen wir:

- den Stichprobenumfang, z.B. $n=200$
- den Parameter der Nullhypothese, z.B. $p=0{,}4$
- die Form der Gegenhypothese, z.B. $p>0{,}4$
- das Signifikanzniveau, z.B. $\alpha=0{,}05$

Es handelt sich um einen rechtsseitigen Hypothesentest, da die Gegenhypothese $H_1$ die Form $p>0{,}4$ hat. Wir führen eine Unbekannte $k$ ein, um den Annahme- und Ablehungsbereich prägnant beschreiben zu können. Es gilt:

|Nullhypothese | Gegenhypothese |
| $H_0: p=0{,}4$ | $H_1: p>0{,}4$ |
| $A=\\{0,1,2,...,k-1\\}$ | $\overline{A}=\\{k,k+1,...,200\\}$ |

Der Annahme- und Ablehnungsbereich ist von der abgebildeten Gestalt, da wir uns wegen $H_1: p>0{,}4$ bei großen Stichprobenergebnissen für $H_1$ entscheiden, und bei kleinen für $H_0$.

Das Signifikanzniveau ist die maximal tolerierte Wahrscheinlichkeit für den Fehler 1. Art. Er tritt auf, wenn $H_0$ stimmt, wir uns aber für $H_1$ entscheiden, das heißt, wenn das Stichprobenergebnis in $\overline{A}$ liegt. Gesucht ist also das kleinste $k$, so dass $P(X\geq k)<0{,}05$. Mit dem Taschenrechner oder Tafelwerk ermitteln wir:

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