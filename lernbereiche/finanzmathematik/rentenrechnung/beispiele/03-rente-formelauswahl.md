---
layout: null
permalink: /lernbereiche/finanzmathematik/rentenrechnung/beispiele/03-rente-formelauswahl.html
---
Entscheiden Sie für jede Situation, ob eine vor- oder nachschüssige Rente vorliegt, ob End- oder Barwert gesucht ist, und wählen Sie die passende Formel.

a) Ein Verein zahlt 10 Jahre lang jeweils am Jahresende $1\,500$ € auf ein Konto ein. Gesucht ist das Guthaben unmittelbar nach der letzten Einzahlung.

b) Eine Studentin soll 5 Jahre lang jeweils zu Jahresbeginn $6\,000$ € erhalten, erstmals sofort. Gesucht ist der Betrag, der dafür heute angelegt werden muss.

c) Ein Handwerksbetrieb legt 8 Jahre lang jeweils am Jahresanfang $4\,000$ € zurück. Gesucht ist das Guthaben am Ende des 8. Jahres.
d) Ein Ehepaar möchte 12 Jahre lang jeweils zum Jahresende $9\,000$ € entnehmen. Gesucht ist der Betrag, der dafür heute angelegt werden muss.
**Schritt 1: Zahlungszeitpunkt (vor- oder nachschüssig)**

Am Zeitstrahl liegt jedes Jahr zwischen zwei Zeitpunkten. Fällt die Rate an den Anfang eines Jahres, ist die Rente vorschüssig; fällt sie an das Ende, ist sie nachschüssig.

- a) „am Jahresende“ → nachschüssig
- b) „zu Jahresbeginn, erstmals sofort“ → vorschüssig
- c) „am Jahresanfang“ → vorschüssig
- d) „zum Jahresende“ → nachschüssig

**Schritt 2: Bewertungszeitpunkt (Endwert oder Barwert)**

- a) Guthaben nach der letzten Einzahlung → Wert am Ende der Laufzeit → Endwert
- b) Betrag, der heute angelegt werden muss → Wert zu Beginn → Barwert
- c) Guthaben am Ende des 8. Jahres → Endwert
- d) Betrag, der heute angelegt werden muss → Barwert

**Schritt 3: Formel zuordnen**

Die vier Situationen decken genau die vier Rentenformeln ab:

$$\begin{aligned}
\text{a)}\quad R_n &= \frac{r \cdot (q^n - 1)}{q - 1} &&\text{(nachschüssiger Rentenendwert)} \\
\text{b)}\quad \overline{R}_0 &= \frac{r \cdot q \cdot (q^n - 1)}{q^n \cdot (q - 1)} &&\text{(vorschüssiger Rentenbarwert)} \\
\text{c)}\quad \overline{R}_n &= \frac{r \cdot q \cdot (q^n - 1)}{q - 1} &&\text{(vorschüssiger Rentenendwert)} \\
\text{d)}\quad R_0 &= \frac{r \cdot (q^n - 1)}{q^n \cdot (q - 1)} &&\text{(nachschüssiger Rentenbarwert)}
\end{aligned}$$

Übersicht:

| | Endwert | Barwert |
| nachschüssig | $R_n$ (a) | $R_0$ (d) |
| vorschüssig | $\overline{R}_n$ (c) | $\overline{R}_0$ (b) |

Merkhilfe: Der Querstrich steht für vorschüssig – jede Rate wird ein Jahr länger verzinst, deshalb der zusätzliche Faktor $q$. Der Barwert entsteht aus dem Endwert durch Abzinsen mit $q^n$.
