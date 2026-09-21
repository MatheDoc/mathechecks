---
layout: null
permalink: /lernbereiche/finanzmathematik/tilgungsrechnung/beispiele/07-sondertilgung-tilgungspause.html
---
Ein Fahrradladen nimmt ein Annuitätendarlehen über $100\,000$ € zu $4\,\%$ mit einer Laufzeit von 15 Jahren auf; die Annuität beträgt $8\,994{,}11$ €. Zusammen mit der 5. Annuität leistet er eine Sondertilgung von $20\,000$ €.

a) Wie hoch ist die Restschuld nach 5 Jahren vor und nach der Sondertilgung?

b) Die Gesamtlaufzeit von 15 Jahren soll unverändert bleiben. Wie hoch ist die neue Annuität für die verbleibenden 10 Jahre?

c) Stattdessen bleibt die Annuität unverändert. Wie viele Jahre dauert die Rückzahlung ab der Sondertilgung noch?

**Lösung zu a): Restschuld**

$$RK_5 = 100\,000 \cdot 1{,}04^5 - \frac{8\,994{,}11 \cdot (1{,}04^5 - 1)}{0{,}04} \approx 121\,665{,}29 - 48\,715{,}00 \approx 72\,950{,}29\,\text{€}$$

Nach der Sondertilgung: $RK_5' = 72\,950{,}29 - 20\,000 = 52\,950{,}29$ €.

**Lösung zu b): Laufzeit fest, Annuität neu**

Die verringerte Restschuld ist das „neue Darlehen“, die Restlaufzeit von 10 Jahren das neue $n$:

$$A' = \frac{52\,950{,}29 \cdot 1{,}04^{10} \cdot 0{,}04}{1{,}04^{10} - 1} = \frac{52\,950{,}29 \cdot 1{,}4802 \cdot 0{,}04}{0{,}4802} \approx 6\,528{,}29\,\text{€}$$

Die jährliche Belastung sinkt um rund $2\,466$ €.

**Lösung zu c): Annuität fest, Laufzeit neu**

Mit $A = T_1' \cdot q^n$, wobei $T_1'$ die Tilgung im ersten Jahr nach der Sondertilgung ist:

$$\begin{aligned}
T_1' &= 8\,994{,}11 - 52\,950{,}29 \cdot 0{,}04 \approx 6\,876{,}10\,\text{€} \\
8\,994{,}11 &= 6\,876{,}10 \cdot 1{,}04^n \\
1{,}04^n &\approx 1{,}3080 \\
n &= \frac{\ln 1{,}3080}{\ln 1{,}04} \approx 6{,}85
\end{aligned}$$

Statt 10 Jahren dauert die Rückzahlung nur noch etwa $6{,}85$ Jahre – die Laufzeit verkürzt sich um gut 3 Jahre.

**Variante: Tilgungspause statt Sondertilgung**

Angenommen, der Fahrradladen leistet keine Sondertilgung, sondern setzt im 6. Jahr die Tilgung aus und zahlt nur die Zinsen: $Z_6 = 72\,950{,}29 \cdot 0{,}04 \approx 2\,918{,}01$ €. Die Restschuld bleibt bei $72\,950{,}29$ €.

- *Laufzeit fest:* Für die verbleibenden 9 Jahre gilt $A' = \frac{72\,950{,}29 \cdot 1{,}04^9 \cdot 0{,}04}{1{,}04^9 - 1} \approx 9\,811{,}30$ € – höher als zuvor, weil ein Tilgungsjahr fehlt.
- *Annuität fest:* $T_1' = 8\,994{,}11 - 2\,918{,}01 = 6\,076{,}10$ €, also $1{,}04^n = \frac{8\,994{,}11}{6\,076{,}10} \approx 1{,}4802$ und $n = \frac{\ln 1{,}4802}{\ln 1{,}04} \approx 10$. Nach der Pause dauert es genau die ursprünglich noch ausstehenden 10 Jahre – die Gesamtlaufzeit verlängert sich um das Pausenjahr auf 16 Jahre.

In beiden Situationen ist das Vorgehen gleich: aktuelle Restschuld als neues $K_0$ nehmen, dann entweder mit fester Restlaufzeit die Annuität oder mit fester Annuität die Laufzeit neu bestimmen.
