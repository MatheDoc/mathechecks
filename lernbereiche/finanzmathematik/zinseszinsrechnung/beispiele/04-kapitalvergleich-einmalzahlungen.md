---
layout: null
permalink: /lernbereiche/finanzmathematik/zinseszinsrechnung/beispiele/04-kapitalvergleich-einmalzahlungen.html
---
Eine Fahrschule verkauft einen Kleinbus. Drei Interessenten machen folgende Angebote:

- Angebot A: $50\,000$ € sofort.
- Angebot B: $20\,000$ € sofort und $35\,000$ € in 4 Jahren.
- Angebot C: $60\,000$ € in 3 Jahren.

Für welches Angebot sollte sich die Fahrschule entscheiden, wenn ein Zinssatz von $4\,\%$ zugrunde gelegt wird?

**Grundidee**

Zahlungen zu verschiedenen Zeitpunkten sind nicht direkt vergleichbar. Deshalb wird jede Zahlung auf den heutigen Zeitpunkt abgezinst (Barwert): $K_0 = \frac{K_n}{q^n}$ mit $q = 1{,}04$.

**Barwert Angebot A**

Die Zahlung erfolgt sofort, der Barwert ist der Betrag selbst: $B_A = 50\,000$ €.

**Barwert Angebot B**

$$B_B = 20\,000 + \frac{35\,000}{1{,}04^4} \approx 20\,000 + 29\,918{,}15 = 49\,918{,}15\,\text{€}$$

**Barwert Angebot C**

$$B_C = \frac{60\,000}{1{,}04^3} \approx 53\,339{,}78\,\text{€}$$

**Entscheidung**

Angebot C hat mit rund $53\,339{,}78$ € den höchsten Barwert. Als Empfängerin der Zahlungen sollte sich die Fahrschule für Angebot C entscheiden. Angebot B ist trotz der höheren Summe ($55\,000$ €) sogar geringfügig schlechter als Angebot A, weil der Großteil erst in 4 Jahren gezahlt wird.

Hinweis: Wäre die Fahrschule Zahlerin (z. B. beim Kauf), würde sie das Angebot mit dem niedrigsten Barwert wählen.
