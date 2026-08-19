---
layout: module
title: "Regression erklärt – passende Funktionen zu Daten finden"
description: "Regression Schritt für Schritt erklärt: Regressionsgerade rechnerisch berechnen, quadratische und kubische Regression über lineare Gleichungssysteme, Prognosen im Sachkontext und Regression mit dem GTR."
page_context: Lernbereich
nav: dashboard
body_class: page-module
module_key: skript
published: true
lernbereich: regression
gebiet: analysis
permalink: /lernbereiche/analysis/regression/skript.html
---

# Regression: passende Funktionen zu Daten finden

## Regression

Wie hängen zwei Größen voneinander ab? Diese Frage stellt sich in nahezu sämtlichen Gebieten, z.B. in der Wirtschaft (Wie hängt der Gewinn von der Absatzmenge ab?), in der Politik (Wie hängt die Bevölkerungsanzahl von der Zeit ab?) oder in den Naturwissenschaften (Wie hängt die zurückgelegte Fallstrecke eines frei fallenden Körpers von seiner Fallzeit ab?). Eine Antwort auf diese Frage kann aus einer konkreten mathematischen Funktion bestehen, die die beiden Größen zueinander in Beziehung setzt. Um eine solche Funktion zu finden, werden zunächst durch Umfragen, Messungen u.Ä. Datenpunkte ermittelt (z.B. x-Wert Jahreszahl, y-Wert Bevölkerungszahl). Im Anschluss sucht man dann nach einer Funktion, die diese Datenpunkte möglichst gut approximiert (annähert). Dieses Vorgehen heißt Regression. Dabei treten zwei Fragen auf:

1. Welche Funktionsart (linear, quadratisch, kubisch, exponentiell etc.) ist am ehesten geeignet?
2. Welchen Wert haben die Parameter der gewählten Funktionsart (bei linearen Funktionen müssen z.B. die Werte der Steigung und des y-Abschnitts bestimmt werden)?

{% include widgets/widget-punktwolke-regression.html %}

Die erste Frage kann grob beantwortet werden, indem man die vorliegenden Datenpunkte graphisch darstellt und sich dann überlegt, welcher Funktionsgraph am besten zu der Punktwolke passt (hier gibt es natürlich auch systematischere Verfahren). Hat man sich bei der ersten Frage für eine lineare Funktion entschieden, so spricht man auch von einer linearen Regression (entsprechend: quadratisch, exponentiell etc.).

Die zweite Frage steht im Zentrum dieses Skripts. Zunächst klären wir, was „möglichst gut approximieren" überhaupt bedeutet. Danach bestimmen wir die Parameter rechnerisch: zuerst für lineare Funktionen mit zwei fertigen Formeln, anschließend für quadratische und kubische Funktionen über ein lineares Gleichungssystem. Zum Abschluss zeigen wir, wie der GTR dieselbe Rechnung auf Knopfdruck erledigt.

## Die Idee: quadratische Abweichungen minimieren

Wann approximiert eine Funktion die Datenpunkte möglichst gut? Um das zu präzisieren, vergleichen wir für eine Kandidatenfunktion $f$ an jeder gegebenen Stelle $x_i$ den Funktionswert $f(x_i)$ mit dem tatsächlich gemessenen Wert $y_i$. Die Differenz $y_i-f(x_i)$ heißt Abweichung (auch: Residuum). Anschaulich ist die Abweichung der senkrechte Abstand zwischen dem Datenpunkt $(x_i \mid y_i)$ und dem Graphen von $f$: Liegt der Datenpunkt oberhalb des Graphen, ist die Abweichung positiv, liegt er unterhalb, ist sie negativ.

Eine gute Funktion sollte insgesamt kleine Abweichungen haben. Die Abweichungen einfach zu addieren, ist allerdings keine gute Idee: Positive und negative Abweichungen heben sich gegenseitig auf, sodass auch eine schlecht passende Funktion eine Abweichungssumme nahe null haben kann. Deshalb werden die Abweichungen zuerst quadriert. Das hat zwei Effekte: Die Vorzeichen verschwinden (jede Abweichung zählt positiv), und große Abweichungen wiegen überproportional schwer.

Als Gütekriterium dient also die Summe der Abweichungsquadrate. Für eine Gerade $f(x)=m\cdot x+b$ lautet sie

