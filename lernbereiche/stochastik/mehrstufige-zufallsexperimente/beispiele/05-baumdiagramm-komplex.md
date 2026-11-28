---
layout: null
permalink: /lernbereiche/stochastik/mehrstufige-zufallsexperimente/beispiele/05-baumdiagramm-komplex.html
---

An einer Schule wurden 800 Schülerinnen und Schüler zu ihrem Schulweg befragt. Sie kommen mit dem Bus (B), mit dem Fahrrad (F) oder zu Fuß (Z). Wer mit dem Bus oder dem Fahrrad kommt, wurde zusätzlich gefragt, ob er in der letzten Woche immer rechtzeitig (R) oder mindestens einmal verspätet (V) angekommen ist. 200 der Befragten kommen zu Fuß. Jeder Fünfte der Busfahrer ist verspätet angekommen. 8&nbsp;% aller Befragten fahren mit dem Bus und sind verspätet angekommen. Insgesamt sind 11,5&nbsp;% aller Befragten verspätet angekommen. Wie sieht das vollständig ausgefüllte Baumdiagramm aus?

**Baumdiagramm aufstellen.** Auf der ersten Stufe steht das Verkehrsmittel mit drei Ästen B, F und Z. Nur bei B und F geht es weiter mit R und V. Der Pfad Z endet nach der ersten Stufe, denn bei den Fußgängern wurde die Pünktlichkeit nicht erfasst.

**Angaben eintragen.** Jede Angabe gehört an eine bestimmte Stelle:

- „200 der Befragten kommen zu Fuß“ ist ein Anteil aller Befragten, also der Ast zu Z. Er ist zugleich das Pfadende von Z:
    $$
    \frac{200}{800}=0{,}25.
    $$
- „Jeder Fünfte der Busfahrer …“ ist ein Anteil der Busfahrer, also der Ast von B nach V: $0{,}2$.
- „8&nbsp;% aller Befragten fahren mit dem Bus und sind verspätet …“ ist ein Anteil aller Befragten, also das Pfadende von B → V: $0{,}08$.
- „Insgesamt 11,5&nbsp;% …“ betrifft zwei Pfade. Er ist die Summe der Pfadenden von B → V und F → V und steht deshalb nicht an einer einzelnen Stelle im Baum.

{% include baumdiagramm-allgemein.html baum="B[①](R[②|③] V[0,2|0,08]) F[④](R[⑤|⑥] V[⑦|⑧]) Z[0,25|0,25]" %}

**Baumdiagramm vervollständigen.**

- Welchen Wert hat ②?

    An jedem Knoten summieren sich die Wahrscheinlichkeiten zu 1:
    $$
    ② = 1-0{,}2 = 0{,}8.
    $$

- Welchen Wert hat ①?

    Die Pfadmultiplikationsregel auf den Pfad B → V angewendet ergibt
    $$
    ① \cdot 0{,}2 = 0{,}08 \Rightarrow ① = 0{,}08 : 0{,}2 = 0{,}4.
    $$

- Welche Werte haben ④ und ③?

    $$
    \begin{align*}
    ④ &= 1-0{,}4-0{,}25 = 0{,}35\\
    ③ &= 0{,}4 \cdot 0{,}8 = 0{,}32
    \end{align*}
    $$

- Welchen Wert hat ⑧?

    Der Gesamtanteil der Verspäteten ist die Summe der Pfade B → V und F → V:
    $$
    0{,}08 + ⑧ = 0{,}115 \Rightarrow ⑧ = 0{,}035.
    $$

- Welche Werte haben ⑦, ⑤ und ⑥?

    Die Pfadmultiplikationsregel auf den Pfad F → V angewendet ergibt
    $$
    \begin{align*}
    0{,}35 \cdot ⑦ &= 0{,}035 \Rightarrow ⑦ = 0{,}035 : 0{,}35 = 0{,}1\\
    ⑤ &= 1-0{,}1 = 0{,}9\\
    ⑥ &= 0{,}35 \cdot 0{,}9 = 0{,}315
    \end{align*}
    $$

Zur Kontrolle: Alle Pfadenden zusammen ergeben $0{,}32+0{,}08+0{,}315+0{,}035+0{,}25=1$.

{% include baumdiagramm-allgemein.html baum="B[0,4](R[0,8|0,32] V[0,2|0,08]) F[0,35](R[0,9|0,315] V[0,1|0,035]) Z[0,25|0,25]" %}

**Baumdiagramm auswerten.** Nun können wir Anteile im Sachzusammenhang ablesen:

- Der Anteil der Radfahrer, die verspätet angekommen sind, steht am Ast von F nach V: $0{,}1$, also 10&nbsp;%.
- Der Anteil aller Befragten, die mit dem Fahrrad kommen und immer rechtzeitig waren, ist das Pfadende von F → R: $0{,}315$.
- Der Anteil aller Befragten, die mit Bus oder Fahrrad immer rechtzeitig angekommen sind, ist eine Summe von Pfadenden:
    $$
    0{,}32 + 0{,}315 = 0{,}635.
    $$
