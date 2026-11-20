---
layout: null
permalink: /lernbereiche/stochastik/hypothesentests/beispiele/02-ablehnungsbereich.html
---
Ein Versandhändler weiß aus Erfahrung, dass 40 % aller Bestellungen mit Expressversand aufgegeben werden. Zur Überprüfung werden 200 Bestellungen zufällig ausgewählt. $X$ ist die Anzahl der Expressbestellungen in der Stichprobe. Das Signifikanzniveau soll $\alpha=5\\,\%$ betragen.

**Linksseitiger Test**

Es wird vermutet, dass der Anteil der Expressbestellungen gesunken ist.

|Nullhypothese | Gegenhypothese |
| $H_0: p=0{,}4$ | $H_1: p<0{,}4$ |
| $A=\\{k+1,k+2,\ldots,200\\}$ | $\overline{A}=\\{0,1,2,\ldots,k\\}$ |

Gesucht ist das größte $k$, sodass $P(X\leq k)\leq 0{,}05$.

$$
\begin{align*}
P(X\leq 68)&=Bcd(0;68;200;0{,}4)\\
            &=0{,}0475\leq 0{,}05\\
            \\
P(X\leq 69)&=Bcd(0;69;200;0{,}4)\\
            &=0{,}0639>0{,}05
\end{align*}
$$

Damit folgt $k=68$, also $A=\\{69,70,\ldots,200\\}$ und $\overline{A}=\\{0,1,2,\ldots,68\\}$.

Werden höchstens 68 Expressbestellungen gezählt, gehen wir also von einem gesunkenen Anteil aus.

**Rechtsseitiger Test**

Nun wird umgekehrt vermutet, dass der Anteil der Expressbestellungen gestiegen ist.

|Nullhypothese | Gegenhypothese |
| $H_0: p=0{,}4$ | $H_1: p>0{,}4$ |
| $A=\\{0,1,2,\ldots,k-1\\}$ | $\overline{A}=\\{k,k+1,\ldots,200\\}$ |

Gesucht ist das kleinste $k$, sodass $P(X\geq k)\leq 0{,}05$.

$$
\begin{align*}
P(X\geq 91)&=Bcd(91;200;200;0{,}4)\\
            &=0{,}0655>0{,}05\\
            \\
P(X\geq 92)&=Bcd(92;200;200;0{,}4)\\
            &=0{,}0492\leq 0{,}05
\end{align*}
$$

Damit folgt $k=92$, also $A=\\{0,1,2,\ldots,91\\}$ und $\overline{A}=\\{92,93,\ldots,200\\}$.

Werden mindestens 92 Expressbestellungen gezählt, gehen wir also von einem gestiegenen Anteil aus.
