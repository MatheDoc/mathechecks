---
layout: null
permalink: /lernbereiche/stochastik/hypothesentests/beispiele/01-hypothesenergebnis.html
---
Ein Versandhändler weiß aus Erfahrung, dass 40 % aller Bestellungen mit Expressversand aufgegeben werden. Zur Überprüfung werden 200 Bestellungen zufällig ausgewählt. $X$ ist die Anzahl der Expressbestellungen in der Stichprobe.

**Linksseitiger Test**

Es wird vermutet, dass der Anteil der Expressbestellungen gesunken ist. Werden höchstens 70 Expressbestellungen gezählt, geht man von einem gesunkenen Anteil aus.

|Nullhypothese | Gegenhypothese |
| $H_0: p=0{,}4$ | $H_1: p<0{,}4$ |
| $A=\\{71,72,\ldots,200\\}$ | $\overline{A}=\\{0,1,\ldots,70\\}$ |

*Entscheidung:* In der Stichprobe werden 69 Expressbestellungen gezählt. Da $69\in\overline{A}$, wird $H_0$ verworfen: Man geht davon aus, dass der Anteil gesunken ist.

*Fehler 1. Art:* Man schließt auf einen gesunkenen Anteil, obwohl er weiterhin 40 % beträgt. Die Wahrscheinlichkeit dafür ist

$$
\begin{align*}
P(X\leq 70) &= Bcd(0;70;200;0{,}4) \\
            &= 0{,}0844
\end{align*}
$$

*Fehler 2. Art:* Angenommen, der Anteil ist tatsächlich auf 30 % gesunken. Man bleibt aber beim bisherigen Wert von 40 %. Die Wahrscheinlichkeit dafür ist

$$
\begin{align*}
P(X\geq 71) &= Bcd(71;200;200;0{,}3) \\
            &= 0{,}0542
\end{align*}
$$

**Rechtsseitiger Test**

Nun wird umgekehrt vermutet, dass der Anteil der Expressbestellungen gestiegen ist. Werden mindestens 91 Expressbestellungen gezählt, geht man von einem gestiegenen Anteil aus.

|Nullhypothese | Gegenhypothese |
| $H_0: p=0{,}4$ | $H_1: p>0{,}4$ |
| $A=\\{0,1,\ldots,90\\}$ | $\overline{A}=\\{91,92,\ldots,200\\}$ |

*Entscheidung:* In der Stichprobe werden 88 Expressbestellungen gezählt. Da $88\in A$, wird $H_0$ beibehalten: Man geht weiterhin von einem Anteil von 40 % aus.

*Fehler 1. Art:* Man schließt auf einen gestiegenen Anteil, obwohl er weiterhin 40 % beträgt. Die Wahrscheinlichkeit dafür ist

$$
\begin{align*}
P(X\geq 91) &= Bcd(91;200;200;0{,}4) \\
            &= 0{,}0655
\end{align*}
$$

*Fehler 2. Art:* Angenommen, der Anteil ist tatsächlich auf 50 % gestiegen. Man bleibt aber beim bisherigen Wert von 40 %. Die Wahrscheinlichkeit dafür ist

$$
\begin{align*}
P(X\leq 90) &= Bcd(0;90;200;0{,}5) \\
            &= 0{,}0895
\end{align*}
$$
