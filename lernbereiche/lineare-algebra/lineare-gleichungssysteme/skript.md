---
layout: skript
title: Lineare Gleichungssysteme
description: Lineare Gleichungssysteme - Skript
lernbereich: lineare-gleichungssysteme
---

## Einführung

Ein lineares Gleichungssystem (LGS) besteht aus mehreren linearen Gleichungen, die alle zugleich erfüllt sein sollen. In diesen Gleichungen treten eine oder mehrere Unbekannte auf. Ein einfaches Beispiel ist das folgende LGS mit den Unbekannten 
$x$ und $y$:

$$
\begin{align}
3x + y &= 23 \\
-2x - y &= -16
\end{align}
$$

Die typische Fragestellung besteht darin, LGS zu lösen. Das bedeutet, Werte für die Unbekannten zu bestimmen, sodass alle Gleichungen des Systems gleichzeitig erfüllt sind. Im vorliegenden Beispiel sind also die Werte von 
$x$ und $y$ zu berechnen, die beide Gleichungen zugleich korrekt machen.

LGS finden weitreichend Anwendungen:

- PageRank-Algorithmus – zur Berechnung der Bedeutung von Webseiten im Google-Suchranking.
- Stromnetzberechnung – zur Bestimmung von Strömen und Spannungen in elektrischen Netzwerken.
- Gleichgewichtsanalysen in der Ökonomie – zur Ermittlung von Preisen und Produktionsmengen in Märkten mit mehreren Gütern.
- Bildverarbeitung – zur Rekonstruktion oder Filterung von Bildern, etwa bei Rauschunterdrückung.
- Physikalische Modelle – z. B. bei Kräften im statischen Gleichgewicht oder bei der Berechnung von Schnittpunkten von Ebenen.
- Computergraphik – zur Berechnung von Transformationen, Projektionen oder Beleuchtungseffekten in 3D-Szenen.
- Chemische Reaktionsgleichungen – zur Bestimmung der stöchiometrischen Koeffizienten bei der Reaktionsbilanzierung.

## Lösungsverfahren

Wir sehen, dass im obigen Beispiel $x$ und $y$ nicht direkt berechnet werden können, da in jeder Gleichung zwei Unbekannte auftreten. Um ein solches LGS nun nach $x$ und $y$ auflösen zu können, gibt es verschiedene Verfahren. Die Grundidee ist immer, die Gleichungen so zu kombinieren, dass nur noch eine Unbekannte in einer Gleichung auftritt. Diese Unbekannte kann dann bestimmt werden, und in der Folge auch die übrigen Unbekannten.

### Gleichsetzungsverfahren

<iframe  src="https://www.youtube.com/embed/6BuVmbuxZco?si=bQ8gQxBzqQTycXh_" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

### Einsetzungsverfahren

<iframe  src="https://www.youtube.com/embed/SDVU0ENxN7g?si=u7MGxLmobYcPQDDC" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

### Additionsverfahren

<iframe  src="https://www.youtube.com/embed/T08IjF7OPf4?si=dG4-2SQxtpGjR7bc" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

{%include info.html
index="1"
frage="Lösen LGS mit 2 Gleichungen und 2 Unbekannten"
antwort="

- Gleichsetzungsverfahren: Beide Gleichungen nach der gleichen Unbekannten auflösen und gleichsetzen
- Einsetzungsverfahren: Eine Gleichung nach einer Unbekannten auflösen und diese Lösung in die andere Gleichung einsetzen
- Additionsverfahren: Durch geschicktes Addieren der beiden Gleichungen eine Unbekannte eliminieren
  "
  %}

<div id="skript-aufgabe-1"></div>

### Gauß-Algorithmus

Der Gauß-Algorithmus ist im Grunde eine systematische Erweiterung des Additionsverfahrens. Durch geschickte Umformungen der Gleichungen wird das System schrittweise vereinfacht, bis sich die Lösungen direkt berechnen lassen.

<iframe  src='https://www.youtube.com/embed/aosbq7Ci7Ec?si=Z-LlK00xnOk_908D' title='YouTube video player' frameborder='0' allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share' referrerpolicy='strict-origin-when-cross-origin' allowfullscreen></iframe>

Die Stärke des Gauß-Algorithmus liegt darin, dass er grundsätzlich für beliebig viele Gleichungen und Unbekannte anwendbar ist. Der Einfachheit halber verzichten wir dabei meist auf die Bezeichnung der Unbekannten und stellen das Gleichungssystem stattdessen in einer übersichtlichen Matrixform dar.

