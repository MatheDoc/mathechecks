---
layout: module
title: "Rentenrechnung erklärt – vor- und nachschüssige Renten, Endwert, Barwert und Kapitalauf- und -abbau"
description: "Rentenrechnung Schritt für Schritt: Zahlungszeitpunkte am Zeitstrahl, die vier Rentenformeln, Rate und Laufzeit bestimmen, Kapitalauf- und -abbau als Kombination mit der Zinseszinsformel, Kapitalvergleich über Barwerte."
page_context: Lernbereich
nav: dashboard
body_class: page-module
module_key: skript
published: true
lernbereich: rentenrechnung
gebiet: finanzmathematik
permalink: /lernbereiche/finanzmathematik/rentenrechnung/skript.html
---

# Rentenrechnung: regelmäßige Zahlungen bewerten

## Einführung

Jonas spart für sein erstes Auto: Fünf Jahre lang legt er jedes Jahr 1 200 € auf ein Konto, das mit 2,5 % verzinst wird. Anders als in der Zinseszinsrechnung gibt es hier nicht eine Einmalzahlung, sondern mehrere gleich hohe Zahlungen in gleichen Zeitabständen – in der Finanzmathematik heißt eine solche Zahlungsfolge **Rente**, die einzelne Zahlung **Rate** $r$. Hier wird ausschließlich mit jährlichen Zahlungen und jährlicher Verzinsung gerechnet.

Zwei Dinge muss Jonas mit seiner Bank klären:

