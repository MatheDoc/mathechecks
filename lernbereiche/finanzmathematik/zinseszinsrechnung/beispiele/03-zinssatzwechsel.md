---
layout: null
permalink: /lernbereiche/finanzmathematik/zinseszinsrechnung/beispiele/03-zinssatzwechsel.html
---
Eine Tischlerei legt $20\,000$ € an. In den ersten 3 Jahren wird das Kapital mit $2\,\%$ verzinst, anschließend 5 Jahre lang mit einem anderen Zinssatz. Nach insgesamt 8 Jahren beträgt das Guthaben $25\,200$ €.

a) Wie hoch ist das Guthaben am Ende der ersten Zinsphase?

b) Mit welchem Zinssatz wurde das Kapital in der zweiten Zinsphase verzinst?

**Schritt 1: Gegeben und gesucht am Zeitstrahl ordnen**

| | Phase 1 | Phase 2 |
| Dauer | $n_1 = 3$ | $n_2 = 5$ |
| Zinssatz | $p_1 = 2\,\%$ | $p_2$ gesucht |
| Kapital am Anfang | $K_0 = 20\,000$ € | $K_3 = \,?$ |
| Kapital am Ende | $K_3 = \,?$ | $K_8 = 25\,200$ € |

Der Zwischenwert $K_3$ verbindet beide Phasen. Die Unbekannte liegt in Phase 2, also wird $K_3$ vorwärts aus Phase 1 berechnet.

**Lösung zu a): Zwischenwert vorwärts berechnen**

$$
K_3 = 20\,000 \cdot 1{,}02^3 \approx 21\,224{,}16\,\text{€}
$$

**Lösung zu b): Zinseszinsformel in Phase 2 nach $q_2$ auflösen**

In der zweiten Phase ist $K_3$ das Anfangskapital und $K_8$ das Endkapital:

$$
\begin{aligned}
25\,200 &= 21\,224{,}16 \cdot q_2^5 \\
q_2^5 &= \frac{25\,200}{21\,224{,}16} \approx 1{,}1873 \\
q_2 &= \sqrt[5]{1{,}1873} \approx 1{,}0349
\end{aligned}
$$

In der zweiten Phase wurde das Kapital mit etwa $3{,}49\,\%$ verzinst.

**Variante: Unbekannte in Phase 1**

Wäre stattdessen der Zinssatz der *ersten* Phase gesucht (bekannt: $p_2 = 3{,}5\,\%$, $K_8 = 25\,200$ €), müsste $K_3$ rückwärts aus dem Endkapital bestimmt werden:

$$
K_3 = \frac{25\,200}{1{,}035^5} \approx 21\,217{,}72\,\text{€}, \qquad
q_1 = \sqrt[3]{\frac{21\,217{,}72}{20\,000}} \approx 1{,}0199
$$

also $p_1 \approx 1{,}99\,\%$. Die erste Teilfrage lautet in beiden Fällen gleich, die Rechenrichtung ist aber verschieden – deshalb lohnt sich der Blick auf den Zeitstrahl, bevor gerechnet wird.
