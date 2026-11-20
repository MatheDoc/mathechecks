---
layout: null
permalink: /lernbereiche/stochastik/hypothesentests/beispiele/07-parameter-aus-fehlerwahrscheinlichkeit.html
---

**Beispiel 1: $p_0$ der Nullhypothese gesucht (Fehler 1. Art gegeben)**

Gegeben ist ein linksseitiger Hypothesentest mit:

- $n=80$
- Ablehnungsbereich $\overline{A}=\\{0,1,\ldots,22\\}$
- Wahrscheinlichkeit für den Fehler 1. Art: $\alpha=0{,}0324$

Gesucht: $p_0$

Die Wahrscheinlichkeit für den Fehler 1. Art beim linksseitigen Test ist $P(X\leq 22)$. Es muss also gelten:

$$P(X\leq 22)=Bcd(0;22;80;p_0)=0{,}0324$$

Durch Probieren mit dem Taschenrechner:

$$
\begin{align*}
Bcd(0;22;80;0{,}37)&=0{,}0479>0{,}0324\\
Bcd(0;22;80;0{,}38)&=0{,}0324=0{,}0324\quad\checkmark\\
Bcd(0;22;80;0{,}39)&=0{,}0213<0{,}0324
\end{align*}
$$

Damit gilt $p_0=0{,}38$.

---

**Beispiel 2: Stichprobenumfang $n$ gesucht (Fehler 2. Art gegeben)**

Gegeben ist ein linksseitiger Hypothesentest mit:

- $H_0$: $p=0{,}40$, $H_1$: $p<0{,}40$
- Ablehnungsbereich $\overline{A}=\\{0,1,\ldots,32\\}$
- tatsächliche Wahrscheinlichkeit $p_1=0{,}28$
- Wahrscheinlichkeit für den Fehler 2. Art: $\beta=0{,}1580$

Gesucht: $n$

Die Wahrscheinlichkeit für den Fehler 2. Art beim linksseitigen Test ist $P(X>32)$. Es muss also gelten:

$$Bcd(33;n;n;0{,}28)=0{,}1580$$

Durch Probieren mit dem Taschenrechner:

$$
\begin{align*}
Bcd(33;99;99;0{,}28)&=0{,}1427<0{,}1580\\
Bcd(33;33;100;0{,}28)&=0{,}1580=0{,}1580\quad\checkmark\\
Bcd(33;101;101;0{,}28)&=0{,}1743>0{,}1580
\end{align*}
$$

Damit gilt $n=100$.
