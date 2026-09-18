---
layout: null
permalink: /lernbereiche/finanzmathematik/tilgungsrechnung/beispiele/02-annuitaetenformeln-umformen.html
---
Bestimmen Sie jeweils die gesuchte Größe.

a) $K_0 = 150\,000$ €, $p = 4\,\%$, $n = 20$. Gesucht: $A$.

b) $A = 12\,000$ €, $p = 3\,\%$, $n = 15$. Gesucht: $K_0$.

c) $K_0 = 100\,000$ €, $A = 9\,000$ €, $p = 4\,\%$. Gesucht: $n$.

**Lösung zu a): Annuität**

$$A = \frac{150\,000 \cdot 1{,}04^{20} \cdot 0{,}04}{1{,}04^{20} - 1} = \frac{150\,000 \cdot 2{,}1911 \cdot 0{,}04}{1{,}1911} \approx 11\,037{,}26\,\text{€}$$

**Lösung zu b): Darlehenssumme**

Die bekannten Werte werden eingesetzt; der Bruch ohne $K_0$ wird ausgerechnet, dann wird durch diesen Faktor geteilt:

$$\begin{aligned}
12\,000 &= \frac{K_0 \cdot 1{,}03^{15} \cdot 0{,}03}{1{,}03^{15} - 1} \\
12\,000 &= K_0 \cdot \frac{1{,}5580 \cdot 0{,}03}{0{,}5580} \\
12\,000 &= K_0 \cdot 0{,}08377 \\
K_0 &= \frac{12\,000}{0{,}08377} \approx 143\,255{,}22\,\text{€}
\end{aligned}$$

Mit einer jährlichen Annuität von $12\,000$ € kann bei $3\,\%$ und 15 Jahren Laufzeit ein Darlehen von rund $143\,255$ € getilgt werden.

**Lösung zu c): Laufzeit mit $A = T_1 \cdot q^n$**

Zuerst wird die Tilgung des ersten Jahres bestimmt:

$$T_1 = A - K_0 \cdot 0{,}04 = 9\,000 - 4\,000 = 5\,000\,\text{€}$$

Dann wird die Formel nach $q^n$ aufgelöst und logarithmiert:

$$\begin{aligned}
9\,000 &= 5\,000 \cdot 1{,}04^n \\
1{,}04^n &= 1{,}8 \\
n &= \frac{\ln 1{,}8}{\ln 1{,}04} \approx 14{,}99
\end{aligned}$$

Das Darlehen ist nach etwa 15 Jahren getilgt.
