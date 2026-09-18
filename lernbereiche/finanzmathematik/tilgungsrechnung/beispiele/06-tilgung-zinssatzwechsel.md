---
layout: null
permalink: /lernbereiche/finanzmathematik/tilgungsrechnung/beispiele/06-tilgung-zinssatzwechsel.html
---
Ein Pflegedienst nimmt ein Annuitätendarlehen über $250\,000$ € mit einer Laufzeit von 20 Jahren auf. Der Zinssatz beträgt zunächst $3\,\%$. Nach 5 Jahren wird der Zinssatz auf $4{,}5\,\%$ angepasst; die Gesamtlaufzeit bleibt unverändert.

a) Wie hoch ist die ursprüngliche Annuität?

b) Wie hoch ist die Restschuld nach 5 Jahren?

c) Wie hoch ist die neue Annuität für die verbleibenden 15 Jahre?

**Lösung zu a): Ursprüngliche Annuität**

$$A_1 = \frac{250\,000 \cdot 1{,}03^{20} \cdot 0{,}03}{1{,}03^{20} - 1} = \frac{250\,000 \cdot 1{,}8061 \cdot 0{,}03}{0{,}8061} \approx 16\,803{,}93\,\text{€}$$

**Lösung zu b): Restschuld zum Zeitpunkt des Wechsels**

$$\begin{aligned}
RK_5 &= 250\,000 \cdot 1{,}03^5 - \frac{16\,803{,}93 \cdot (1{,}03^5 - 1)}{0{,}03} \\
&\approx 250\,000 \cdot 1{,}1593 - \frac{16\,803{,}93 \cdot 0{,}1593}{0{,}03} \\
&\approx 289\,818{,}52 - 89\,214{,}35 \\
&\approx 200\,604{,}17\,\text{€}
\end{aligned}$$

**Lösung zu c): Neue Annuität**

Die Restschuld wird wie ein neues Darlehen behandelt: neues $K_0 = 200\,604{,}17$ €, neues $n = 15$, neuer Zinsfaktor $q = 1{,}045$.

$$A_2 = \frac{200\,604{,}17 \cdot 1{,}045^{15} \cdot 0{,}045}{1{,}045^{15} - 1} = \frac{200\,604{,}17 \cdot 1{,}9353 \cdot 0{,}045}{0{,}9353} \approx 18\,679{,}02\,\text{€}$$

Durch den höheren Zinssatz steigt die jährliche Belastung um rund $1\,875$ €.

Drei Schritte beim Zinssatzwechsel: Restschuld bestimmen → Restschuld, Restlaufzeit und neuen Zinsfaktor in die Annuitätenformel einsetzen → Tilgungsplan mit der neuen Annuität fortführen.
