---
layout: null
permalink: /lernbereiche/finanzmathematik/tilgungsrechnung/beispiele/01-tilgungsplan-aufstellen.html
---
Ein Fotostudio nimmt ein Darlehen über $18\,000$ € auf. Der Zinssatz beträgt $3{,}5\,\%$, die Rückzahlung erfolgt durch Annuitätentilgung in 3 Jahren mit einer Annuität von $6\,424{,}82$ €. Stellen Sie den Tilgungsplan auf.

**Vorüberlegung: Woher kommt die Annuität?**

$$
A = \frac{18\,000 \cdot 1{,}035^3 \cdot 0{,}035}{1{,}035^3 - 1} = \frac{18\,000 \cdot 1{,}1087 \cdot 0{,}035}{0{,}1087} \approx 6\,424{,}82\,\text{€}
$$

**Vorgehen pro Zeile**

1. Zinsen aus der Restschuld zu Jahresbeginn: $Z_k = RK_{k-1} \cdot 0{,}035$
2. Tilgung als Rest der Annuität: $T_k = A - Z_k$
3. Neue Restschuld: $RK_k = RK_{k-1} - T_k$

Jede Zelle wird auf Cent gerundet; mit den gerundeten Werten wird weitergerechnet.

**Zeile 1**

$$\begin{aligned}
Z_1 &= 18\,000 \cdot 0{,}035 = 630{,}00 \\
T_1 &= 6\,424{,}82 - 630{,}00 = 5\,794{,}82 \\
RK_1 &= 18\,000 - 5\,794{,}82 = 12\,205{,}18
\end{aligned}$$

**Zeile 2**

$$\begin{aligned}
Z_2 &= 12\,205{,}18 \cdot 0{,}035 \approx 427{,}18 \\
T_2 &= 6\,424{,}82 - 427{,}18 = 5\,997{,}64 \\
RK_2 &= 12\,205{,}18 - 5\,997{,}64 = 6\,207{,}54
\end{aligned}$$

**Zeile 3 (letzte Zeile)**

Im letzten Jahr wird die gesamte verbliebene Restschuld getilgt. Die Annuität ergibt sich aus Zinsen plus Tilgung:

$$\begin{aligned}
Z_3 &= 6\,207{,}54 \cdot 0{,}035 \approx 217{,}26 \\
T_3 &= RK_2 = 6\,207{,}54 \\
A_3 &= 217{,}26 + 6\,207{,}54 = 6\,424{,}80
\end{aligned}$$

**Fertiger Tilgungsplan** (Beträge in €)

| Jahr | Restschuld Anfang | Zinsen | Tilgung | Annuität | Restschuld Ende |
| 1 | 18 000,00 | 630,00 | 5 794,82 | 6 424,82 | 12 205,18 |
| 2 | 12 205,18 | 427,18 | 5 997,64 | 6 424,82 | 6 207,54 |
| 3 | 6 207,54 | 217,26 | 6 207,54 | 6 424,80 | 0,00 |

Die letzte Annuität liegt um $0{,}02$ € unter der vereinbarten Annuität – das ist die **Rundungsdifferenz**. Sie entsteht durch das zeilenweise Runden auf Cent und beträgt bei kurzen Laufzeiten meist nur ein oder zwei Cent.