- **Wann wird gezahlt?** Zahlt er jeweils am Ende eines Jahres, heißt die Rente **nachschüssig**. Zahlt er jeweils am Anfang eines Jahres, heißt sie **vorschüssig** – jede Rate wird dann ein Jahr länger verzinst.
- **Zu welchem Zeitpunkt wird bewertet?** Der **Rentenendwert** ist der Wert aller Raten am Ende der Laufzeit (Jonas' Guthaben nach fünf Jahren). Der **Rentenbarwert** ist ihr Wert zu Beginn (der Betrag, der heute einmalig angelegt dieselben fünf Raten ermöglichen würde).

Vorschüssige Größen werden mit einem Querstrich gekennzeichnet: $\overline{R}_n$, $\overline{R}_0$.

## Rentenendwert

Wie viel Guthaben hat Jonas nach fünf Jahren, wenn er nachschüssig zahlt? Die erste Rate wird am Ende des ersten Jahres eingezahlt und danach noch vier Jahre verzinst, die zweite drei Jahre, … , die fünfte gar nicht mehr. Jede Rate wird also einzeln mit der Zinseszinsformel aufgezinst:

$$
R_5 = 1\,200 \cdot 1{,}025^4 + 1\,200 \cdot 1{,}025^3 + 1\,200 \cdot 1{,}025^2 + 1\,200 \cdot 1{,}025 + 1\,200 \approx 6\,307{,}59\,\text{€}
$$

Bei fünf Raten geht das noch; bei 25 Raten wäre es mühsam. Allgemein lautet die Summe für $n$ Raten

$$
R_n = r \cdot q^{n-1} + r \cdot q^{n-2} + \dots + r \cdot q + r
$$

Diese Summe lässt sich mit einem Trick zusammenfassen: Multipliziert man die Gleichung mit $q$, verschiebt sich jeder Summand um eine Potenz nach oben:

$$
\begin{aligned}
q \cdot R_n &= r \cdot q^{n} + r \cdot q^{n-1} + \dots + r \cdot q^2 + r \cdot q \\
R_n &= r \cdot q^{n-1} + r \cdot q^{n-2} + \dots + r \cdot q + r
\end{aligned}
$$

Zieht man die zweite Gleichung von der ersten ab, heben sich alle mittleren Summanden auf; übrig bleiben nur der größte und der kleinste:

$$
q \cdot R_n - R_n = r \cdot q^n - r
$$

Ausklammern liefert $R_n \cdot (q - 1) = r \cdot (q^n - 1)$ und damit die **nachschüssige Rentenendwertformel**:

$$
R_n = \frac{r \cdot (q^n - 1)}{q - 1}
$$

Für Jonas: $R_5 = \frac{1\,200 \cdot (1{,}025^5 - 1)}{0{,}025} \approx 6\,307{,}59$ € – dasselbe Ergebnis wie oben, aber in einem Schritt.

Zahlt Jonas **vorschüssig**, also jeweils am Jahresanfang, wird jede Rate genau ein Jahr länger verzinst als im nachschüssigen Fall. Der gesamte Endwert ist deshalb um den Faktor $q$ größer:

$$
\overline{R}_n = \frac{r \cdot q \cdot (q^n - 1)}{q - 1}
$$

Für Jonas: $\overline{R}_5 = 6\,307{,}59 \cdot 1{,}025 \approx 6\,465{,}28$ €. Die frühere Zahlung bringt ihm also rund 158 € mehr.

Beim Rechnen werden die bekannten Werte eingesetzt und anschließend nach der verbleibenden Größe aufgelöst – nach $r$ durch Division, nach $n$ über $q^n$ und den Logarithmus. Eine Umformung nach $q$ wird nicht behandelt.

{% include check-anker.html nummer="1" %}

## Rentenbarwert

Jonas' Tante macht ein Angebot: Statt dass er fünf Jahre lang spart, gibt sie ihm heute einmalig 5 600 €. Ist das mehr oder weniger wert als sein Sparplan? Um das zu vergleichen, wird gefragt, welcher Betrag heute angelegt werden müsste, damit daraus alle fünf Raten gezahlt werden könnten – das ist der **Rentenbarwert**. Dazu muss der Rentenendwert nur auf den Zeitpunkt $0$ abgezinst werden, genau wie eine Einmalzahlung mit der Zinseszinsformel:

$$
R_0 = \frac{R_n}{q^n} = \frac{r \cdot (q^n - 1)}{q^n \cdot (q - 1)}
$$

Für Jonas' nachschüssigen Sparplan: $R_0 = \frac{6\,307{,}59}{1{,}025^5} \approx 5\,574{,}99$ €. Das Angebot der Tante (5 600 €) ist also geringfügig mehr wert.

Für die vorschüssige Rente wird entsprechend $\overline{R}_n$ abgezinst:

$$
\overline{R}_0 = \frac{\overline{R}_n}{q^n} = \frac{r \cdot q \cdot (q^n - 1)}{q^n \cdot (q - 1)}
$$

Zahlt Jonas vorschüssig, ist sein Sparplan $\overline{R}_0 \approx 5\,714{,}37$ € wert – dann liegt er vor dem Angebot der Tante. Der Zahlungszeitpunkt entscheidet hier also über die Antwort.

Der Barwert unterscheidet sich vom Endwert nur durch den zusätzlichen Faktor $q^n$ im Nenner. Ist $n$ gesucht, wird die Gleichung zunächst mit $q^n$ multipliziert, damit $q^n$ nur noch an einer Stelle steht.

{% include check-anker.html nummer="2" %}

## Die vier Rentenformeln im Überblick

| | Endwert (Ende der Laufzeit) | Barwert (heute) |
|---|---|---|
| **nachschüssig** (Jahresende) | $R_n = \dfrac{r \cdot (q^n - 1)}{q - 1}$ | $R_0 = \dfrac{r \cdot (q^n - 1)}{q^n \cdot (q - 1)}$ |
| **vorschüssig** (Jahresanfang) | $\overline{R}_n = \dfrac{r \cdot q \cdot (q^n - 1)}{q - 1}$ | $\overline{R}_0 = \dfrac{r \cdot q \cdot (q^n - 1)}{q^n \cdot (q - 1)}$ |

In Sachaufgaben entscheidet der Text, welche Formel gebraucht wird. Zwei Fragen sind zu klären: Wann wird gezahlt (Jahresanfang → vorschüssig, Jahresende → nachschüssig)? Und zu welchem Zeitpunkt soll bewertet werden (Guthaben am Ende → Endwert, heute nötiger Betrag → Barwert)?

{% include check-anker.html nummer="3" %}

## Sachaufgaben zur Rentenrechnung

In Textaufgaben sind drei Fragen zu klären: Ist die Zahlung vor- oder nachschüssig? Geht es um End- oder Barwert? Welche Größe ist gesucht? Bei Jonas könnte zum Beispiel gefragt sein, wie lange er 1 200 € nachschüssig einzahlen muss, bis 10 000 € zusammen sind: Aus $10\,000 = \frac{1\,200 \cdot (1{,}025^n - 1)}{0{,}025}$ folgt $1{,}025^n \approx 1{,}2083$ und $n \approx 7{,}66$ – also erst im achten Jahr.

{% include check-anker.html nummer="4" %}

## Kapitalauf- und -abbau

Jonas hat bereits 800 € auf dem Konto, bevor er mit den Einzahlungen beginnt. Dieses Startkapital wächst fünf Jahre lang mit Zinseszins, während gleichzeitig die Raten dazukommen. Beide Anteile werden getrennt bewertet und addiert – Zinseszins- und Rentenendwertformel werden kombiniert:

$$
E_n = K_0 \cdot q^n \pm R_n
\qquad\text{bzw.}\qquad
\overline{E}_n = K_0 \cdot q^n \pm \overline{R}_n
$$

Für Jonas (nachschüssig): $E_5 = 800 \cdot 1{,}025^5 + 6\,307{,}59 \approx 905{,}13 + 6\,307{,}59 = 7\,212{,}72$ €.

Einzahlungen erhöhen das Kapital ($+$, **Kapitalaufbau**), Entnahmen verringern es ($-$, **Kapitalabbau**) – etwa wenn Jonas später aus dem angesparten Betrag jährlich einen festen Betrag für Versicherung und Wartung entnimmt. Ist $n$ gesucht, wird $q^n$ ausgeklammert und anschließend logarithmiert.

{% include check-anker.html nummer="5" %}

## Sachaufgaben zum Kapitalauf- und -abbau

Typische Fragen sind „Wie hoch ist das Guthaben nach $n$ Jahren?“ oder „Wie lange reicht das Kapital bei jährlicher Entnahme?“ (Kapitalabbau mit $E_n = 0$). Entscheidend ist, die Kombination zu erkennen: ein Startkapital *und* regelmäßige Zahlungen.

{% include check-anker.html nummer="6" %}

## Kapitalvergleich

Die Tante überlegt es sich noch einmal und stellt Jonas drei Varianten zur Wahl:

- A: 5 600 € sofort.
- B: 2 500 € sofort und 3 500 € in drei Jahren.
- C: Fünf Jahre lang jeweils am Jahresende 1 200 € (sie übernimmt also seinen Sparplan).

Angebote aus Einmalzahlungen und Renten werden verglichen, indem alle Zahlungen auf denselben Zeitpunkt bezogen werden – meist den Barwert. Einmalzahlungen werden mit $q^n$ abgezinst, Renten über den Rentenbarwert bewertet:

$$
B_A = 5\,600\,\text{€}, \qquad
B_B = 2\,500 + \frac{3\,500}{1{,}025^3} \approx 5\,750{,}10\,\text{€}, \qquad
B_C = R_0 \approx 5\,574{,}99\,\text{€}.
$$

Als Empfänger wählt Jonas das Angebot mit dem höchsten Barwert, also B – obwohl C mit insgesamt 6 000 € die größte Summe verspricht.

{% include check-anker.html nummer="7" %}
