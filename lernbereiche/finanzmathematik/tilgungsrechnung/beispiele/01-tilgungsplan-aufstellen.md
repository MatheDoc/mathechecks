---
layout: null
permalink: /lernbereiche/finanzmathematik/tilgungsrechnung/beispiele/01-tilgungsplan-aufstellen.html
---
Ein Fotostudio nimmt ein Darlehen über $20\,000$ € auf. Der Zinssatz beträgt $5\,\%$, die Rückzahlung erfolgt durch Annuitätentilgung in 4 Jahren mit einer Annuität von $5\,640{,}24$ €. Stellen Sie den Tilgungsplan auf.

**Vorgehen pro Zeile**

1. Zinsen aus der Restschuld zu Jahresbeginn: $Z_k = RK_{k-1} \cdot 0{,}05$
2. Tilgung als Rest der Annuität: $T_k = A - Z_k$
3. Neue Restschuld: $RK_k = RK_{k-1} - T_k$

Jede Zelle wird auf Cent gerundet; mit den gerundeten Werten wird weitergerechnet.

**Zeile 1**

$$\begin{aligned}
Z_1 &= 20\,000 \cdot 0{,}05 = 1\,000{,}00 \\
T_1 &= 5\,640{,}24 - 1\,000{,}00 = 4\,640{,}24 \\
RK_1 &= 20\,000 - 4\,640{,}24 = 15\,359{,}76
\end{aligned}$$

**Zeile 2**

$$\begin{aligned}
Z_2 &= 15\,359{,}76 \cdot 0{,}05 \approx 767{,}99 \\
T_2 &= 5\,640{,}24 - 767{,}99 = 4\,872{,}25 \\
RK_2 &= 15\,359{,}76 - 4\,872{,}25 = 10\,487{,}51
\end{aligned}$$

**Zeile 3**

$$\begin{aligned}
Z_3 &= 10\,487{,}51 \cdot 0{,}05 \approx 524{,}38 \\
T_3 &= 5\,640{,}24 - 524{,}38 = 5\,115{,}86 \\
RK_3 &= 10\,487{,}51 - 5\,115{,}86 = 5\,371{,}65
\end{aligned}$$

**Zeile 4 (letzte Zeile)**

Im letzten Jahr wird die gesamte verbliebene Restschuld getilgt. Die Annuität ergibt sich aus Zinsen plus Tilgung:

$$\begin{aligned}
Z_4 &= 5\,371{,}65 \cdot 0{,}05 \approx 268{,}58 \\
T_4 &= RK_3 = 5\,371{,}65 \\
A_4 &= 268{,}58 + 5\,371{,}65 = 5\,640{,}23
\end{aligned}$$

**Fertiger Tilgungsplan** (Beträge in €)

| Jahr | Restschuld Anfang | Zinsen | Tilgung | Annuität | Restschuld Ende |
| 1 | 20 000,00 | 1 000,00 | 4 640,24 | 5 640,24 | 15 359,76 |
| 2 | 15 359,76 | 767,99 | 4 872,25 | 5 640,24 | 10 487,51 |
| 3 | 10 487,51 | 524,38 | 5 115,86 | 5 640,24 | 5 371,65 |
| 4 | 5 371,65 | 268,58 | 5 371,65 | 5 640,23 | 0,00 |

Die letzte Annuität weicht um $0{,}01$ € von der vereinbarten Annuität ab – das ist die **Rundungsdifferenz**, die durch das zeilenweise Runden entsteht.
