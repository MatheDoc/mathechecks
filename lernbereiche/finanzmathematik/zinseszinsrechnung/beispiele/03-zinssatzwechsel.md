---
layout: null
permalink: /lernbereiche/finanzmathematik/zinseszinsrechnung/beispiele/03-zinssatzwechsel.html
---
Eine Tischlerei legt $20\,000$ € an. In den ersten 3 Jahren wird das Kapital mit $2\,\%$ verzinst, in den folgenden 4 Jahren mit $3{,}5\,\%$.

a) Über welchen Betrag verfügt die Tischlerei nach insgesamt 7 Jahren?

b) Mit welchem einheitlichen Zinssatz hätte dasselbe Endkapital in 7 Jahren erreicht werden können?

**Lösung zu a): Zinsphasen verketten**

Das Kapital am Ende der ersten Phase ist zugleich das Anfangskapital der zweiten Phase:

$$\begin{aligned}
K_3 &= 20\,000 \cdot 1{,}02^3 = 21\,224{,}16\,\text{€} \\
K_7 &= K_3 \cdot 1{,}035^4 = 21\,224{,}16 \cdot 1{,}035^4 \approx 24\,355{,}21\,\text{€}
\end{aligned}$$

Kurzform in einer Zeile: $K_7 = 20\,000 \cdot 1{,}02^3 \cdot 1{,}035^4 \approx 24\,355{,}21$ €.

**Lösung zu b): Einheitlicher Zinssatz**

Gesucht ist $q$ mit $20\,000 \cdot q^7 = 24\,355{,}21$:

$$\begin{aligned}
q^7 &= \frac{24\,355{,}21}{20\,000} \approx 1{,}2178 \\
q &= \sqrt[7]{1{,}2178} \approx 1{,}0285
\end{aligned}$$

Ein einheitlicher Zinssatz von etwa $2{,}85\,\%$ hätte zum gleichen Endkapital geführt. Er liegt – wie zu erwarten – zwischen $2\,\%$ und $3{,}5\,\%$, aber nicht genau in der Mitte, weil die zweite Phase länger ist.

Vorgehen bei fehlender Größe: Alle bekannten Faktoren einsetzen und nach dem offenen Faktor auflösen – Wurzel, wenn ein $q$ gesucht ist, Logarithmus, wenn ein $n$ gesucht ist.
