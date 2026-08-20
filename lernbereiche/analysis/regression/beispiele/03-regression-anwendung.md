---
layout: null
permalink: /lernbereiche/analysis/regression/beispiele/03-regression-anwendung.html
---
Nach der Einnahme eines Medikaments wird die Wirkstoffkonzentration im Blut gemessen ($t$: Stunden nach der Einnahme, Konzentration in mg/l):

| Stunde $t$           | 0 | 2  | 4  | 6  |
| Konzentration (mg/l) | 0 | 28 | 30 | 26 |

Die Daten sollen durch eine quadratische Regressionsfunktion mit dem Ansatz $K(t)=at^2+bt+c$ modelliert werden.

a) Bestimmen Sie die quadratische Regressionsfunktion.

b) Prognostizieren Sie mit dem Modell die Konzentration 7 Stunden nach der Einnahme.

c) Die Wirkung lässt spürbar nach, sobald die Konzentration unter 25 mg/l fällt. Ab welchem Zeitpunkt ist das nach dem Modell der Fall?

**Lösung zu a): Regressionsfunktion bestimmen**

Zunächst wird die Abweichungssumme aufgestellt – für jeden Datenpunkt die quadrierte Abweichung zwischen Messwert und Funktionswert:

$$\begin{aligned}
S(a,b,c)=\;&\big(0-(a\cdot 0^2+b\cdot 0+c)\big)^2+\big(28-(a\cdot 2^2+b\cdot 2+c)\big)^2 \\
+\;&\big(30-(a\cdot 4^2+b\cdot 4+c)\big)^2+\big(26-(a\cdot 6^2+b\cdot 6+c)\big)^2
\end{aligned}$$

Für das Minimum wird $S$ nacheinander als Funktion jeweils eines Koeffizienten aufgefasst, abgeleitet und die Ableitung gleich null gesetzt:

$$S'_{b,c}(a)=0, \qquad S'_{a,c}(b)=0, \qquad S'_{a,b}(c)=0$$

<!--$$\begin{aligned}
1568a+288b+56c &= 1528 \\
288a+56b+12c &= 332 \\
56a+12b+4c &= 84
\end{aligned}$$-->

Dieses LGS kann mit dem GTR oder dem Gauß-Algorithmus gelöst werden. Die Lösung lautet $a=-2$, $b=16$ und $c=1$, also

$$K(t)=-2t^2+16t+1.$$

{% include graph.html
	funktionen='[{"name":"K", "term":"-2*x^2+16*x+1", "color":"#4363d8"}]'
	punkte='[
	 {"x":0,"y":0,"text":"Messpunkt 1"},
	 {"x":2,"y":28,"text":"Messpunkt 2"},
	 {"x":4,"y":30,"text":"Messpunkt 3"},
	 {"x":6,"y":26,"text":"Messpunkt 4"}
	]'
	xachse="t (Stunden)"
	yachse="Konzentration (mg/l)"
	xmin=0
	xmax=9
	ymin=0
	ymax=35
%}

**Lösung zu b): Prognose (t-Wert einsetzen)**

Für die Prognose wird $t=7$ in die Regressionsfunktion eingesetzt:

$$K(7)=-2\cdot 7^2+16\cdot 7+1=-98+112+1=15$$

Nach dem Modell beträgt die Konzentration 7 Stunden nach der Einnahme 15 mg/l.

**Lösung zu c): Umkehrfrage (Gleichung lösen)**

Gesucht ist der Zeitpunkt, ab dem die Konzentration unter 25 mg/l fällt. Dazu wird zunächst die Gleichung $K(t)=25$ gelöst:

$$\begin{aligned}
-2t^2+16t+1 &= 25 \\
t^2-8t+12 &= 0 \\
t_{1} = 2, \qquad t_{2} &= 6
\end{aligned}$$

Die Gleichung hat zwei Lösungen, weil die Parabel den Wert 25 mg/l zweimal annimmt: bei $t_1=2$ in der steigenden Phase (die Konzentration baut sich noch auf) und bei $t_2=6$ in der fallenden Phase. Gefragt ist, ab wann die Konzentration *unter* 25 mg/l fällt – das passiert in der fallenden Phase, also ist $t_2=6$ die im Sachkontext passende Lösung: Ab etwa 6 Stunden nach der Einnahme lässt die Wirkung spürbar nach.

**Hinweis zu den Grenzen des Modells:** Für $t>8{,}1$ liefert die Regressionsfunktion negative Konzentrationen – das ist im Sachkontext unmöglich. Das Modell beschreibt die Daten im gemessenen Bereich gut, taugt aber nicht für Prognosen weit darüber hinaus.
