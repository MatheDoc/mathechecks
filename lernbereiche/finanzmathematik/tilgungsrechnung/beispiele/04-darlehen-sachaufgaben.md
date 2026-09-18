---
layout: null
permalink: /lernbereiche/finanzmathematik/tilgungsrechnung/beispiele/04-darlehen-sachaufgaben.html
---
Ein Cateringbetrieb plant eine Investition. Die Angaben in den Teilaufgaben sind unabhängig voneinander.

a) Der Betrieb nimmt ein Darlehen über $80\,000$ € zu $4\,\%$ auf, das in 10 Jahren durch gleich hohe Jahresraten getilgt werden soll. Wie hoch ist die jährliche Rate?

b) Der Betrieb nimmt ein Darlehen über $120\,000$ € zu $3\,\%$ auf und zahlt jährlich eine Annuität von $10\,000$ €. Nach wie vielen Jahren ist das Darlehen getilgt?

**Schritt 1: Gegeben und gesucht klären**

| Teilaufgabe | $K_0$ | $p$ | $n$ | $A$ | Formel |
| a) | $80\,000$ € | $4\,\%$ | $10$ | gesucht | Annuitätenformel |
| b) | $120\,000$ € | $3\,\%$ | gesucht | $10\,000$ € | $A = T_1 \cdot q^n$ |

„Gleich hohe Jahresraten“ ist das Signalwort für die Annuität; „nach wie vielen Jahren getilgt“ fragt nach der Laufzeit.

**Lösung zu a): Annuität**

$$A = \frac{80\,000 \cdot 1{,}04^{10} \cdot 0{,}04}{1{,}04^{10} - 1} = \frac{80\,000 \cdot 1{,}4802 \cdot 0{,}04}{0{,}4802} \approx 9\,863{,}28\,\text{€}$$

Der Betrieb zahlt jährlich rund $9\,863{,}28$ €.

**Lösung zu b): Laufzeit**

$$\begin{aligned}
T_1 &= 10\,000 - 120\,000 \cdot 0{,}03 = 10\,000 - 3\,600 = 6\,400\,\text{€} \\
10\,000 &= 6\,400 \cdot 1{,}03^n \\
1{,}03^n &= 1{,}5625 \\
n &= \frac{\ln 1{,}5625}{\ln 1{,}03} \approx 15{,}10
\end{aligned}$$

Das Darlehen ist nach etwa $15{,}1$ Jahren getilgt: 15 volle Annuitäten und eine kleine Restzahlung im 16. Jahr.

Kontrolle: Die Annuität muss größer sein als die Zinsen des ersten Jahres ($3\,600$ €), sonst würde die Schuld nie sinken.
