---
layout: module
title: "Tilgungsrechnung erklärt – Tilgungsplan, Annuitätenformel und Restschuld"
description: "Annuitätentilgung Schritt für Schritt: Tilgungsplan aufstellen, Annuität, Laufzeit und Restschuld berechnen, lückenhafte Tilgungspläne vervollständigen, Zinssatzwechsel, Sondertilgung und Tilgungspause."
page_context: Lernbereich
nav: dashboard
body_class: page-module
module_key: skript
published: true
lernbereich: tilgungsrechnung
gebiet: finanzmathematik
permalink: /lernbereiche/finanzmathematik/tilgungsrechnung/skript.html
---

# Tilgungsrechnung: ein Darlehen planmäßig zurückzahlen

## Gründungsdarlehen für ein eigenes Café

Für dein Café nimmst du 60 000 € zu 5 % auf und sollst jedes Jahr denselben Betrag zurückzahlen. Wie hoch ist diese jährliche Rate, wenn das Darlehen nach zehn Jahren getilgt sein soll – und wie viel Schulden hast du nach fünf Jahren noch?

## Einführung

Bei der **Annuitätentilgung** zahlt der Kreditnehmer jedes Jahr denselben Betrag, die **Annuität** $A$. Sie setzt sich aus Zinsen $Z_k$ und Tilgung $T_k$ zusammen: $A = Z_k + T_k$. Da die Restschuld sinkt, werden die Zinsen von Jahr zu Jahr kleiner und der Tilgungsanteil entsprechend größer.

Bezeichnungen:

- $K_0$: Darlehenssumme
- $RK_k$: Restschuld nach $k$ Jahren
- $Z_k$, $T_k$: Zinsen und Tilgung im Jahr $k$
- $A$: Annuität
- $q = 1 + \frac{p}{100}$: Zinsfaktor

## Der Tilgungsplan

| Jahr | Restschuld (Anfang) | Zinsen | Tilgung | Annuität | Restschuld (Ende) |
|---|---|---|---|---|---|
| $k$ | $RK_{k-1}$ | $Z_k = RK_{k-1} \cdot \frac{p}{100}$ | $T_k = A - Z_k$ | $A$ | $RK_k = RK_{k-1} - T_k$ |

Jede Zelle wird auf zwei Nachkommastellen gerundet, mit den gerundeten Werten wird weitergerechnet. In der letzten Zeile ist die Tilgung gleich der verbliebenen Restschuld; die letzte Annuität weicht dadurch meist geringfügig von $A$ ab (Rundungsdifferenz).

Im folgenden Widget kannst du Darlehenssumme, Zinssatz und Laufzeit verändern. Der Tilgungsplan wird zeilenweise berechnet; im Diagramm siehst du, wie der Zinsanteil der Annuität von Jahr zu Jahr sinkt und der Tilgungsanteil wächst.

{% include widgets/widget-tilgungsplan.html %}

{% include check-anker.html nummer="1" %}

## Annuität und Laufzeit

$$
A = \frac{K_0 \cdot q^n \cdot (q - 1)}{q^n - 1}
\qquad
A = T_1 \cdot q^n
$$

Mit der ersten Formel wird die Annuität aus Darlehenssumme, Zinssatz und Laufzeit berechnet – oder umgekehrt die Darlehenssumme aus einer vorgegebenen Annuität. Die zweite Formel liefert über $q^n = \frac{A}{T_1}$ und den Logarithmus die Laufzeit.

{% include check-anker.html nummer="2" %}

## Restschuld

$$
RK_k = K_0 \cdot q^k - \frac{A \cdot (q^k - 1)}{q - 1}
\qquad
RK_k = K_0 - \frac{T_1 \cdot (q^k - 1)}{q - 1}
$$

Aus der Restschuld nach $k$ Jahren ergeben sich Zinsen und Tilgung des Folgejahres. Die Gesamtzinsen über die Laufzeit sind $n \cdot A - K_0$.

{% include check-anker.html nummer="3" %}

## Sachaufgaben zu Annuitätendarlehen

In Textaufgaben ist zu klären, welche Größen gegeben sind und ob Annuität, Darlehenssumme, Laufzeit oder Restschuld gesucht ist.

{% include check-anker.html nummer="4" %}

## Tilgungsplan vervollständigen

Sind nur einzelne Werte eines Tilgungsplans bekannt, werden die Zusammenhänge $A = Z_k + T_k$, $Z_k = RK_{k-1} \cdot \frac{p}{100}$ und $RK_k = RK_{k-1} - T_k$ genutzt – auch rückwärts, etwa $RK_{k-1} = RK_k + T_k$.

{% include check-anker.html nummer="5" %}

## Zinssatzwechsel

Ändert sich der Zinssatz, wird die Restschuld zum Zeitpunkt des Wechsels als neue Darlehenssumme und die Restlaufzeit als neue Laufzeit in die Annuitätenformel eingesetzt.

{% include check-anker.html nummer="6" %}

## Sondertilgung und Tilgungspause

Eine **Sondertilgung** verringert die Restschuld zusätzlich; anschließend wird entweder die Annuität (bei fester Restlaufzeit) oder die Laufzeit (bei fester Annuität) neu bestimmt. Bei einer **Tilgungspause** werden nur die Zinsen gezahlt, die Restschuld bleibt unverändert.

{% include check-anker.html nummer="7" %}

## Zurück zum Gründungsdarlehen

Die Annuität ergibt sich aus $A = \frac{60\,000 \cdot 1{,}05^{10} \cdot 0{,}05}{1{,}05^{10} - 1}$. Mit ihr lassen sich die ersten Zeilen des Tilgungsplans aufstellen, und die Restschuldformel liefert $RK_5$ nach fünf Jahren.
