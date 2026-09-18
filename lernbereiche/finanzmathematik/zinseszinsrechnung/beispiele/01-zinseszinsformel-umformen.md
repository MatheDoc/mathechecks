---
layout: null
permalink: /lernbereiche/finanzmathematik/zinseszinsrechnung/beispiele/01-zinseszinsformel-umformen.html
---
Ein Kapital wird jährlich mit Zinseszins verzinst. Bestimmen Sie jeweils die gesuchte Größe.

a) $K_0 = 8\,000$ €, $p = 3\,\%$, $n = 6$. Gesucht: $K_n$.

b) $K_n = 12\,000$ €, $p = 2{,}5\,\%$, $n = 10$. Gesucht: $K_0$.

c) $K_0 = 5\,000$ €, $K_n = 6\,500$ €, $n = 8$. Gesucht: $p$.

d) $K_0 = 10\,000$ €, $K_n = 15\,000$ €, $p = 4\,\%$. Gesucht: $n$.

**Vorüberlegung: Zinsfaktor**

Aus dem Zinssatz wird der Zinsfaktor gebildet: $q = 1 + \frac{p}{100}$. Für $p = 3\,\%$ ist also $q = 1{,}03$.

**Lösung zu a): Endkapital**

$$K_6 = 8\,000 \cdot 1{,}03^6 = 8\,000 \cdot 1{,}1941 \approx 9\,552{,}42\,\text{€}$$

**Lösung zu b): Anfangskapital**

Alle bekannten Werte werden eingesetzt, dann wird nach $K_0$ aufgelöst:

$$\begin{aligned}
12\,000 &= K_0 \cdot 1{,}025^{10} \\
12\,000 &= K_0 \cdot 1{,}2801 \\
K_0 &= \frac{12\,000}{1{,}2801} \approx 9\,374{,}38\,\text{€}
\end{aligned}$$

**Lösung zu c): Zinssatz**

$$\begin{aligned}
6\,500 &= 5\,000 \cdot q^8 \\
q^8 &= 1{,}3 \\
q &= \sqrt[8]{1{,}3} \approx 1{,}0333
\end{aligned}$$

Der Zinssatz beträgt $p = (q - 1) \cdot 100 \approx 3{,}33\,\%$.

**Lösung zu d): Laufzeit**

$$\begin{aligned}
15\,000 &= 10\,000 \cdot 1{,}04^n \\
1{,}04^n &= 1{,}5 \\
n &= \frac{\ln 1{,}5}{\ln 1{,}04} \approx 10{,}34
\end{aligned}$$

Das Kapital ist nach etwa $10{,}34$ Jahren auf $15\,000$ € angewachsen.

Tipp: Zwischenwerte wie $q^n$ mit mindestens vier Nachkommastellen weiterrechnen, sonst wird das Ergebnis bei großen Beträgen ungenau.
