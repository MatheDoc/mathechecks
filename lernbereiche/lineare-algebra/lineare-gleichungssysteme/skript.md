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

### Gauß-Algorithmus

Der Gauß-Algorithmus ist im Grunde eine systematische Erweiterung des Additionsverfahrens. Durch geschickte Umformungen der Gleichungen wird das System schrittweise vereinfacht, bis sich die Lösungen direkt berechnen lassen.

<iframe width='560' height='315' src='https://www.youtube.com/embed/aosbq7Ci7Ec?si=Z-LlK00xnOk_908D' title='YouTube video player' frameborder='0' allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share' referrerpolicy='strict-origin-when-cross-origin' allowfullscreen></iframe>

Die Stärke des Gauß-Algorithmus liegt darin, dass er grundsätzlich für beliebig viele Gleichungen und Unbekannte anwendbar ist. Der Einfachheit halber verzichten wir dabei meist auf die Bezeichnung der Unbekannten und stellen das Gleichungssystem stattdessen in einer übersichtlichen Matrixform dar.

Wir betrachten dazu das folgende lineare Gleichungssystem:

$$
\begin{align*}
x_1 + x_2 + x_3 &= 3 \\
4x_1 + 2x_2 + x_3 &= 14 \\
16x_1 - 4x_2 + x_3 &= 8
\end{align*}
$$

Die Matrixform erhalten wir, indem die Unbekannten und Rechenoperationen ausgelassen werden, die Koeffizienten müssen dabei konsequent untereinander geschrieben werden.

{% include flip-card.html
frage="Darstellung in Matrixform"
antwort="

$$
\begin{pmatrix}
1 & 1   & 1 & | & 3\\
4 & 2   & 1 & | & 14\\
16 & -4 & 1 & | & 8
\end{pmatrix}
$$

" %}

Diese Matrix wird mit Hilfe des Additionsverfahrens in eine obere Dreiecksform überführt.

{% include flip-card.html
frage="Umformen in obere Dreiecksform"
antwort="

$$
\begin{pmatrix}
1 & 1 & 1 & | & 3\\
4 & 2 & 1 & | & 14\\
16 & -4 & 1 &| & 8
\end{pmatrix}
\quad
\begin{matrix}
\\
II-4\cdot I\\
III-16\cdot I
\end{matrix}
$$

$$
\begin{pmatrix}
1 & 1 & 1 & | & 3\\
0 & -2 & -3 & | & 2\\
0 & -20 & -15 &| & -40
\end{pmatrix}
\quad
\begin{matrix}
\\
\\
III-10\cdot II
\end{matrix}
$$

$$
\begin{pmatrix}
1 & 1 & 1 & | & 3\\
0 & -2 & -3 & | & 2\\
0 & 0 & 15 &| & -60
\end{pmatrix}
\quad
\begin{matrix}
\\
\\
\quad\quad\quad\quad\quad
\end{matrix}
$$

" %}

Nun verwenden wieder die ausführliche Schreibweise, um angefangen von der letzten Gleichung alle Unbekannten nacheinander zu bestimmen.

{% include flip-card.html
frage="Suksessives Auflösen nach den Unbekannten"
antwort="Ausgeschrieben lautet das System:

$$
\begin{alignat*}{3}
I:\quad   & x_1+x_2+x_3 & =3\\
II:\quad  & -2x_2-3x_3  & =2\\
III:\quad & 15x_3       & =-60
\end{alignat*}
$$

Auflösen nach den Unbekannten:

$$
\begin{alignat*}{2}
III:\quad & 15x_3=-60 \Rightarrow x_3=-4\quad ✅\\
II:\quad  & -2x_2-3\cdot (-4)=2 \Rightarrow -2x_2=-10 \Rightarrow x_2=5\quad ✅\\
I:\quad   & x_1+5-4=3 \Rightarrow x_1=2\quad ✅\\
\end{alignat*}
$$

"
%}

Der Gauß-Algorithmus bezeichnet konkret das Verfahren, mit dem wir eine obere Dreiecksmatrix oder, allgemeiner, eine Zeilenstufenform erhalten. Dabei verwendeten wir die sogenannten elementaren Zeilenumformungen:

- Vertauschen zweier Zeilen
- Multiplizieren einer Zeile mit einem von null verschiedenen Faktor
- Addieren oder Subtrahieren eines Vielfachen einer Zeile zu einer anderen Zeile

Das folgende Video zeigt ein Beispiel, in dem ein Zeilentausch notwendig ist, um in der linken oberen Ecke eine Zahl ungleich Null zu erhalten.

<iframe width="560" height="315" src="https://www.youtube.com/embed/ac8r-E5h9FI?si=pOwZHOmOnZLPiBol" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

{%include info.html
index="2"
frage="Lösen linearer Gleichungssysteme mit 3 Gleichungen und 3 Unbekannten"
antwort="

1. Darstellung in Matrixform
2. Umformen in obere Dreiecksform
3. Suksessives Auflösen nach den Unbekannten

"
%}

<div id="skript-aufgabe-2"></div>

{%include info.html
index="3"
frage="Lösen linearer Gleichungssysteme mit 4 Gleichungen und 4 Unbekannten"
antwort="

1. Darstellung in Matrixform
2. Umformen in obere Dreiecksform
3. Suksessives Auflösen nach den Unbekannten

"
%}

<div id="skript-aufgabe-3"></div>

## Lösbarkeit linearer Gleichungsysteme

Wir haben also {% include ttt.html text="$5$" tt="$2+3$" %} und das ist gut so.

{% include firebase-test.html %}