Wir betrachten dazu das folgende LGS:

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

Diese Matrix wird mit Hilfe des Additionsverfahrens in eine obere Dreiecksform überführt, das heißt in eine Matrix, bei der alle Elemente unterhalb der Diagonalen gleich null sind.

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

Nun verwenden wir wieder die ausführliche Schreibweise, um angefangen von der letzten Gleichung alle Unbekannten nacheinander zu bestimmen.

{% include flip-card.html
frage="Sukzessives Auflösen nach den Unbekannten"
antwort="Ausgeschrieben lautet das System:

$$
\begin{alignat*}{3}
I:\quad   & x_1+x_2+x_3 & =3\\
II:\quad  & -2x_2-3x_3  & =2\\
III:\quad & 15x_3       & =-60\\
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

Der Gauß-Algorithmus bezeichnet konkret das Verfahren, mit dem wir eine obere Dreiecksmatrix erhalten. Dabei verwenden wir die sogenannten elementaren Zeilenumformungen:

- Vertauschen zweier Zeilen
- Multiplizieren einer Zeile mit einem von null verschiedenen Faktor
- Addieren oder Subtrahieren eines Vielfachen einer Zeile zu einer anderen Zeile

Das folgende Video zeigt ein Beispiel, in dem ein Zeilentausch notwendig ist, um in der linken oberen Ecke eine Zahl ungleich Null zu erhalten.

<iframe src="https://www.youtube.com/embed/ac8r-E5h9FI?si=pOwZHOmOnZLPiBol" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

{%include info.html
index="2"
frage="Lösen LGS mit 3 Gleichungen und 3 Unbekannten"
antwort="

1. Darstellung in Matrixform
2. Umformen in obere Dreiecksform
3. Sukzessives Auflösen nach den Unbekannten

"
%}

<div id="skript-aufgabe-2"></div>

{%include info.html
index="3"
frage="Lösen LGS mit 4 Gleichungen und 4 Unbekannten"
antwort="

1. Darstellung in Matrixform
2. Umformen in obere Dreiecksform
3. Sukzessives Auflösen nach den Unbekannten

"
%}

<div id="skript-aufgabe-3"></div>

## Lösungsarten

Bisher haben wir nur LGS mit genau einer Lösung betrachtet. Es gibt aber auch den Fall, dass keine oder unendliche viele Lösungen vorliegen. Dazu betrachten wir die folgenden drei Beispiele, in denen die LGS bereits in Matrixform vorliegen.

### Beispiel 1: Eine eindeutige Lösung

$$
\begin{pmatrix}
1 & 0 & 3 & | & 9\\
2 & 2 & 1 & | & 10\\
3 & 4 & 3 &| & 19
\end{pmatrix}
\quad
\begin{matrix}
\\
II-2\cdot I\\
III-3\cdot I
\end{matrix}
$$

$$
\begin{pmatrix}
1 & 0 & 3 & | & 9\\
0 & 2 & -5 & | & -8\\
0 & 4 & -6 &| & -8
\end{pmatrix}
\quad
\begin{matrix}
\\
\\
III-2\cdot II
\end{matrix}
$$

$$
\begin{pmatrix}
1 & 0 & 3 & | & 9\\
0 & 2 & -5 & | & -8\\
0 & 0 & 4 &| & 8
\end{pmatrix}
\quad
\begin{matrix}
\\
\\
\quad\quad\quad\quad\quad
\end{matrix}
$$

Ausgeschrieben erhalten wir:

$$
\begin{align*}
III:\quad & 4x_3=8 \Rightarrow x_3=2\\
II:\quad & 2x_2-5\cdot 2=-8 \Rightarrow x_2=1\\
I:\quad & x_1+0\cdot 1+3\cdot 2 = 9 \Rightarrow x_1=3\\
\end{align*}
$$

Das LGS hat also die eindeutige Lösung $x_1=3$, $x_2=1$ und $x_3=2$.

### Beispiel 2: Keine Lösung

$$
\begin{pmatrix}
1 & 2 & 1 & | & 3\\
2 & 3 & 1 & | & 2\\
5 & 8 & 3 &| & 4
\end{pmatrix}
\quad
\begin{matrix}
\\
II-2\cdot I\\
III-5\cdot I
\end{matrix}
$$

$$
\begin{pmatrix}
1 & 2 & 1 & | & 3\\
0 & -1 & -1 & | & -4\\
0 & -2 & -2 &| & -11
\end{pmatrix}
\quad
\begin{matrix}
\\
\\
III-2\cdot II
\end{matrix}
$$

$$
\begin{pmatrix}
1 & 2 & 1 & | & 3\\
0 & -1 & -1 & | & -4\\
0 & 0 & 0 &| & -3
\end{pmatrix}
\quad
\begin{matrix}
\\
\\
\quad\quad\quad\quad\quad
\end{matrix}
$$

Ausgeschrieben erhalten wir:

$$
\begin{align*}
III:\quad & 0=-3 \Rightarrow \text{falsche Aussage}\\
\end{align*}
$$

Das LGS hat also keine Lösung.

### Beispiel 3: Unendlich viele Lösungen

$$
\begin{pmatrix}
1 & 2 & 1 & | & 3\\
2 & 3 & 1 & | & 2\\
5 & 8 & 3 &| & 7
\end{pmatrix}
\quad
\begin{matrix}
\\
II-2\cdot I\\
III-5\cdot I
\end{matrix}
$$

$$
\begin{pmatrix}
1 & 2 & 1 & | & 3\\
0 & -1 & -1 & | & -4\\
0 & -2 & -2 &| & -8
\end{pmatrix}
\quad
\begin{matrix}
\\
\\
III-2\cdot II
\end{matrix}
$$

$$
\begin{pmatrix}
1 & 2 & 1 & | & 3\\
0 & -1 & -1 & | & -4\\
0 & 0 & 0 &| & 0
\end{pmatrix}
\quad
\begin{matrix}
\\
\\
\quad\quad\quad\quad\quad
\end{matrix}
$$

Ausgeschrieben erhalten wir:

$$
\begin{align*}
III:\quad & 0\cdot x_3=0 \\
        & \text{Wir sehen, dass jede beliebige reelle Zahl eine Lösung für $x_3$ ist. Formal schreiben wir dafür $x_3=t$ mit $t\in\mathbb{R}$.}\\
II:\quad & -x_2-t=-4 \Rightarrow -x_2=t-4 \Rightarrow x_2=4-t\\
I:\quad & x_1+2(4-t)+t=3 \Rightarrow x_1+8-2t+t=3 \Rightarrow x_1=t-5
\end{align*}
$$

Das LGS hat also die unendlich vielen Lösungen $x_1=t-5$, $x_2=4-t$ und $x_3=t$, wobei $t$ eine beliebige reelle Zahl ist.

Statt $x_3$ hätten wir hier auch $x_1$ oder $x_2$ gleich $t$ setzen können. Die Gestalt der Lösung sähe dann anders aus, die Menge der Lösungen ist aber stets gleich.

### Zusammenfassung

LGS können die drei folgenden Arten von Lösungen haben:

1. Eine eindeutige Lösung
2. Keine Lösung
3. Unendlich viele Lösungen

## Allgemeine Systeme

Im Allgemeinen muss in einem LGS die Anzahl der Unbekannten nicht mit der Anzahl der Gleichungen übereinstimmen. Wir nennen LGS mit mehr Unbekannten als Gleichungen **unterbestimmt** und LGS mit weniger Unbekannten als Gleichungen **überbestimmt**. Auch in diesen Fällen lässt sich das System systematisch mit dem Gauß-Algorithmus lösen. Statt von einer oberen Dreiecksform sprechen wir hier allgemeiner von einer Zeilenstufenform. Diese liegt vor, wenn in jeder Zeile das erste von Null verschiedene Element weiter rechts liegt als in der darüberliegenden Zeile und wenn alle Einträge unterhalb dieser führenden Elemente jeweils Null sind.

### Beispiel: Unterbestimmte LGS

$$
\begin{align*}
x_1 + 4x_2 + 3x_3 &= 2 \\
2x_1 + 6x_2 + 8x_3 &= 3 \\
\end{align*}
$$

Darstellung in Zeilenstufenform:

$$
\begin{pmatrix}
1 & 4 & 3 & | & 2\\
2 & 6 & 8 & | & 3\\
\end{pmatrix}
\quad
\begin{matrix}
\\
II-2\cdot I
\end{matrix}
$$

$$
\begin{pmatrix}
1 & 4 & 3 & | & 2 \\
0 & -2 & 2 & | & -1\\
\end{pmatrix}
\quad
\begin{matrix}
\\
\quad\quad\quad\quad\quad
\end{matrix}
$$

Ausgeschrieben erhalten wir:

$$
\begin{align*}
II:\quad & -2\cdot x_2 + 2x_3=-1 \\
        & \text{Wir sehen, dass wir für $x_3$ jede beliebige reelle Zahl vorgeben können, und dann diese Gleichung nach $x_2$ auflösen können.}\\
        &x_3=t\text{ mit }t\in\mathbb{R}.\\
        &-2\cdot x_2+2\cdot t =-1 \Rightarrow x_2=0,5+t\\
I:\quad & x_1+4(0,5+t)+3t=2 \Rightarrow x_1+2+4t+3t=5 \Rightarrow x_1=3-7t
\end{align*}
$$

### Beispiel: Überbestimmte LGS

$$
\begin{align*}
x_1 + 2x_2  &= 4 \\
3x_1 + 4x_2  &= 3 \\
2x_1 + 1x_2  &= 5 \\
\end{align*}
$$

Darstellung in Zeilenstufenform:

$$
\begin{pmatrix}
1 & 2 & | & 4\\
3 & 4 & | & 3\\
2 & 1 &| & 5
\end{pmatrix}
\quad
\begin{matrix}
\\
II-3\cdot I\\
III-2\cdot I
\end{matrix}
$$

$$
\begin{pmatrix}
1 & 2 & | & 4\\
0 & -2 & | & -9\\
0 & -3 &| & -3
\end{pmatrix}
\quad
\begin{matrix}
\\
\\
3\cdot II-2\cdot III
\end{matrix}
$$

$$
\begin{pmatrix}
1 & 2 & | & 4\\
0 & -2 & | & -9\\
0 & 0 &| & -21
\end{pmatrix}
\quad
\begin{matrix}
\\
\\
\quad\quad\quad\quad\quad
\end{matrix}
$$

Ausgeschrieben erhalten wir:

$$
III:\quad  0=-21 \Rightarrow\text{falsche Aussage}
$$

Das LGS hat also keine Lösung.

### Zusammenfassung

Die letzten beiden Beispiele verdeutlichen zusammen mit den zu Beginn betrachteten LGS den generischen, also häufigen, jedoch nicht ausnahmslosen Fall.

- Quadratisches LGS, d.h. Anzahl Gleichungen = Anzahl Unbekannte: eine eindeutige Lösung 
- Unterbestimmtes LGS, d.h. Anzahl Gleichungen < Anzahl Unbekannte: unendlich viele Lösungen
- Überbestimmtes LGS, d.h. Anzahl Gleichungen > Anzahl Unbekannte: keine Lösung

Wichtig: Wie wir bereits gesehen haben, können aber auch LGS mit der gleichen Anzahl an Gleichungen und Unbekannten unendlich viele oder auch keine Lösung besitzen. Ähnliches gilt für unter- und überbestimmte LGS. Eine systematische Untersuchung dieser Fälle erfolgt im nächsten Abschnitt.

## Das Rangkriterium

Mit Hilfe des Rangkriteriums können wir systematisch angeben, wie viele Lösungen ein LGS besitzt. Zunächst benötigen wir die Definition des **Rangs** einer Matrix: Eine Matrix liege in Zeilenstufenform vor. Dann heißt die Anzahl der Zeilen, in denen nicht alle Elemente 0 sind, Rang von $A$, in Kurzschreibweise $rg(A)$. Diese Defintion ist anwendbar auf gewöhnliche Koeffizientenmatrizen, z.B.

$$
A=
\begin{pmatrix}
-4 & 5  & 0\\
0 & 8  & 1\\
0 & 0  & 0
\end{pmatrix}
$$

als auch auf erweiterte Koeffizientenmatrizen, z.B. 

$$
(A\mid y)=
\begin{pmatrix}
-4 & 5 & 0 & | & 2\\
0 & 8 & 1  & | & 0\\
0 & 0 & 0  & | & 1
\end{pmatrix}.
$$ 

In diesen Beispielen ist {% include ttt.html text="$rg(A)=2$" tt="da die letzte Zeile von $A$ nur aus Nullen besteht" %} und {% include ttt.html text="$rg(A\mid y)=3$" tt="da alle drei Zeilen von $(A\mid y)$ von 0 verschiedene Elemente haben" %}.

### Satz

Wir betrachten das LGS $(A\mid y)$. Die Anzahl der Spalten von $A$, d.h. die Anzahl der Unbekannten, bezeichnen wir mit $n$. Dann gilt für die Anzahl der Lösungen: 

* $rg(A)=rg(A\mid y)=n$: eine eindeutige Lösung
* $rg(A)=rg(A\mid y)<n$: unendlich viele Lösungen
* $rg(A)<rg(A\mid y)$: keine Lösung

### Beispiele

Matrixschreibweise
Zeilenstufen
Rangkriterium