$$S(m,b)=\sum_{i=1}^{n}\big(y_i-(m\cdot x_i+b)\big)^2.$$

Die beste Gerade ist diejenige, für die $S(m,b)$ so klein wie möglich wird. Dieses Vorgehen heißt **Methode der kleinsten Quadrate**.

Im folgenden Widget kannst du die Steigung $m$ und den y-Achsenabschnitt $b$ einer Geraden selbst einstellen. Die Abweichungsquadrate werden als Flächen angezeigt, ihre Summe wird laufend berechnet.

{% include widgets/widget-regression-minimierung.html %}

Verändere $m$ und $b$ und versuche, die Summe der Abweichungsquadrate so klein wie möglich zu machen. Genau diese Minimierungsaufgabe lösen wir in den nächsten Abschnitten rechnerisch – die von dir gefundene beste Gerade lässt sich dann exakt bestimmen.

## Spezialfall: Gerade durch zwei Punkte

Bei genau zwei Datenpunkten $(x_1 \mid y_1)$ und $(x_2 \mid y_2)$ mit $x_1\neq x_2$ ist die Lösung bereits bekannt: Es gibt genau eine Gerade, die exakt durch beide Punkte verläuft. Beide Abweichungen sind dann null, also ist auch die Summe der Abweichungsquadrate $S=0$ – kleiner geht es nicht. Die beste Gerade im Sinne der Regression ist hier also einfach die Gerade durch die beiden Punkte.

Ihre Steigung liefert die bekannte Steigungsformel

$$m=\frac{y_2-y_1}{x_2-x_1},$$

also Differenz der y-Werte geteilt durch Differenz der x-Werte. Den y-Achsenabschnitt $b$ erhält man anschließend, indem man einen der beiden Punkte in $y=m\cdot x+b$ einsetzt und nach $b$ auflöst.

Ab drei Datenpunkten liegen die Punkte in der Regel nicht mehr exakt auf einer gemeinsamen Geraden. Dann ist $S=0$ nicht mehr erreichbar, und wir brauchen ein Verfahren, das die Gerade mit der kleinstmöglichen Abweichungssumme findet. Genau das leistet der nächste Abschnitt.

## Lineare Regression

Die Abweichungssumme $S(m,b)$ hängt von den beiden Parametern $m$ und $b$ ab. Um ihr Minimum zu finden, verwenden wir die gewöhnlichen Methoden der Differentialrechnung. Da hier zwei Variablen $m$ und $b$ auftreten, betrachten wir einmal $S$ in Abhängigkeit von $b$ mit Parameter $m$, d.h. $S_m(b)$, und einmal $S$ in Abhängigkeit von $m$ mit Parameter $b$, d.h. $S_b(m)$. Die notwendige Bedingung für Extrema besagt, dass $S'_m(b)=0$ und $S'_b(m)=0$ sein muss. Diese beiden Gleichungen können nun nach den beiden Unbekannten $m$ und $b$ aufgelöst werden (auf die hinreichende Bedingung verzichten wir hier, man kann zeigen, dass die Lösungen der notwendigen Bedingung wirklich extremal sind).

### Beispiel: Drei Punkte von Hand

Gegeben sind die drei Datenpunkte $(1 \mid 1)$, $(2 \mid 3)$ und $(3 \mid 2)$. Die Abweichungssumme für eine Gerade $f(x)=m\cdot x+b$ lautet

$$S(m,b)=\big(1-(m\cdot 1+b)\big)^2+\big(3-(m\cdot 2+b)\big)^2+\big(2-(m\cdot 3+b)\big)^2.$$

Ausmultiplizieren und Zusammenfassen ergibt

$$S(m,b)=14m^2+12mb+3b^2-26m-12b+14.$$

Fasst man $m$ als Parameter auf und sortiert nach Potenzen von $b$, entsteht eine quadratische Funktion in $b$:

$$S_m(b)=3b^2+(12m-12)\cdot b+\big(14m^2-26m+14\big)$$

Ihre Ableitung nach $b$ wird null gesetzt:

$$S'_m(b)=6b+12m-12=0$$

Genauso wird $S$ nach Potenzen von $m$ sortiert (jetzt ist $b$ der Parameter) und nach $m$ abgeleitet:

