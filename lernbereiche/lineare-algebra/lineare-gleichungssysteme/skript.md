---
layout: skript
title: Lineare Gleichungssysteme
description: Lineare Gleichungssysteme - Skript
lernbereich: lineare-gleichungssysteme
---

## Einführung

Ein lineares Gleichungssystem besteht aus mehreren linearen Gleichungen, die alle zugleich erfüllt sein sollen. In den Gleichungen gibt es eine oder mehrere Unbekannte.

$$
\begin{align}
3x + y &= 23 \\
-2x - y &= -16
\end{align}
$$

Hier sind einige kurze, einfache Anwendungsbeispiele für lineare Gleichungssysteme:

- PageRank-Algorithmus – zur Berechnung der Bedeutung von Webseiten im Google-Suchranking.
- Stromnetzberechnung – zur Bestimmung von Strömen und Spannungen in elektrischen Netzwerken.
- Gleichgewichtsanalysen in der Ökonomie – zur Ermittlung von Preisen und Produktionsmengen in Märkten mit mehreren Gütern.
- Bildverarbeitung – zur Rekonstruktion oder Filterung von Bildern, etwa bei Rauschunterdrückung.
- Physikalische Modelle – z. B. bei Kräften im statischen Gleichgewicht oder bei der Berechnung von Schnittpunkten von Ebenen.
- Computergraphik – zur Berechnung von Transformationen, Projektionen oder Beleuchtungseffekten in 3D-Szenen.
- Chemische Reaktionsgleichungen – zur Bestimmung der stöchiometrischen Koeffizienten bei der Reaktionsbilanzierung.

## Lösungsverfahren

Wir sehen, dass im obigen Beispiel $x$ und $y$ nicht direkt berechnet werden können, da in jeder Gleichung zwei Unbekannte auftreten. Um ein solches lineares Gleichungssystem nun nach $x$ und $y$ auflösen zu können, gibt es verschiedene Verfahren. Die Grundidee ist immer, die Gleichungen so zu kombinieren, dass nur noch eine Unbekannte in einer Gleichung auftritt. Diese Unbekannte kann dann bestimmt werden kann, und in der Folge auch die übrigen Unbekannten.

### Gleichsetzungsverfahren

<iframe width="560" height="315" src="https://www.youtube.com/embed/6BuVmbuxZco?si=bQ8gQxBzqQTycXh_" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

### Einsetzungsverfahren

<iframe width="560" height="315" src="https://www.youtube.com/embed/SDVU0ENxN7g?si=u7MGxLmobYcPQDDC" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

### Additionsverfahren

<iframe width="560" height="315" src="https://www.youtube.com/embed/T08IjF7OPf4?si=dG4-2SQxtpGjR7bc" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

{%include info.html
index="1"
frage="Lösen linearer Gleichungssysteme mit 2 Gleichungen und 2 Unbekannten"
antwort="

- Gleichsetzungsverfahren: Beide Gleichungen nach der gleichen Unbekannten auflösen und gleichsetzen
- Einsetzungsverfahren: Eine Gleichung nach einer Unbekannten auflösen und diese Lösung in die andere Gleichung einsetzen
- Additionsverfahren: Durch geschicktes Addieren der beiden Gleichungen eine Unbekannte eliminieren
  "
  %}

<div id="skript-aufgabe-1"></div>

Betrachten wir lineare Gleichungssysteme mit mehreren Gleichungen und Unbekannten, so werden das Gleichsetzungs- und das Einsetzungsverfahren schnell unübersichtlich. Schreibt man das System jedoch in einer geordneten, tabellarischen Form auf, lässt es sich deutlich systematischer bearbeiten. Dieses Vorgehen bezeichnet man als Gaußschen Algorithmus oder Gauß-Verfahren.

Der Gauß-Algorithmus ist im Grunde eine systematische Erweiterung des Additionsverfahrens. Durch geschickte Umformungen der Gleichungen wird das System schrittweise vereinfacht, bis sich die Lösungen direkt ablesen lassen.

### Gauß-Algorithmus

<iframe width='560' height='315' src='https://www.youtube.com/embed/aosbq7Ci7Ec?si=Z-LlK00xnOk_908D' title='YouTube video player' frameborder='0' allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share' referrerpolicy='strict-origin-when-cross-origin' allowfullscreen></iframe>

{%include info.html
index="2"
frage="Lösen linearer Gleichungssysteme mit 3 Gleichungen und 3 Unbekannten"
antwort="Umformen des linearen Gleichungssystem in eine obere Dreiecksform"
%}

<div id="skript-aufgabe-2"></div>

Die Stärke des Gauß-Algorithmus liegt darin, dass er grundsätzlich für beliebig viele Gleichungen und Unbekannte anwendbar ist. Der Einfachheit halber verzichtet man dabei meist auf die Bezeichnung der Unbekannten und stellt das Gleichungssystem stattdessen in einer übersichtlichen Matrixform dar.

#### Beispiel

$$
\begin{align*}
x_1 + x_2 + x_3 &= 3 \\
4x_1 + 2x_2 + x_3 &= 14 \\
16x_1 - 4x_2 + x_3 &= 8
\end{align*}
$$

{% include flip-card.html
frage="Darstellung in Matrixform"
antwort="

$$
\begin{pmatrix}
1 & 1 & 1 \\
4 & 2 & 1 \\
16 & -4 & 1
\end{pmatrix}
$$

" %}

<iframe width='560' height='315' src='https://www.youtube.com/embed/N4iuTaHUC80?si=BrInX6fFM52Kg3kr' title='YouTube video player' frameborder='0' allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share' referrerpolicy='strict-origin-when-cross-origin' allowfullscreen></iframe>

{%include info.html
index="3"
frage="Lösen linearer Gleichungssysteme mit 4 Gleichungen und 4 Unbekannten"
antwort="Umformen des linearen Gleichungssystem in eine obere Dreiecksform"
%}

<div id="skript-aufgabe-3"></div>

## Lösbarkeit linearer Gleichungsysteme

Wir betrachten die folgenden drei linearen Gleichungssysteme
