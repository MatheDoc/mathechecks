---
layout: null
permalink: /lernbereiche/finanzmathematik/tilgungsrechnung/beispiele/01-tilgungsplan-aufstellen.html
---
Ein Fotostudio nimmt ein Darlehen über $18\,000$ € auf. Der Zinssatz beträgt $3{,}5\,\%$, die Rückzahlung erfolgt durch Annuitätentilgung in 6 Jahren mit einer Annuität von $3\,378{,}03$ €. Stellen Sie die ersten beiden Zeilen des Tilgungsplans auf.

**Vorüberlegung: Woher kommt die Annuität?**

$$
A = \frac{18\,000 \cdot 1{,}035^6 \cdot 0{,}035}{1{,}035^6 - 1} \approx 3\,378{,}03\,\text{€}
$$

**Vorgehen pro Zeile**

1. Zinsen aus der Restschuld zu Jahresbeginn: $Z_k = RK_{k-1} \cdot 0{,}035$
2. Tilgung als Rest der Annuität: $T_k = A - Z_k$
3. Neue Restschuld: $RK_k = RK_{k-1} - T_k$

Jede Zelle wird auf Cent gerundet; mit den gerundeten Werten wird weitergerechnet.

**Zeile 1**

Zu Beginn ist die Restschuld die Darlehenssumme:

$$\begin{aligned}
Z_1 &= 18\,000 \cdot 0{,}035 = 630{,}00 \\
T_1 &= 3\,378{,}03 - 630{,}00 = 2\,748{,}03 \\
RK_1 &= 18\,000 - 2\,748{,}03 = 15\,251{,}97
\end{aligned}$$

**Zeile 2**

Die Restschuld am Ende des 1. Jahres ist die Restschuld zu Beginn des 2. Jahres:

$$\begin{aligned}
Z_2 &= 15\,251{,}97 \cdot 0{,}035 \approx 533{,}82 \\
T_2 &= 3\,378{,}03 - 533{,}82 = 2\,844{,}21 \\
RK_2 &= 15\,251{,}97 - 2\,844{,}21 = 12\,407{,}76
\end{aligned}$$

**Tilgungsplan (Auszug, Beträge in €)**

| Jahr | Restschuld Anfang | Zinsen | Tilgung | Annuität | Restschuld Ende |
| 1 | 18 000,00 | 630,00 | 2 748,03 | 3 378,03 | 15 251,97 |
| 2 | 15 251,97 | 533,82 | 2 844,21 | 3 378,03 | 12 407,76 |

Die Zinsen sinken mit der Restschuld, bei gleicher Annuität steigt deshalb die Tilgung. Alle weiteren Zeilen folgen demselben Schema.