$$S_b(m)=14m^2+(12b-26)\cdot m+\big(3b^2-12b+14\big), \qquad S'_b(m)=28m+12b-26=0$$

Damit liegen zwei lineare Gleichungen für die beiden Unbekannten $m$ und $b$ vor. Die erste Gleichung liefert nach $b$ aufgelöst $b=2-2m$; eingesetzt in die zweite Gleichung:

$$28m+12\cdot(2-2m)-26=0 \quad\Longrightarrow\quad 4m-2=0 \quad\Longrightarrow\quad m=0{,}5$$

Mit $b=2-2\cdot 0{,}5=1$ lautet die beste Gerade also $f(x)=0{,}5x+1$.

{% include graph.html
	funktionen='[{"name":"f", "term":"0.5*x+1", "color":"#4363d8"}]'
	punkte='[
	 {"x":1,"y":1,"text":"(1 | 1)"},
	 {"x":2,"y":3,"text":"(2 | 3)"},
	 {"x":3,"y":2,"text":"(3 | 2)"}
	]'
	xachse="x"
	yachse="y"
	xmin=0
	xmax=4
	ymin=0
	ymax=4
%}

Beachte: Abgeleitet wird hier nach $m$ bzw. nach $b$ – nicht nach $x$. Die Datenwerte $x_i$ und $y_i$ sind feste Zahlen aus der Wertetabelle; die Variablen der Funktion $S$ sind die Parameter der gesuchten Geraden.

Für den allgemeinen Fall betrachten wir $n$ Datenpunkte $(x_1 \mid y_1),\,(x_2 \mid y_2),\,\ldots,\,(x_n \mid y_n)$ und gehen genauso vor wie im Beispiel – nur mit Summenzeichen statt konkreter Zahlen: Die Abweichungssumme $S(m,b)$ wird einmal als Funktion $S_m(b)$ und einmal als Funktion $S_b(m)$ aufgefasst, beide Ableitungen werden null gesetzt, und das entstehende Gleichungssystem wird nach $m$ und $b$ aufgelöst.

Man kann zeigen (siehe Exkurs unten), dass die beiden Gleichungen $S'_m(b)=0$ und $S'_b(m)=0$ zu folgenden **Regressionsformeln** führen:

$$m=\frac{\sum (x_i-\bar{x})(y_i-\bar{y})}{\sum (x_i-\bar{x})^2}, \qquad b=\bar{y}-m\cdot\bar{x}$$

Dabei sind $\bar{x}$ und $\bar{y}$ die Mittelwerte der x-Werte bzw. der y-Werte. In der Praxis legt man eine Tabelle mit den Abweichungen $x_i-\bar{x}$ und $y_i-\bar{y}$ an, bildet daraus die Produkte und Quadrate und summiert.

Die beiden Formeln lassen sich anschaulich deuten: Der Zähler der $m$-Formel misst, ob die x- und y-Werte gemeinsam von ihren Mittelwerten abweichen – liegen $x_i$ und $y_i$ tendenziell gleichzeitig über bzw. unter ihrem Mittelwert, sind die Produkte überwiegend positiv und die Steigung wird positiv. Der Nenner misst die Streuung der x-Werte. (Der Zähler trägt übrigens – bis auf einen Faktor – den Namen *Kovarianz*.) Stellt man die $b$-Formel zu $\bar{y}=m\cdot\bar{x}+b$ um, ergibt sich ein nützlicher Merksatz: **Die Regressionsgerade läuft immer durch den Schwerpunkt $(\bar{x} \mid \bar{y})$ der Datenpunkte.** Das eignet sich hervorragend als Plausibilitätskontrolle: Einfach $\bar{x}$ in die berechnete Regressionsfunktion einsetzen – es muss $\bar{y}$ herauskommen.

{% include check-anker.html nummer="1" %}

### Exkurs: Herleitung der Regressionsformeln

Dieser Abschnitt zeigt, wie die beiden Regressionsformeln entstehen. Er kann beim ersten Lesen übersprungen werden.

Leitet man $S(m,b)=\sum\big(y_i-(m\cdot x_i+b)\big)^2$ nach $b$ ab (bei festem $m$) und setzt die Ableitung gleich null, ergibt sich nach Division durch $-2$ und Ausmultiplizieren die erste Gleichung. Analog liefert das Ableiten nach $m$ (bei festem $b$) die zweite Gleichung:

