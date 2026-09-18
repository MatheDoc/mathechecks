---
layout: null
permalink: /lernbereiche/finanzmathematik/rentenrechnung/beispiele/01-rentenendwert-umformen.html
---
Bestimmen Sie jeweils die gesuchte Größe.

a) Nachschüssige Rente mit $r = 2\,000$ €, $p = 3\,\%$, $n = 8$. Gesucht: $R_n$.

b) Vorschüssige Rente mit $\overline{R}_n = 30\,000$ €, $p = 2\,\%$, $n = 10$. Gesucht: $r$.

c) Nachschüssige Rente mit $r = 1\,500$ €, $R_n = 20\,000$ €, $p = 4\,\%$. Gesucht: $n$.

**Lösung zu a): Rentenendwert**

$$R_8 = \frac{2\,000 \cdot (1{,}03^8 - 1)}{1{,}03 - 1} = \frac{2\,000 \cdot 0{,}2668}{0{,}03} \approx 17\,784{,}67\,\text{€}$$

**Lösung zu b): Rate**

Die bekannten Werte werden eingesetzt; der Bruch ohne $r$ wird ausgerechnet, dann wird durch diesen Faktor geteilt:

$$\begin{aligned}
30\,000 &= \frac{r \cdot 1{,}02 \cdot (1{,}02^{10} - 1)}{1{,}02 - 1} \\
30\,000 &= r \cdot \frac{1{,}02 \cdot 0{,}2190}{0{,}02} \\
30\,000 &= r \cdot 11{,}1687 \\
r &= \frac{30\,000}{11{,}1687} \approx 2\,686{,}07\,\text{€}
\end{aligned}$$

**Lösung zu c): Laufzeit**

Zuerst wird nach $q^n$ aufgelöst, dann logarithmiert:

$$\begin{aligned}
20\,000 &= \frac{1\,500 \cdot (1{,}04^n - 1)}{0{,}04} \\
20\,000 \cdot 0{,}04 &= 1\,500 \cdot (1{,}04^n - 1) \\
\frac{800}{1\,500} + 1 &= 1{,}04^n \\
1{,}04^n &= 1{,}5333 \\
n &= \frac{\ln 1{,}5333}{\ln 1{,}04} \approx 10{,}90
\end{aligned}$$

Nach etwa $10{,}9$ Jahren – also im Laufe des 11. Jahres – ist der Endwert von $20\,000$ € erreicht.
