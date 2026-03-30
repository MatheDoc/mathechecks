---
layout: null
---

Einer Aufgabenstellung entnehmen wir:

- den Stichprobenumfang, z.B. $n=200$
- den Parameter der Nullhypothese, z.B. $p=0{,}4$
- die Form der Gegenhypothese, z.B. $p<0{,}4$
- das Signifikanzniveau, z.B. $\alpha=0{,}05$

Es handelt sich um einen linksseitigen Hypothesentest, da die Gegenhypothese $H_1$ die Form $p<0{,}4$ hat. Wir führen eine Unbekannte $k$ ein, um den Annahme- und Ablehungsbereich prägnant beschreiben zu können. Es gilt:

|Nullhypothese | Gegenhypothese |
| $H_0: 0{,}4$ | $H_1: p<0{,}4$ |
| $A=\\{k+1,k+2,...,200\\}$ | $\overline{A}=\\{0,1,2,...,k\\}$ |

Der Annahme- und Ablehnungsbereich ist von der abgebildeten Gestalt, da wir uns wegen $H_1: p<0{,}4$ bei kleinen Stichprobenergebnissen für $H_1$ entscheiden, und bei großen für $H_0$.

Das Signifikanzniveau ist die maximal tolerierte Wahrscheinlichkeit für den Fehler 1. Art. Er tritt auf, wenn $H_0$ stimmt, wir uns aber für $H_1$ entscheiden, das heißt, wenn das Stichprobenergebnis in $\overline{A}$ liegt. Gesucht ist also das größte $k$, so dass $P(X\leq k)<0{,}05$. Mit dem Taschenrechner oder Tafelwerk ermitteln wir:

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