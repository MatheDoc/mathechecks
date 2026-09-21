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

In diesem Lernbereich wird ausschließlich jährlich verzinst. Wir verwenden folgende Bezeichnungen:

- $K_0$: Anfangskapital (Kapital zum Zeitpunkt $0$), hier $3\,000$ €
- $K_n$: Kapital nach $n$ Jahren
- $p$: Zinssatz in Prozent pro Jahr, hier $3\,\%$
- $q = 1 + \frac{p}{100}$: Zinsfaktor, hier $1{,}03$
- $n$: Laufzeit in Jahren

Mit dem Zinsfaktor lässt sich ein Jahr Verzinsung als eine einzige Multiplikation schreiben: $3\,000 \cdot 1{,}03 = 3\,090$. Das zweite Jahr ist wieder eine Multiplikation mit $1{,}03$, also $3\,000 \cdot 1{,}03 \cdot 1{,}03 = 3\,000 \cdot 1{,}03^2 \approx 3\,182{,}70$.

## Die Zinseszinsformel

Im Zentrum dieses Lernbereichs steht die **Zinseszinsformel**:

$$
K_n = K_0 \cdot q^n
$$

Das folgende Widget zeigt die Herleitung dieser Formelam Zeitstrahl (voreingestellt ist Lenas Anlage): Über jedem Jahr steht das Kapital, darunter die Zinsen und der Zinsfaktor, mit dem von einem Jahr zum nächsten multipliziert wird. Der große Bogen fasst alle $n$ Jahresschritte zu einer einzigen Multiplikation mit $q^n$ zusammen.

{% include widgets/widget-zinseszins-herleitung.html %}

Mit der Zinseszinsformel können wir beispielsweise berechnen, wie viel Lenas Geld in sechs Jahren wert sein wird:

$$
K_6 = 3\,000 \cdot 1{,}03^6 \approx 3\,000 \cdot 1{,}1941 \approx 3\,582{,}16\,\text{€}
$$

{% include check-anker.html nummer="1" %}

## Sachaufgaben zur Zinseszinsrechnung

In Textaufgaben steht die gesuchte Größe nicht dabei. Deshalb ist zunächst zu klären, welche Werte gegeben sind und welche Größe gesucht ist. Hierbei helfen Signalwörter: „Kapital nach $n$ Jahren“ → $K_n$, „heute anlegen“ → $K_0$, „nach wie vielen Jahren“ → $n$, „mit welchem Zinssatz“ → $p$.

{% include check-anker.html nummer="2" %}

## Zinssatzwechsel

Lenas Bank bietet eine Alternative an: in den ersten zwei Jahren 2 %, danach vier Jahre lang 3,5 %. Die Laufzeit zerfällt damit in zwei Zinsphasen mit eigenem Zinsfaktor:

<div class="zeitstrahl" style="--zs-n: 6;">
<div class="zeitstrahl__track">
<div class="zeitstrahl__phase zeitstrahl__phase--1" style="--zs-from: 0; --zs-to: 2;"></div>
<div class="zeitstrahl__phase zeitstrahl__phase--2" style="--zs-from: 2; --zs-to: 6;"></div>
<span class="zeitstrahl__tick" style="--zs-t: 0;"><span class="zeitstrahl__jahr">0</span></span>
<span class="zeitstrahl__tick" style="--zs-t: 1;"><span class="zeitstrahl__jahr">1</span></span>
<span class="zeitstrahl__tick" style="--zs-t: 2;"><span class="zeitstrahl__jahr">2</span></span>
<span class="zeitstrahl__tick" style="--zs-t: 3;"><span class="zeitstrahl__jahr">3</span></span>
<span class="zeitstrahl__tick" style="--zs-t: 4;"><span class="zeitstrahl__jahr">4</span></span>
<span class="zeitstrahl__tick" style="--zs-t: 5;"><span class="zeitstrahl__jahr">5</span></span>
<span class="zeitstrahl__tick" style="--zs-t: 6;"><span class="zeitstrahl__jahr">6</span></span>
<span class="zeitstrahl__punkt" style="--zs-t: 0;"><span class="zeitstrahl__wert">$K_0 = 3\,000$ €</span></span>
<span class="zeitstrahl__punkt" style="--zs-t: 2;"><span class="zeitstrahl__wert">$K_2 \approx 3\,121{,}20$ €</span></span>
<span class="zeitstrahl__punkt" style="--zs-t: 6;"><span class="zeitstrahl__wert">$K_6 \approx 3\,581{,}65$ €</span></span>
<span class="zeitstrahl__label zeitstrahl__label--1" style="--zs-from: 0; --zs-to: 2;">Phase 1<br>$n_1 = 2$, $p_1 = 2\,\%$, $q_1 = 1{,}02$</span>
<span class="zeitstrahl__label zeitstrahl__label--2" style="--zs-from: 2; --zs-to: 6;">Phase 2<br>$n_2 = 4$, $p_2 = 3{,}5\,\%$, $q_2 = 1{,}035$</span>
<span class="zeitstrahl__achse">Jahre</span>
</div>
</div>

Die Zinseszinsformel wird einfach zweimal angewendet. Erst für die erste Phase:

$$
K_2 = 3\,000 \cdot 1{,}02^2 = 3\,121{,}20\,\text{€}
$$

Dieses Zwischenergebnis ist das Anfangskapital der zweiten Phase, die wieder mit der Zinseszinsformel berechnet wird:

$$
K_6 = 3\,121{,}20 \cdot 1{,}035^4 \approx 3\,581{,}65\,\text{€}
$$

Das Alternativangebot bringt also fast genau so viel wie die durchgehenden 3 % (3 582,16 €). Der Zwischenwert $K_{n_1}$ am Übergang ist der Schlüssel jeder Aufgabe zum Zinssatzwechsel: Er verbindet beide Phasen. Ist eine der sechs Größen $K_0$, $K_n$, $p_1$, $p_2$, $n_1$, $n_2$ gesucht, wird zuerst $K_{n_1}$ bestimmt – **vorwärts** aus $K_0$ mit $q_1^{n_1}$, wenn die Unbekannte in der zweiten Phase liegt, oder **rückwärts** aus $K_n$ durch Teilen durch $q_2^{n_2}$, wenn sie in der ersten Phase liegt. Danach bleibt in der anderen Phase eine gewöhnliche Zinseszinsaufgabe mit einer Unbekannten.

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
