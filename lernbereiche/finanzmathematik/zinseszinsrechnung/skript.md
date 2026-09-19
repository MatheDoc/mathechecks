---
layout: module
title: "Zinseszinsrechnung erklärt – Zinseszinsformel, Zinssatzwechsel und Kapitalvergleich"
description: "Zinseszinsrechnung Schritt für Schritt: Zinsfaktor bilden, Zinseszinsformel nach jeder Größe umformen, Sachaufgaben lösen, Zinssatzwechsel berechnen und Angebote über Barwerte vergleichen."
page_context: Lernbereich
nav: dashboard
body_class: page-module
module_key: skript
published: true
lernbereich: zinseszinsrechnung
gebiet: finanzmathematik
permalink: /lernbereiche/finanzmathematik/zinseszinsrechnung/skript.html
---

# Zinseszinsrechnung: Kapital wächst mit Zinsen auf Zinsen

## Einführung

Lena bekommt von ihrem Opa 3 000 € geschenkt und legt das Geld fest zu 3 % pro Jahr an. Am Ende des ersten Jahres schreibt die Bank Zinsen gut: 3 % von 3 000 € sind 90 €, das Guthaben beträgt nun 3 090 €. Im zweiten Jahr werden nicht mehr nur die 3 000 €, sondern die vollen 3 090 € verzinst – die Zinsen des ersten Jahres bringen selbst Zinsen. Man spricht von **Zinseszins**.

In diesem Lernbereich wird ausschließlich jährlich verzinst. Bezeichnungen:

- $K_0$: Anfangskapital (Kapital zum Zeitpunkt $0$), hier $3\,000$ €
- $K_n$: Kapital nach $n$ Jahren
- $p$: Zinssatz in Prozent pro Jahr, hier $3\,\%$
- $q = 1 + \frac{p}{100}$: Zinsfaktor, hier $1{,}03$
- $n$: Laufzeit in Jahren

Mit dem Zinsfaktor lässt sich ein Jahr Verzinsung als eine einzige Multiplikation schreiben: $3\,000 \cdot 1{,}03 = 3\,090$. Das zweite Jahr ist wieder eine Multiplikation mit $1{,}03$, also $3\,000 \cdot 1{,}03 \cdot 1{,}03 = 3\,000 \cdot 1{,}03^2 \approx 3\,182{,}70$.

## Die Zinseszinsformel

Nach $n$ Jahren wurde $n$-mal mit $q$ multipliziert:

$$
K_n = K_0 \cdot q^n
$$

Lenas Geld soll in sechs Jahren ein Auslandsjahr mitfinanzieren. Nach sechs Jahren sind es

$$
K_6 = 3\,000 \cdot 1{,}03^6 \approx 3\,000 \cdot 1{,}1941 \approx 3\,582{,}16\,\text{€}.
$$

Die Formel enthält vier Größen. Je nachdem, welche gesucht ist, wird sie nicht allgemein umgestellt; stattdessen werden alle bekannten Werte eingesetzt und die verbleibende Unbekannte wird durch Umformen bestimmt:

- $K_n$ gesucht: einsetzen und ausrechnen (wie eben).
- $K_0$ gesucht: durch $q^n$ teilen. Wollte Lena in sechs Jahren genau 4 000 € haben, müsste sie heute $K_0 = \frac{4\,000}{1{,}03^6} \approx 3\,349{,}94$ € anlegen.
- $n$ gesucht: nach $q^n$ auflösen, logarithmieren. Wann erreichen die 3 000 € die Marke von 4 000 €? Aus $1{,}03^n = \frac{4\,000}{3\,000}$ folgt $n = \frac{\ln(4\,000/3\,000)}{\ln 1{,}03} \approx 9{,}73$ – erst im zehnten Jahr.
- $p$ gesucht: nach $q^n$ auflösen, $n$-te Wurzel ziehen, $p = (q - 1) \cdot 100$. Welcher Zinssatz brächte die 3 000 € in sechs Jahren auf 4 000 €? $q = \sqrt[6]{4\,000/3\,000} \approx 1{,}0491$, also etwa $4{,}91\,\%$.

Zwischenwerte wie $q^n$ werden mit mindestens vier Nachkommastellen weitergerechnet, sonst wird das Ergebnis bei großen Beträgen ungenau.

{% include check-anker.html nummer="1" %}

## Sachaufgaben zur Zinseszinsrechnung

In Textaufgaben steht die gesuchte Größe nicht dabei. Deshalb ist zunächst zu klären, welche Werte gegeben sind und welche Größe gesucht ist – erst danach wird die Formel eingesetzt. Signalwörter helfen: „über welchen Betrag verfügen“ → $K_n$, „heute anlegen“ → $K_0$, „nach wie vielen Jahren“ → $n$, „mit welchem Zinssatz“ → $p$.

{% include check-anker.html nummer="2" %}

## Zinssatzwechsel

Lenas Bank bietet eine Alternative an: in den ersten drei Jahren 2 %, danach 3,5 %. Dann wird das Kapital phasenweise verzinst – das Endkapital der ersten Phase ist das Anfangskapital der zweiten:

$$
K_3 = 3\,000 \cdot 1{,}02^3 \approx 3\,183{,}62\,\text{€}, \qquad K_6 = K_3 \cdot 1{,}035^3 \approx 3\,529{,}74\,\text{€}.
$$

Allgemein werden die Zinsfaktoren aller Phasen mit ihren Laufzeiten verkettet:

$$
K_n = K_0 \cdot q_1^{n_1} \cdot q_2^{n_2} \cdot q_3^{n_3}
$$

Das Alternativangebot bringt weniger als die durchgehenden 3 % (3 582,16 €). Ist eine Größe unbekannt, werden alle bekannten Faktoren eingesetzt und anschließend nach dem offenen Faktor aufgelöst – Wurzel für ein $q$, Logarithmus für ein $n$.

{% include check-anker.html nummer="3" %}

## Kapitalvergleich

Lenas Tante möchte ebenfalls etwas beisteuern und stellt drei Varianten zur Wahl: 3 000 € sofort, oder 1 500 € sofort und 1 900 € in vier Jahren, oder 3 600 € in sechs Jahren. Welches Angebot ist am meisten wert?

Zahlungen zu unterschiedlichen Zeitpunkten lassen sich nur vergleichen, wenn sie auf denselben Zeitpunkt bezogen werden. Üblich ist der **Barwert**, also der Wert zum Zeitpunkt $0$:

$$
K_0 = \frac{K_n}{q^n}
$$

Mit $q = 1{,}03$ ergeben sich die Barwerte

$$
B_1 = 3\,000\,\text{€}, \qquad
B_2 = 1\,500 + \frac{1\,900}{1{,}03^4} \approx 3\,188{,}13\,\text{€}, \qquad
B_3 = \frac{3\,600}{1{,}03^6} \approx 3\,014{,}94\,\text{€}.
$$

Für jedes Angebot werden also die Barwerte aller Zahlungen addiert. Die Empfängerin wählt das Angebot mit dem höchsten Barwert – hier das zweite, obwohl das dritte die größte Summe verspricht. Ein Zahler würde umgekehrt den niedrigsten Barwert wählen.

{% include check-anker.html nummer="4" %}