$$\begin{aligned}
\sum y_i &= m\cdot\sum x_i + n\cdot b \\
\sum x_i y_i &= m\cdot\sum x_i^2 + b\cdot\sum x_i
\end{aligned}$$

Das ist ein lineares Gleichungssystem mit den Unbekannten $m$ und $b$ – die sogenannten **Normalengleichungen**. Teilt man die erste Gleichung durch die Anzahl $n$ der Datenpunkte, entstehen auf beiden Seiten Mittelwerte:

$$\bar{y}=m\cdot\bar{x}+b \qquad\Longrightarrow\qquad b=\bar{y}-m\cdot\bar{x}$$

Das ist bereits die $b$-Formel – und gleichzeitig die Schwerpunkt-Gleichung: Der Punkt $(\bar{x} \mid \bar{y})$ erfüllt die Geradengleichung. Setzt man diesen Ausdruck für $b$ in die zweite Gleichung ein und nutzt $\sum x_i=n\cdot\bar{x}$ sowie $\sum y_i=n\cdot\bar{y}$, kann man nach $m$ auflösen:

$$\begin{aligned}
\sum x_i y_i &= m\cdot\sum x_i^2 + (\bar{y}-m\cdot\bar{x})\cdot\sum x_i \\
\sum x_i y_i - n\cdot\bar{x}\bar{y} &= m\cdot\Big(\sum x_i^2 - n\cdot\bar{x}^2\Big) \\
m &= \frac{\sum x_i y_i - n\cdot\bar{x}\bar{y}}{\sum x_i^2 - n\cdot\bar{x}^2}
\end{aligned}$$

Zähler und Nenner stimmen mit der Summenform der Leitformel überein, denn durch Ausmultiplizieren zeigt man:

$$\begin{aligned}
\sum (x_i-\bar{x})(y_i-\bar{y}) &= \sum x_i y_i - \bar{y}\cdot\sum x_i - \bar{x}\cdot\sum y_i + n\cdot\bar{x}\bar{y} = \sum x_i y_i - n\cdot\bar{x}\bar{y} \\
\sum (x_i-\bar{x})^2 &= \sum x_i^2 - 2\bar{x}\cdot\sum x_i + n\cdot\bar{x}^2 = \sum x_i^2 - n\cdot\bar{x}^2
\end{aligned}$$

Damit sind beide Regressionsformeln hergeleitet.

## Weitere Regressionsfunktionen

Die gleiche Methode funktioniert auch für andere Funktionstypen. Beim quadratischen Ansatz $f(x)=ax^2+bx+c$ lautet die Abweichungssumme

$$S(a,b,c)=\sum_{i=1}^{n}\big(y_i-(a x_i^2+b x_i+c)\big)^2.$$

Sie hängt jetzt von drei Koeffizienten ab. Das Rezept bleibt dasselbe: $S$ wird nacheinander als Funktion jeweils eines Koeffizienten betrachtet (die anderen beiden festgehalten), abgeleitet und die Ableitung gleich null gesetzt. Drei Koeffizienten liefern drei Gleichungen – die Normalengleichungen für den quadratischen Ansatz:

$$\begin{aligned}
a\cdot\sum x_i^4 + b\cdot\sum x_i^3 + c\cdot\sum x_i^2 &= \sum x_i^2\, y_i \\
a\cdot\sum x_i^3 + b\cdot\sum x_i^2 + c\cdot\sum x_i &= \sum x_i\, y_i \\
a\cdot\sum x_i^2 + b\cdot\sum x_i + c\cdot n &= \sum y_i
\end{aligned}$$

Alle Summen sind konkrete Zahlen, die sich direkt aus der Wertetabelle berechnen lassen. Es entsteht also ein lineares 3×3-Gleichungssystem in den Unbekannten $a$, $b$ und $c$. Dieses LGS kann mit dem GTR oder dem Gauß-Algorithmus gelöst werden – von Hand muss hier niemand rechnen. Beim kubischen Ansatz $f(x)=ax^3+bx^2+cx+d$ läuft alles analog: vier Koeffizienten, vier Normalengleichungen, ein 4×4-LGS (mit Summen bis $\sum x_i^6$).

