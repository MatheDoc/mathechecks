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

## Sparplan fürs erste Auto

Für dein erstes Auto legst du fünf Jahre lang jedes Jahr 1 200 € zu 2,5 % zurück. Deine Tante bietet dir stattdessen an, dir heute einmalig 5 600 € zu geben. Welches Angebot ist mehr wert – und macht es einen Unterschied, ob du am Jahresanfang oder am Jahresende einzahlst?

## Einführung

Eine **Rente** ist in der Finanzmathematik eine Folge gleich hoher Zahlungen $r$ in gleichen Zeitabständen. Hier wird ausschließlich mit jährlichen Zahlungen und jährlicher Verzinsung gerechnet.

- **Nachschüssig:** Die Zahlung erfolgt am Ende jedes Jahres.
- **Vorschüssig:** Die Zahlung erfolgt am Anfang jedes Jahres. Jede Rate wird dadurch ein Jahr länger verzinst.

Der **Rentenendwert** ist der Wert aller Raten am Ende der Laufzeit, der **Rentenbarwert** ihr Wert zu Beginn. Vorschüssige Größen werden mit einem Querstrich gekennzeichnet.

## Rentenendwert

Wie viel ist eine Rente am Ende der Laufzeit wert? Bei einer nachschüssigen Rente wird die erste Rate am Ende des ersten Jahres gezahlt und danach noch $n-1$ Jahre verzinst, die zweite Rate $n-2$ Jahre, … , die letzte Rate gar nicht mehr. Jede Rate wird also einzeln mit der Zinseszinsformel aufgezinst:

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

Bei einer **vorschüssigen** Rente wird jede Rate am Jahresanfang gezahlt und damit genau ein Jahr länger verzinst als im nachschüssigen Fall. Der gesamte Endwert ist deshalb um den Faktor $q$ größer:

$$
\overline{R}_n = \frac{r \cdot q \cdot (q^n - 1)}{q - 1}
$$

Beim Rechnen werden die bekannten Werte eingesetzt und anschließend nach der verbleibenden Größe aufgelöst – nach $r$ durch Division, nach $n$ über $q^n$ und den Logarithmus. Eine Umformung nach $q$ wird nicht behandelt.

{% include check-anker.html nummer="1" %}

## Rentenbarwert

Der Rentenbarwert beantwortet die umgekehrte Frage: Welcher Betrag müsste heute angelegt werden, damit daraus alle $n$ Raten gezahlt werden können? Dazu muss der Rentenendwert nur auf den Zeitpunkt $0$ abgezinst werden – genau wie eine Einmalzahlung mit der Zinseszinsformel:

$$
R_0 = \frac{R_n}{q^n} = \frac{r \cdot (q^n - 1)}{q^n \cdot (q - 1)}
$$

Für die vorschüssige Rente wird entsprechend $\overline{R}_n$ abgezinst:

$$
\overline{R}_0 = \frac{\overline{R}_n}{q^n} = \frac{r \cdot q \cdot (q^n - 1)}{q^n \cdot (q - 1)}
$$

Der Barwert unterscheidet sich vom Endwert also nur durch den zusätzlichen Faktor $q^n$ im Nenner. Ist $n$ gesucht, wird die Gleichung zunächst mit $q^n$ multipliziert, damit $q^n$ nur noch an einer Stelle steht.

{% include check-anker.html nummer="2" %}

## Die vier Rentenformeln im Überblick

| | Endwert (Ende der Laufzeit) | Barwert (heute) |
|---|---|---|
| **nachschüssig** (Jahresende) | $R_n = \dfrac{r \cdot (q^n - 1)}{q - 1}$ | $R_0 = \dfrac{r \cdot (q^n - 1)}{q^n \cdot (q - 1)}$ |
| **vorschüssig** (Jahresanfang) | $\overline{R}_n = \dfrac{r \cdot q \cdot (q^n - 1)}{q - 1}$ | $\overline{R}_0 = \dfrac{r \cdot q \cdot (q^n - 1)}{q^n \cdot (q - 1)}$ |

In Sachaufgaben entscheidet der Text, welche Formel gebraucht wird. Zwei Fragen sind zu klären: Wann wird gezahlt (Jahresanfang → vorschüssig, Jahresende → nachschüssig)? Und zu welchem Zeitpunkt soll bewertet werden (Guthaben am Ende → Endwert, heute nötiger Betrag → Barwert)?

{% include check-anker.html nummer="3" %}

## Kapitalauf- und -abbau

Wird zusätzlich zu den regelmäßigen Zahlungen ein Startkapital $K_0$ angelegt, kombiniert man Zinseszins- und Rentenendwertformel:

$$
E_n = K_0 \cdot q^n \pm R_n
\qquad\text{bzw.}\qquad
\overline{E}_n = K_0 \cdot q^n \pm \overline{R}_n
$$

Einzahlungen erhöhen das Kapital ($+$, Kapitalaufbau), Entnahmen verringern es ($-$, Kapitalabbau). Ist $n$ gesucht, wird $q^n$ ausgeklammert und anschließend logarithmiert.

{% include check-anker.html nummer="4" %}

## Sachaufgaben zur Rentenrechnung

In Textaufgaben sind drei Fragen zu klären: Ist die Zahlung vor- oder nachschüssig? Geht es um End- oder Barwert? Welche Größe ist gesucht?

{% include check-anker.html nummer="5" %}

## Sachaufgaben zum Kapitalauf- und -abbau

Typische Fragen sind „Wie hoch ist das Guthaben nach $n$ Jahren?" oder „Wie lange reicht das Kapital bei jährlicher Entnahme?" (Kapitalabbau mit $E_n = 0$).

{% include check-anker.html nummer="6" %}

## Kapitalvergleich

Angebote aus Einmalzahlungen und Renten werden verglichen, indem alle Zahlungen auf denselben Zeitpunkt – meist den Barwert – bezogen werden. Einmalzahlungen werden mit $q^n$ abgezinst, Renten über den Rentenbarwert bewertet.

{% include check-anker.html nummer="7" %}

## Zurück zum Sparplan

Der Rentenendwert der fünf Raten ergibt sich nachschüssig als $R_5 = \frac{1\,200 \cdot (1{,}025^5 - 1)}{0{,}025}$ und vorschüssig als $\overline{R}_5 = R_5 \cdot 1{,}025$. Der Einmalbetrag der Tante wächst auf $5\,600 \cdot 1{,}025^5$. Der Vergleich der drei Endwerte – oder alternativ der Barwerte – zeigt, welches Angebot mehr wert ist.
