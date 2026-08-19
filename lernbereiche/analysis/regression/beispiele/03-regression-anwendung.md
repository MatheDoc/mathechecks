---
layout: null
permalink: /lernbereiche/analysis/regression/beispiele/03-regression-anwendung.html
---
Nach der Einnahme eines Medikaments wird die Wirkstoffkonzentration im Blut gemessen ($t$: Stunden nach der Einnahme, Konzentration in mg/l):

| Stunde $t$           | 0    | 2    | 4    | 6    |
| Konzentration (mg/l) | 0,75 | 7,75 | 8,25 | 7,25 |

Die Daten sollen durch eine quadratische Regressionsfunktion mit dem Ansatz $K(t)=at^2+bt+c$ modelliert werden.

a) Bestimmen Sie die quadratische Regressionsfunktion.

b) Prognostizieren Sie mit dem Modell die Konzentration 7 Stunden nach der Einnahme.

c) Die Wirkung lässt spürbar nach, sobald die Konzentration unter 7 mg/l fällt. Ab welchem Zeitpunkt ist das nach dem Modell der Fall?

**Lösung zu a): Regressionsfunktion bestimmen**

Für die Normalengleichungen des quadratischen Ansatzes werden die folgenden Summen berechnet:

| $\sum t_i$ | $\sum t_i^2$ | $\sum t_i^3$ | $\sum t_i^4$ | $\sum y_i$ | $\sum t_i y_i$ | $\sum t_i^2 y_i$ |
| $12$ | $56$ | $288$ | $1568$ | $24$ | $92$ | $424$ |

Mit $n=4$ Datenpunkten lautet das 3×3-Gleichungssystem:

$$\begin{aligned}
1568a+288b+56c &= 424 \\
288a+56b+12c &= 92 \\
56a+12b+4c &= 24
\end{aligned}$$

Dieses LGS kann mit dem GTR oder dem Gauß-Algorithmus gelöst werden. Die Lösung lautet $a=-0{,}5$, $b=4$ und $c=1$, also

$$K(t)=-0{,}5t^2+4t+1.$$

{% include graph.html
	funktionen='[{"name":"K", "term":"-0.5*x^2+4*x+1", "color":"#4363d8"}]'
	punkte='[
	 {"x":0,"y":0.75,"text":"Messpunkt 1"},
	 {"x":2,"y":7.75,"text":"Messpunkt 2"},
	 {"x":4,"y":8.25,"text":"Messpunkt 3"},
	 {"x":6,"y":7.25,"text":"Messpunkt 4"}
	]'
	xachse="t (Stunden)"
	yachse="Konzentration (mg/l)"
	xmin=0
	xmax=9
	ymin=0
	ymax=10
%}

**Lösung zu b): Prognose (t-Wert einsetzen)**

Für die Prognose wird $t=7$ in die Regressionsfunktion eingesetzt:

$$K(7)=-0{,}5\cdot 7^2+4\cdot 7+1=-24{,}5+28+1=4{,}5$$

Nach dem Modell beträgt die Konzentration 7 Stunden nach der Einnahme 4,5 mg/l.

**Lösung zu c): Umkehrfrage (Gleichung lösen)**

Gesucht ist der Zeitpunkt, ab dem die Konzentration unter 7 mg/l fällt. Dazu wird zunächst die Gleichung $K(t)=7$ gelöst:

$$\begin{aligned}
-0{,}5t^2+4t+1 &= 7 \\
t^2-8t+12 &= 0 \\
t_{1} = 2, \qquad t_{2} &= 6
\end{aligned}$$

Die Gleichung hat zwei Lösungen, weil die Parabel den Wert 7 mg/l zweimal annimmt: bei $t_1=2$ in der steigenden Phase (die Konzentration baut sich noch auf) und bei $t_2=6$ in der fallenden Phase. Gefragt ist, ab wann die Konzentration *unter* 7 mg/l fällt – das passiert in der fallenden Phase, also ist $t_2=6$ die im Sachkontext passende Lösung: Ab etwa 6 Stunden nach der Einnahme lässt die Wirkung spürbar nach.

**Hinweis zu den Grenzen des Modells:** Für $t>8{,}2$ liefert die Regressionsfunktion negative Konzentrationen – das ist im Sachkontext unmöglich. Das Modell beschreibt die Daten im gemessenen Bereich gut, taugt aber nicht für Prognosen weit darüber hinaus.