Obwohl die Regressionsfunktionen quadratisch oder kubisch sind, entsteht beim Ableiten **immer ein lineares Gleichungssystem**. Der Grund: Die gesuchten Koeffizienten gehen linear in den Ansatz ein, sie werden nur mit festen Zahlen wie $x_i^2$ oder $x_i^3$ multipliziert und aufaddiert. Ob der Graph gekrümmt ist, spielt für die Struktur der Gleichungen keine Rolle.

Im zugehörigen Check treten lineare, quadratische und kubische Ansätze gemischt auf. Beim linearen Ansatz hast du die Wahl: entweder direkt die Regressionsformeln aus dem vorigen Abschnitt anwenden oder das 2×2-LGS der beiden Normalengleichungen (siehe Exkurs) aufstellen und lösen.

{% include check-anker.html nummer="2" %}

## Regression im Sachzusammenhang

In Anwendungsaufgaben ist die Regressionsfunktion selten das Endziel – sie ist das Werkzeug, mit dem Sachfragen beantwortet werden. Typisch ist ein Dreischritt:

1. **Regressionsfunktion bestimmen:** Zum vorgegebenen Funktionstyp die Koeffizienten berechnen – mit den Regressionsformeln oder über das LGS (das der GTR lösen darf).
2. **Prognose:** Einen gegebenen x-Wert (z. B. einen zukünftigen Zeitpunkt) in die Regressionsfunktion einsetzen; der Funktionswert ist der prognostizierte y-Wert.
3. **Umkehrfrage:** Gesucht ist der x-Wert, zu dem ein vorgegebener y-Wert gehört. Dazu wird die Gleichung $f(x)=y$ gelöst. Bei quadratischen Modellen entstehen dabei in der Regel zwei Lösungen – hier muss im Sachkontext entschieden werden, welche Lösung zur Frage passt (etwa: liegt der gesuchte Zeitpunkt in der steigenden oder in der fallenden Phase?).

Hinweis: Eine Regressionsfunktion beschreibt die Daten in dem Bereich, in dem gemessen wurde. Je weiter eine Prognose diesen Datenbereich verlässt (sogenannte Extrapolation), desto unzuverlässiger wird sie. Ein Modell, das die ersten Monate gut beschreibt, weiß nichts über plötzliche Trendwechsel, Sättigungseffekte oder Ereignisse weit in der Zukunft. Es lohnt sich also immer zu fragen, ob ein prognostizierter Wert im Sachkontext überhaupt noch plausibel ist.

{% include check-anker.html nummer="3" %}

## Regression mit dem GTR

Alle bisherigen Rechenschritte erledigt auch der GTR auf Knopfdruck: Daten eingeben, Regressionsart wählen, Koeffizienten ablesen. Jetzt weißt du, was dabei intern passiert – der GTR bestimmt genau die Funktion, für die die Summe der Abweichungsquadrate minimal wird. Der GTR kann dabei sogar mehr als der LGS-Ansatz: Bei einer exponentiellen Regression mit dem Ansatz $f(x)=a\cdot e^{bx}$ geht der Parameter $b$ nicht linear in den Ansatz ein, deshalb führt das Ableiten hier auf kein lineares Gleichungssystem – die exponentielle Regression lässt sich also nicht direkt über ein LGS bestimmen, der GTR liefert trotzdem eine Lösung.

Zum Schluss stellt sich die Frage, wie gut die gefundene Funktion die Daten beschreibt. Dafür wird in der Regel das Bestimmtheitsmaß $R^2$ verwendet. Es nimmt Werte zwischen 0 und 1 an. Je näher $R^2$ an 1 liegt, desto besser passt die gewählte Funktion zu den Daten. Auch dieser Wert wird direkt vom GTR angegeben. Vereinfacht gesagt ist die Regression für

- $R^2>0{,}9$ gut bis sehr gut,
- $0{,}7< R^2<0{,}9$ akzeptabel,
- $R^2< 0{,}7$ schwach.

