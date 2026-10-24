---
layout: null
permalink: /lernbereiche/analysis/produktlebenszyklus/beispiele/05-integrale-gemischt.html
---
Der monatliche Absatz eines Produkts wird beschrieben durch

$$
a(t)=(-0{,}1t^3+2t^2)\cdot e^{-0{,}2t} \qquad (t \text{ in Monaten},\ a(t) \text{ in ME/Monat}).
$$

Wegen $-0{,}1t^3+2t^2=t^2(-0{,}1t+2)=0$ für $t=20$ wird das Produkt nach $20$ Monaten vom Markt genommen. Mit dem Rechner bestimmen wir:

- **Monatlicher Absatz nach 8 Monaten** (Funktionswert, kein Integral):

    $$
    a(8)\approx 15{,}51 \text{ ME/Monat}
    $$

- **Gesamtabsatz vom Ende des 3. bis zum Ende des 9. Monats:**

    $$
    \int_3^9 a(t)\,dt \approx 83{,}63 \text{ ME}
    $$

- **Durchschnittlicher monatlicher Absatz in den ersten 6 Monaten:**

    $$
    \frac{1}{6-0}\int_0^6 a(t)\,dt \approx 7{,}93 \text{ ME/Monat}
    $$

- **Gesamtabsatz während des gesamten Produktlebenszyklus:**

    $$
    \int_0^{20} a(t)\,dt \approx 168{,}50 \text{ ME}
    $$

- **Zeitpunkt, zu dem der Gesamtabsatz seit Markteinführung 100 ME erreicht:** Gesucht ist die obere Grenze $z$ mit

    $$
    \int_0^{z} a(t)\,dt = 100 \quad\Rightarrow\quad z\approx 9{,}42
    $$

    Nach ca. $9{,}42$ Monaten sind insgesamt $100$ ME abgesetzt.

- **Wird ein Gesamtabsatz von 200 ME erreicht?** Nein. Nach dem Marktaustritt kommt kein Absatz mehr hinzu, insgesamt werden nur ca. $168{,}50$ ME abgesetzt.
