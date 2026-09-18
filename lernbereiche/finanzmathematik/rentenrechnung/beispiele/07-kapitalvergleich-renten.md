---
layout: null
permalink: /lernbereiche/finanzmathematik/rentenrechnung/beispiele/07-kapitalvergleich-renten.html
---
Eine Landwirtin verkauft eine gebrauchte Erntemaschine. Drei Interessenten machen folgende Angebote:

- Angebot A: $30\,000$ € sofort.
- Angebot B: $12\,000$ € sofort und $22\,000$ € in 5 Jahren.
- Angebot C: 8 Jahreszahlungen von je $4\,500$ €, die erste Zahlung in einem Jahr.

Für welches Angebot sollte sich die Landwirtin bei einem Zinssatz von $3\,\%$ entscheiden?

**Grundidee**

Alle Zahlungen werden auf den heutigen Zeitpunkt bezogen (Barwert). Einmalzahlungen werden mit $q^n$ abgezinst, die Rente über den Rentenbarwert bewertet.

**Barwert Angebot A**

$$B_A = 30\,000\,\text{€}$$

**Barwert Angebot B**

$$B_B = 12\,000 + \frac{22\,000}{1{,}03^5} \approx 12\,000 + 18\,977{,}39 = 30\,977{,}39\,\text{€}$$

**Barwert Angebot C**

Die erste Zahlung erfolgt in einem Jahr, also am Ende des ersten Jahres: nachschüssige Rente mit $r = 4\,500$ €, $n = 8$.

$$B_C = R_0 = \frac{4\,500 \cdot (1{,}03^8 - 1)}{1{,}03^8 \cdot 0{,}03} \approx 4\,500 \cdot 7{,}0197 \approx 31\,588{,}61\,\text{€}$$

**Entscheidung**

Angebot C hat mit rund $31\,588{,}61$ € den höchsten Barwert. Die Landwirtin sollte Angebot C annehmen.

Hinweis: Beginnt eine nachschüssige Rente erst später (z. B. erste Zahlung in 3 Jahren statt in einem Jahr), wird der Rentenbarwert zusätzlich mit $q^k$ abgezinst, wobei $k$ die Verschiebung in Jahren ist (hier $k = 2$). Bei sofort beginnenden Zahlungen ist der vorschüssige Rentenbarwert $\overline{R}_0$ zu verwenden.
