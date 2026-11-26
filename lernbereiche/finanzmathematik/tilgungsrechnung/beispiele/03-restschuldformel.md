---
layout: null
permalink: /lernbereiche/finanzmathematik/tilgungsrechnung/beispiele/03-restschuldformel.html
---
Eine Kfz-Werkstatt nimmt ein Annuitätendarlehen über $200\,000$ € auf. Der Zinssatz beträgt $3{,}5\,\%$, die Laufzeit 25 Jahre, die jährliche Annuität $12\,134{,}81$ €.

a) Wie hoch ist die Restschuld nach 10 Jahren?

b) Wie hoch sind Zinsen und Tilgung im 11. Jahr?

c) Um welchen Betrag weicht die Annuität im letzten Jahr von der vereinbarten Annuität ab?

**Lösung zu a): Restschuldformel**

Statt zehn Zeilen des Tilgungsplans zu berechnen, wird die Restschuldformel verwendet:

$$\begin{aligned}
RK_{10} &= K_0 \cdot q^{10} - \frac{A \cdot (q^{10} - 1)}{q - 1} \\
&= 200\,000 \cdot 1{,}035^{10} - \frac{12\,134{,}81 \cdot (1{,}035^{10} - 1)}{0{,}035} \\
&\approx 200\,000 \cdot 1{,}4106 - \frac{12\,134{,}81 \cdot 0{,}4106}{0{,}035} \\
&\approx 282\,119{,}75 - 142\,358{,}23 \\
&\approx 139\,761{,}53\,\text{€}
\end{aligned}$$

Anschaulich: Das Darlehen wird 10 Jahre aufgezinst, davon wird der Endwert der 10 gezahlten Annuitäten abgezogen.

**Lösung zu b): Zinsen und Tilgung im Folgejahr**

Die Zinsen des 11. Jahres werden aus der Restschuld nach 10 Jahren berechnet:

$$\begin{aligned}
Z_{11} &= 139\,761{,}53 \cdot 0{,}035 \approx 4\,891{,}65\,\text{€} \\
T_{11} &= A - Z_{11} = 12\,134{,}81 - 4\,891{,}65 = 7\,243{,}16\,\text{€}
\end{aligned}$$

**Lösung zu c): Letzte Annuität und Rundungsdifferenz**

Im 25. Jahr wird genau die Restschuld getilgt, die nach 24 Jahren noch offen ist. Die letzte Annuität besteht aus dieser Restschuld und ihren Zinsen für ein Jahr. Zuerst also $RK_{24}$ mit der Restschuldformel:

$$\begin{aligned}
RK_{24} &= 200\,000 \cdot 1{,}035^{24} - \frac{12\,134{,}81 \cdot (1{,}035^{24} - 1)}{0{,}035} \\
&\approx 456\,665{,}70 - 444\,941{,}35 \\
&\approx 11\,724{,}34\,\text{€}
\end{aligned}$$

Die letzte Annuität ist Tilgung plus Zinsen, also die um ein Jahr aufgezinste Restschuld (mit dem ungerundeten Wert weiterrechnen):

$$A_{25} = RK_{24} \cdot 1{,}035 \approx 12\,134{,}70\,\text{€}$$

Sie liegt um $12\,134{,}81 - 12\,134{,}70 = 0{,}11$ € unter der vereinbarten Annuität. Diese **Rundungsdifferenz** entsteht, weil die Annuität auf Cent gerundet wurde. Rechnet man den Tilgungsplan Zeile für Zeile mit gerundeten Werten durch, kann das Ergebnis um ein bis zwei Cent abweichen.
