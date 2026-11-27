---
layout: null
permalink: /lernbereiche/finanzmathematik/rentenrechnung/beispiele/05-kapitalaufbau-abbau-umformen.html
---
Bestimmen Sie jeweils die gesuchte Größe.

a) Kapitalaufbau mit nachschüssigen Zahlungen: $K_0 = 10\,000$ €, $r = 1\,200$ €, $p = 3\,\%$, $n = 8$. Gesucht: $E_n$.

b) Kapitalabbau mit vorschüssigen Zahlungen: $K_0 = 80\,000$ €, $r = 7\,000$ €, $p = 2\,\%$, $\overline{E}_n = 0$ €. Gesucht: $n$.

**Lösung zu a): Endkapital beim Kapitalaufbau**

Das Startkapital wird mit der Zinseszinsformel aufgezinst, die Einzahlungen mit der Rentenendwertformel bewertet; beide Anteile werden addiert:

$$\begin{aligned}
K_0 \cdot q^n &= 10\,000 \cdot 1{,}03^8 \approx 12\,667{,}70\,\text{€} \\
R_n &= \frac{1\,200 \cdot (1{,}03^8 - 1)}{0{,}03} \approx 10\,670{,}80\,\text{€} \\
E_8 &= 12\,667{,}70 + 10\,670{,}80 = 23\,338{,}50\,\text{€}
\end{aligned}$$

**Lösung zu b): Laufzeit beim Kapitalabbau**

Das Kapital ist aufgebraucht, wenn $\overline{E}_n = 0$:

$$0 = 80\,000 \cdot 1{,}02^n - \frac{7\,000 \cdot 1{,}02 \cdot (1{,}02^n - 1)}{0{,}02}$$

Der Bruch wird ausgerechnet ($\frac{7\,000 \cdot 1{,}02}{0{,}02} = 357\,000$) und $q^n$ ausgeklammert:

$$\begin{aligned}
0 &= 80\,000 \cdot 1{,}02^n - 357\,000 \cdot 1{,}02^n + 357\,000 \\
0 &= 1{,}02^n \cdot (80\,000 - 357\,000) + 357\,000 \\
277\,000 \cdot 1{,}02^n &= 357\,000 \\
1{,}02^n &= \frac{357\,000}{277\,000} \approx 1{,}2888 \\
n &= \frac{\ln 1{,}2888}{\ln 1{,}02} \approx 12{,}81
\end{aligned}$$

Das Kapital reicht für etwa $12{,}8$ Jahre, also für 12 volle Entnahmen von $7\,000$ € und eine kleinere Restentnahme im 13. Jahr.
