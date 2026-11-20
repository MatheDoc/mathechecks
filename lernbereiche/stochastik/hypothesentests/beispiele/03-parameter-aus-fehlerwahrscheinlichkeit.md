---
layout: null
permalink: /lernbereiche/stochastik/hypothesentests/beispiele/03-parameter-aus-fehlerwahrscheinlichkeit.html
---

**Beispiel 1: $p_0$ der Nullhypothese gesucht (Fehler 1. Art gegeben)**

Ein Getränkehersteller druckt in einen Teil seiner Kronkorken einen Gewinncode. Es wird vermutet, dass der Anteil der Kronkorken mit Gewinncode gesunken ist. Dazu wird ein linksseitiger Test durchgeführt: 80 Kronkorken werden zufällig ausgewählt. Werden höchstens 22 Kronkorken mit Gewinncode gefunden, wird $H_0$ verworfen. Die Wahrscheinlichkeit für den Fehler 1. Art beträgt $0{,}0324$.

Gesucht: der bisherige Anteil $p_0$

|Nullhypothese | Gegenhypothese |
| $H_0: p=p_0$ | $H_1: p<p_0$ |
| $A=\\{23,24,\ldots,80\\}$ | $\overline{A}=\\{0,1,\ldots,22\\}$ |

Der Fehler 1. Art tritt ein, wenn $H_0$ zutrifft, das Ergebnis aber im Ablehnungsbereich liegt. Es muss also gelten:

$$P(X\leq 22)=Bcd(0;22;80;p_0)=0{,}0324$$

Durch Probieren mit dem Taschenrechner:

$$
\begin{align*}
Bcd(0;22;80;0{,}37)&=0{,}0479>0{,}0324\\
Bcd(0;22;80;0{,}38)&=0{,}0324=0{,}0324\quad\checkmark\\
Bcd(0;22;80;0{,}39)&=0{,}0213<0{,}0324
\end{align*}
$$

Damit gilt $p_0=0{,}38$: Bisher trugen 38 % der Kronkorken einen Gewinncode.

---

**Beispiel 2: Stichprobenumfang $n$ gesucht (Fehler 2. Art gegeben)**

Bisher tragen 40 % der Kronkorken einen Gewinncode. Es wird vermutet, dass dieser Anteil gesunken ist. Werden in der Stichprobe höchstens 32 Kronkorken mit Gewinncode gefunden, wird $H_0$ verworfen. Tatsächlich beträgt der Anteil nur noch 28 %. Die Wahrscheinlichkeit für den Fehler 2. Art beträgt $0{,}1580$.

Gesucht: der Stichprobenumfang $n$

|Nullhypothese | Gegenhypothese |
| $H_0: p=0{,}4$ | $H_1: p<0{,}4$ |
| $A=\\{33,34,\ldots,n\\}$ | $\overline{A}=\\{0,1,\ldots,32\\}$ |

Der Fehler 2. Art tritt ein, wenn tatsächlich $p=0{,}28$ gilt, das Ergebnis aber im Annahmebereich liegt. Es muss also gelten:

$$P(X\geq 33)=Bcd(33;n;n;0{,}28)=0{,}1580$$

Durch Probieren mit dem Taschenrechner:

$$
\begin{align*}
Bcd(33;99;99;0{,}28)&=0{,}1427<0{,}1580\\
Bcd(33;100;100;0{,}28)&=0{,}1580=0{,}1580\quad\checkmark\\
Bcd(33;101;101;0{,}28)&=0{,}1743>0{,}1580
\end{align*}
$$

Damit gilt $n=100$: Es wurden 100 Kronkorken untersucht.
