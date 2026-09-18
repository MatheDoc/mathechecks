---
layout: null
permalink: /lernbereiche/finanzmathematik/tilgungsrechnung/beispiele/07-sondertilgung-tilgungspause.html
---
Ein Fahrradladen nimmt ein Annuitätendarlehen über $100\,000$ € zu $4\,\%$ mit einer Laufzeit von 15 Jahren auf; die Annuität beträgt $8\,994{,}11$ €. Zusammen mit der 5. Annuität leistet er eine Sondertilgung von $20\,000$ €.

a) Wie hoch ist die Restschuld nach 5 Jahren vor und nach der Sondertilgung?

b) Wie hoch ist die neue Annuität, wenn die Gesamtlaufzeit unverändert bleibt?

c) Wie viele Jahre dauert die Rückzahlung noch, wenn stattdessen die Annuität unverändert bleibt?

**Lösung zu a): Restschuld**

$$RK_5 = 100\,000 \cdot 1{,}04^5 - \frac{8\,994{,}11 \cdot (1{,}04^5 - 1)}{0{,}04} \approx 121\,665{,}29 - 48\,715{,}00 \approx 72\,950{,}29\,\text{€}$$

Nach der Sondertilgung: $RK_5' = 72\,950{,}29 - 20\,000 = 52\,950{,}29$ €.

**Lösung zu b): Neue Annuität bei fester Laufzeit**

Es bleiben 10 Jahre. Die verringerte Restschuld wird in die Annuitätenformel eingesetzt:

$$A' = \frac{52\,950{,}29 \cdot 1{,}04^{10} \cdot 0{,}04}{1{,}04^{10} - 1} = \frac{52\,950{,}29 \cdot 1{,}4802 \cdot 0{,}04}{0{,}4802} \approx 6\,528{,}29\,\text{€}$$

**Lösung zu c): Neue Laufzeit bei fester Annuität**

Mit $A = T_1' \cdot q^n$, wobei $T_1'$ die Tilgung im ersten Jahr nach der Sondertilgung ist:

$$\begin{aligned}
T_1' &= 8\,994{,}11 - 52\,950{,}29 \cdot 0{,}04 \approx 6\,876{,}10\,\text{€} \\
8\,994{,}11 &= 6\,876{,}10 \cdot 1{,}04^n \\
1{,}04^n &\approx 1{,}3080 \\
n &= \frac{\ln 1{,}3080}{\ln 1{,}04} \approx 6{,}85
\end{aligned}$$

Statt 10 Jahren dauert die Rückzahlung nur noch etwa $6{,}85$ Jahre – die Laufzeit verkürzt sich um rund 3 Jahre.

**Ergänzung: Tilgungspause**

Wird in einem Jahr die Tilgung ausgesetzt, zahlt der Kreditnehmer nur die Zinsen $Z_k = RK_{k-1} \cdot \frac{p}{100}$; die Restschuld bleibt in diesem Jahr unverändert. Soll die Gesamtlaufzeit erhalten bleiben, wird anschließend die Annuität für die um ein Jahr kürzere Restlaufzeit neu berechnet.
