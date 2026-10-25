---
layout: null
permalink: /lernbereiche/analysis/marktgleichgewicht-vertiefung/beispiele/02-kennzahlen-rechnerisch-lqe.html
---
Gegeben sind die Nachfragefunktion $p_N$ und die Angebotsfunktion $p_A$ mit

$$
\begin{align*}
p_N(x)&=80e^{-0{,}04x}-10\\
p_A(x)&=0{,}02x^2+0{,}5x+5.
\end{align*}
$$

Berechnen Sie den Höchstpreis, die Sättigungsmenge, den Mindestangebotspreis, das Marktgleichgewicht und den Umsatz im Marktgleichgewicht. Bestimmen Sie außerdem Art und Höhe des Überschusses, wenn der Preis auf $40$ GE/ME festgelegt wird.

**Höchstpreis und Mindestangebotspreis**

$$
\begin{align*}
p_N(0)&=80-10=70\\
p_A(0)&=5
\end{align*}
$$

Der Höchstpreis beträgt $70$ GE/ME, der Mindestangebotspreis $5$ GE/ME.

**Sättigungsmenge**

$$
\begin{align*}
80e^{-0{,}04x}-10&=0\\
e^{-0{,}04x}&=0{,}125\\
x&=\frac{\ln(0{,}125)}{-0{,}04}\approx 51{,}99
\end{align*}
$$

Die Sättigungsmenge beträgt etwa $51{,}99$ ME.

**Marktgleichgewicht**

$$
\begin{align*}
80e^{-0{,}04x}-10&=0{,}02x^2+0{,}5x+5 \quad |\text{ CAS}\\
x_G&\approx 21{,}08\\
p_G&=p_N(21{,}08)\approx 24{,}43
\end{align*}
$$

Die Gleichgewichtsmenge beträgt etwa $21{,}08$ ME, der Gleichgewichtspreis etwa $24{,}43$ GE/ME.

**Umsatz im Marktgleichgewicht**

$$
x_G\cdot p_G\approx 21{,}0797\cdot 24{,}4269\approx 514{,}91
$$

Der Umsatz im Marktgleichgewicht beträgt etwa $514{,}91$ GE.

**Überschuss bei festgelegtem Preis von 40 GE/ME**

$$
\begin{align*}
p_N(x)=40 &\Rightarrow 80e^{-0{,}04x}=50 \Rightarrow x_N=\frac{\ln(0{,}625)}{-0{,}04}\approx 11{,}75\\
p_A(x)=40 &\Rightarrow 0{,}02x^2+0{,}5x-35=0 \Rightarrow x_A\approx 31{,}16 \quad (x\approx -56{,}16 \text{ entfällt})
\end{align*}
$$

Da $40$ GE/ME über dem Gleichgewichtspreis liegt, wird mehr angeboten als nachgefragt. Es besteht ein Angebotsüberschuss von $31{,}16-11{,}75=19{,}41$ ME.
