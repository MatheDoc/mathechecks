---
layout: null
permalink: /lernbereiche/finanzmathematik/tilgungsrechnung/beispiele/05-tilgungsplan-vervollstaendigen.html
---
Von einem Tilgungsplan (Annuitätentilgung, Beträge in €) ist nur der folgende Auszug bekannt:

| Jahr | Restschuld Anfang | Zinsen | Tilgung | Annuität | Restschuld Ende |
| 4 | 44 682,76 | 2 010,72 | ? | 7 582,73 | ? |
| 5 | ? | ? | ? | ? | ? |

a) Mit welchem Zinssatz wird das Darlehen verzinst?

b) Vervollständigen Sie die beiden Zeilen.

c) Wie hoch war die Restschuld zu Beginn des 3. Jahres?

**Lösung zu a): Zinssatz aus einer Zeile**

Zinsen und Restschuld zu Jahresbeginn stehen in derselben Zeile, also:

$$p = \frac{Z_4}{RK_3} \cdot 100 = \frac{2\,010{,}72}{44\,682{,}76} \cdot 100 \approx 4{,}5\,\%$$

**Lösung zu b): Zeilen vervollständigen**

Zeile 4 wird mit $T_k = A - Z_k$ und $RK_k = RK_{k-1} - T_k$ ergänzt:

$$\begin{aligned}
T_4 &= 7\,582{,}73 - 2\,010{,}72 = 5\,572{,}01 \\
RK_4 &= 44\,682{,}76 - 5\,572{,}01 = 39\,110{,}75
\end{aligned}$$

Die Restschuld am Ende des 4. Jahres ist die Restschuld zu Beginn des 5. Jahres. Damit:

$$\begin{aligned}
Z_5 &= 39\,110{,}75 \cdot 0{,}045 \approx 1\,759{,}98 \\
T_5 &= 7\,582{,}73 - 1\,759{,}98 = 5\,822{,}75 \\
RK_5 &= 39\,110{,}75 - 5\,822{,}75 = 33\,288{,}00
\end{aligned}$$

| Jahr | Restschuld Anfang | Zinsen | Tilgung | Annuität | Restschuld Ende |
| 4 | 44 682,76 | 2 010,72 | 5 572,01 | 7 582,73 | 39 110,75 |
| 5 | 39 110,75 | 1 759,98 | 5 822,75 | 7 582,73 | 33 288,00 |

**Lösung zu c): Rückwärts rechnen**

Gesucht ist $RK_2$, die Restschuld zu Beginn des 3. Jahres. Für Zeile 3 gilt $RK_3 = RK_2 - T_3$ mit $T_3 = A - RK_2 \cdot 0{,}045$. Einsetzen:

$$\begin{aligned}
RK_3 &= RK_2 - (A - 0{,}045 \cdot RK_2) = 1{,}045 \cdot RK_2 - A \\
RK_2 &= \frac{RK_3 + A}{1{,}045} = \frac{44\,682{,}76 + 7\,582{,}73}{1{,}045} \approx 50\,014{,}82\,\text{€}
\end{aligned}$$

Merkregel für die Rückwärtsrechnung: Restschuld am Jahresanfang $= \dfrac{\text{Restschuld am Jahresende} + A}{q}$.
