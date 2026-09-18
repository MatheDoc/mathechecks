---
layout: null
permalink: /lernbereiche/finanzmathematik/tilgungsrechnung/beispiele/03-restschuldformel.html
---
Eine Kfz-Werkstatt nimmt ein Annuitätendarlehen über $200\,000$ € auf. Der Zinssatz beträgt $3{,}5\,\%$, die Laufzeit 25 Jahre, die jährliche Annuität $12\,134{,}81$ €.

a) Wie hoch ist die Restschuld nach 10 Jahren?

b) Wie hoch sind Zinsen und Tilgung im 11. Jahr?

c) Wie viel Zinsen werden über die gesamte Laufzeit gezahlt?

**Lösung zu a): Restschuldformel**

Statt zehn Zeilen des Tilgungsplans zu berechnen, wird die Restschuldformel verwendet:

$$\begin{aligned}
RK_{10} &= K_0 \cdot q^{10} - \frac{A \cdot (q^{10} - 1)}{q - 1} \\
&= 200\,000 \cdot 1{,}035^{10} - \frac{12\,134{,}81 \cdot (1{,}035^{10} - 1)}{0{,}035} \\
&\approx 200\,000 \cdot 1{,}4106 - \frac{12\,134{,}81 \cdot 0{,}4106}{0{,}035} \\
&\approx 282\,119{,}80 - 142\,358{,}28 \\
&\approx 139\,761{,}53\,\text{€}
\end{aligned}$$

Anschaulich: Das Darlehen wird 10 Jahre aufgezinst, davon wird der Endwert der 10 gezahlten Annuitäten abgezogen.

**Lösung zu b): Zinsen und Tilgung im Folgejahr**

Die Zinsen des 11. Jahres werden aus der Restschuld nach 10 Jahren berechnet:

$$\begin{aligned}
Z_{11} &= 139\,761{,}53 \cdot 0{,}035 \approx 4\,891{,}65\,\text{€} \\
T_{11} &= A - Z_{11} = 12\,134{,}81 - 4\,891{,}65 = 7\,243{,}16\,\text{€}
\end{aligned}$$

**Lösung zu c): Gesamtzinsen**

Insgesamt werden 25 Annuitäten gezahlt; davon ist alles, was über die Darlehenssumme hinausgeht, Zins:

$$Z_{\text{gesamt}} = 25 \cdot 12\,134{,}81 - 200\,000 = 303\,370{,}25 - 200\,000 = 103\,370{,}25\,\text{€}$$

Hinweis: Wegen der Rundungsdifferenz in der letzten Zeile des Tilgungsplans kann der tatsächliche Wert um wenige Cent abweichen.
