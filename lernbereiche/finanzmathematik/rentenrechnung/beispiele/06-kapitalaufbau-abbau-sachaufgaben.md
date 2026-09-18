---
layout: null
permalink: /lernbereiche/finanzmathematik/rentenrechnung/beispiele/06-kapitalaufbau-abbau-sachaufgaben.html
---
Ein Ingenieurbüro plant Rücklagen. Die Angaben in den Teilaufgaben sind unabhängig voneinander.

a) Das Büro hat bereits $25\,000$ € angespart und zahlt weitere 12 Jahre lang jeweils am Jahresende $3\,000$ € auf dasselbe Konto ein ($3\,\%$). Wie hoch ist das Guthaben am Ende der Laufzeit?

b) Das Büro hat $60\,000$ € zu $2\,\%$ angelegt und entnimmt jeweils zu Jahresbeginn $5\,000$ €. Nach wie vielen Jahren ist das Kapital vollständig aufgebraucht?

**Schritt 1: Kombination erkennen**

In beiden Fällen gibt es ein Startkapital *und* regelmäßige Zahlungen. Deshalb werden Zinseszins- und Rentenformel kombiniert: $E_n = K_0 \cdot q^n \pm R_n$. Einzahlungen erhöhen das Kapital ($+$), Entnahmen verringern es ($-$).

**Lösung zu a): Kapitalaufbau, nachschüssig**

$$\begin{aligned}
K_0 \cdot q^n &= 25\,000 \cdot 1{,}03^{12} \approx 35\,644{,}02\,\text{€} \\
R_{12} &= \frac{3\,000 \cdot (1{,}03^{12} - 1)}{0{,}03} \approx 42\,576{,}09\,\text{€} \\
E_{12} &= 35\,644{,}02 + 42\,576{,}09 = 78\,220{,}11\,\text{€}
\end{aligned}$$

**Lösung zu b): Kapitalabbau, vorschüssig, bis $\overline{E}_n = 0$**

$$\begin{aligned}
0 &= 60\,000 \cdot 1{,}02^n - \frac{5\,000 \cdot 1{,}02 \cdot (1{,}02^n - 1)}{0{,}02} \\
0 &= 60\,000 \cdot 1{,}02^n - 255\,000 \cdot (1{,}02^n - 1) \\
0 &= -195\,000 \cdot 1{,}02^n + 255\,000 \\
1{,}02^n &= \frac{255\,000}{195\,000} \approx 1{,}3077 \\
n &= \frac{\ln 1{,}3077}{\ln 1{,}02} \approx 13{,}55
\end{aligned}$$

Das Kapital reicht für etwa $13{,}5$ Jahre: 13 volle Entnahmen von $5\,000$ €, die 14. Entnahme ist nur noch teilweise möglich.
