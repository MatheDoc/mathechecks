---
layout: null
permalink: /lernbereiche/finanzmathematik/rentenrechnung/beispiele/02-rentenbarwert-umformen.html
---
Bestimmen Sie jeweils die gesuchte Größe.

a) Nachschüssige Rente mit $r = 6\,000$ €, $p = 4\,\%$, $n = 12$. Gesucht: $R_0$.

b) Vorschüssige Rente mit $\overline{R}_0 = 50\,000$ €, $p = 3\,\%$, $n = 10$. Gesucht: $r$.

c) Nachschüssige Rente mit $r = 5\,000$ €, $R_0 = 40\,000$ €, $p = 2{,}5\,\%$. Gesucht: $n$.

**Lösung zu a): Rentenbarwert**

$$R_0 = \frac{6\,000 \cdot (1{,}04^{12} - 1)}{1{,}04^{12} \cdot 0{,}04} = \frac{6\,000 \cdot 0{,}6010}{1{,}6010 \cdot 0{,}04} \approx 56\,310{,}44\,\text{€}$$

**Lösung zu b): Rate**

$$\begin{aligned}
50\,000 &= \frac{r \cdot 1{,}03 \cdot (1{,}03^{10} - 1)}{1{,}03^{10} \cdot 0{,}03} \\
50\,000 &= r \cdot \frac{1{,}03 \cdot 0{,}3439}{1{,}3439 \cdot 0{,}03} \\
50\,000 &= r \cdot 8{,}7861 \\
r &= \frac{50\,000}{8{,}7861} \approx 5\,690{,}80\,\text{€}
\end{aligned}$$

**Lösung zu c): Laufzeit**

Die Gleichung wird mit $q^n$ multipliziert, damit $q^n$ nur noch an einer Stelle steht:

$$\begin{aligned}
40\,000 &= \frac{5\,000 \cdot (1{,}025^n - 1)}{1{,}025^n \cdot 0{,}025} \\
40\,000 \cdot 0{,}025 \cdot 1{,}025^n &= 5\,000 \cdot 1{,}025^n - 5\,000 \\
1\,000 \cdot 1{,}025^n - 5\,000 \cdot 1{,}025^n &= -5\,000 \\
-4\,000 \cdot 1{,}025^n &= -5\,000 \\
1{,}025^n &= 1{,}25 \\
n &= \frac{\ln 1{,}25}{\ln 1{,}025} \approx 9{,}04
\end{aligned}$$

Aus $40\,000$ € können etwa 9 Jahre lang $5\,000$ € nachschüssig entnommen werden.
