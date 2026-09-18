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

## Geldgeschenk fürs Auslandsjahr

Zur Konfirmation bekommst du 3 000 € geschenkt und legst sie fest zu 3 % pro Jahr an. In sechs Jahren soll das Geld ein Auslandsjahr mitfinanzieren – reicht es dann für 4 000 €? Und wenn nicht: Wie lange müsstest du warten oder welchen Zinssatz bräuchtest du?

## Einführung

Wird ein Kapital verzinst und bleiben die Zinsen auf dem Konto, so werden im Folgejahr auch die Zinsen mitverzinst. Man spricht von **Zinseszins**. In diesem Lernbereich wird ausschließlich jährlich verzinst.

Bezeichnungen:

- $K_0$: Anfangskapital (Kapital zum Zeitpunkt $0$)
- $K_n$: Kapital nach $n$ Jahren
- $p$: Zinssatz in Prozent pro Jahr
- $q = 1 + \frac{p}{100}$: Zinsfaktor
- $n$: Laufzeit in Jahren

## Die Zinseszinsformel

$$
K_n = K_0 \cdot q^n
$$

Die Formel wird nicht allgemein nach der gesuchten Größe aufgelöst. Stattdessen werden alle bekannten Werte eingesetzt; die verbleibende Unbekannte wird anschließend durch Umformen bestimmt.

- $K_n$ gesucht: einsetzen und ausrechnen.
- $K_0$ gesucht: durch $q^n$ teilen.
- $p$ gesucht: nach $q^n$ auflösen, $n$-te Wurzel ziehen, $p = (q - 1) \cdot 100$.
- $n$ gesucht: nach $q^n$ auflösen, logarithmieren: $n = \frac{\ln(q^n)}{\ln q}$.

Zwischenwerte wie $q^n$ werden mit mindestens vier Nachkommastellen weitergerechnet.

{% include check-anker.html nummer="1" %}

## Sachaufgaben zur Zinseszinsrechnung

In Textaufgaben ist zunächst zu klären, welche Werte gegeben sind und welche Größe gesucht ist. Erst danach wird die Formel eingesetzt.

{% include check-anker.html nummer="2" %}

## Zinssatzwechsel

Ändert sich der Zinssatz während der Laufzeit, wird das Kapital phasenweise verzinst:

$$
K_n = K_0 \cdot q_1^{n_1} \cdot q_2^{n_2} \cdot q_3^{n_3}
$$

Ist eine Größe unbekannt, werden alle bekannten Faktoren eingesetzt und anschließend nach dem offenen Faktor aufgelöst.

{% include check-anker.html nummer="3" %}

## Kapitalvergleich

Zahlungen zu unterschiedlichen Zeitpunkten lassen sich nur vergleichen, wenn sie auf denselben Zeitpunkt bezogen werden. Üblich ist der **Barwert**, also der Wert zum Zeitpunkt $0$:

$$
K_0 = \frac{K_n}{q^n}
$$

Für jedes Angebot werden die Barwerte aller Zahlungen addiert. Der Empfänger wählt das Angebot mit dem höchsten, der Zahler das mit dem niedrigsten Barwert.

{% include check-anker.html nummer="4" %}

## Zurück zum Geldgeschenk

Mit $K_6 = 3\,000 \cdot 1{,}03^6$ ergibt sich das Endkapital nach sechs Jahren. Für das Ziel von 4 000 € liefert $1{,}03^n = \frac{4\,000}{3\,000}$ mit dem Logarithmus die nötige Laufzeit, und $q = \sqrt[6]{\frac{4\,000}{3\,000}}$ den Zinssatz, der das Ziel in sechs Jahren erreicht.