Im folgenden verwenden wir den [Casio fx-CG 20](https://www.casio-schulrechner.de/materialdatenbanken/data/Kurzanleitung_FX-CG20V2.pdf "Anleitung"). Andere Taschenrechner funktionieren ähnlich, z.B. der [Casio fx-CP400](https://www.casio-schulrechner.de/materialdatenbanken/data/Hilfekatalog%20Classpad%20400%20Sekundarstufe%20I.pdf "Anleitung").

### Beispiel: Lineare Regression

Gegeben sind folgende Werte:

| x   | 0,5   | 1,5   | 2,5  | 3,5  | 4,5  |
| y   | -2,67 | -0,77 | 0,81 | 2,39 | 4,24 |

{% include graph.html
	funktionen='[]'
	punkte='[
	 {"x":0.5,"y":-2.67,"text":"Messpunkt 1"},
	 {"x":1.5,"y":-0.77,"text":"Messpunkt 2"},
	 {"x":2.5,"y":0.81,"text":"Messpunkt 3"},
	 {"x":3.5,"y":2.39,"text":"Messpunkt 4"},
	 {"x":4.5,"y":4.24,"text":"Messpunkt 5"}
	]'
	xachse="x"
	yachse="y"
	xmin=0
	xmax=5
	ymin=-4
	ymax=5
%}

Wir vermuten, dass die Datenpunkte in etwa auf einer Geraden liegen, daher wird mit dem GTR eine lineare Regression durchgeführt:

- Menü 2 (Statistik) auswählen
- in List1 und List2 die x- und y-Werte der Datenpunkte eingeben
- Graph1 wählen um Datenpunkte anzeigen zu lassen
- CALC wählen und Regressionsart festlegen (hier: $X$ für eine lineare Regression)
- evtl.: Regressionsfunktion präzisieren (hier kann einfach $ax+b$ gewählt werden)
- im Anschluss werden die Parameter der Regressionsfunktion angezeigt (hier $a=1{,}70$ und $b=-3{,}45$)
- DRAW zeigt die Datenpunkte und den Graphen der Regressionsfunktion an
- Die Regressionsfunktion lautet also $f(x)=1{,}70x-3{,}45$.
- Das Bestimmtheitsmaß lautet $R^2=0{,}999$. Dieser Wert liegt sehr nah an $1$, die lineare Regression ist also gut geeignet, um den Zusammenhang zwischen den beiden Größen zu beschreiben.

### Beispiel: Quadratische Regression

Gegeben sind folgende Werte:

| x   | -7     | -3     | 1    | 6    | 11     |
| y   | -47,24 | -14,85 | 5,83 | 2,42 | -34,33 |

{% include graph.html
	funktionen='[]'
	punkte='[
	 {"x":-7,"y":-47.24,"text":"Messpunkt 1"},
	 {"x":-3,"y":-14.85,"text":"Messpunkt 2"},
	 {"x":1,"y":5.83,"text":"Messpunkt 3"},
	 {"x":6,"y":2.42,"text":"Messpunkt 4"},
	 {"x":11,"y":-34.33,"text":"Messpunkt 5"}
	]'
	xachse="x"
	yachse="y"
	xmin=-8
	xmax=12
	ymin=-50
	ymax=10
%}

Wir vermuten, dass die Datenpunkte in etwa auf einer Parabel liegen, daher wird mit dem GTR eine quadratische Regression durchgeführt:

- Menü 2 (Statistik) auswählen
- in List1 und List2 die x- und y-Werte der Datenpunkte eingeben
- Graph1 wählen um Datenpunkte anzeigen zu lassen
- CALC wählen und Regressionsart festlegen (hier: $X^2$ für eine quadratische Regression)
- evtl.: Regressionsfunktion präzisieren (hier gibt es keine Auswahl)
- im Anschluss werden die Parameter der Regressionsfunktion angezeigt (hier $a=-0{,}59$, $b=3{,}20$ und $c=2{,}74$)
- DRAW zeigt die Datenpunkte und den Graphen der Regressionsfunktion an
- Die Regressionsfunktion lautet also $f(x)=-0{,}59x^2+3{,}20x+2{,}74$.
- Das Bestimmtheitsmaß lautet $R^2=0{,}994$. Dieser Wert liegt sehr nah an $1$, die quadratische Regression ist also gut geeignet, um den Zusammenhang zwischen den beiden Größen zu beschreiben.



{% include check-anker.html nummer="4" %}


