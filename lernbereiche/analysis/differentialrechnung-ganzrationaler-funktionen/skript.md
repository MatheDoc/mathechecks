---
layout: module
title: Differentialrechnung ganzrationaler Funktionen - Skript
description: Lernbereich Differentialrechnung ganzrationaler Funktionen, Modul Skript.
page_context: Lernbereich
nav: dashboard
body_class: page-module
module_key: skript
published: true
lernbereich: differentialrechnung-ganzrationaler-funktionen
gebiet: analysis
permalink: /lernbereiche/analysis/differentialrechnung-ganzrationaler-funktionen/skript.html
---

## E-Scooter-Fahrt durch die Stadt

Du fährst mit dem E-Scooter durch die Stadt. Mal beschleunigst du auf einer freien Strecke, mal bremst du vor einer Kurve, mal rollst du fast gleichmäßig aus. Mathematisch kann man so eine Fahrt mit einer **Weg-Funktion** beschreiben: Jedem Zeitpunkt wird eine zurückgelegte Strecke zugeordnet.

Sobald wir die Weg-Funktion kennen, tauchen sofort neue Fragen auf:

- Wie schnell warst du im Durchschnitt in einem bestimmten Abschnitt?
- Wie groß war die Geschwindigkeit in genau einem bestimmten Moment?
- Wann wurde die Geschwindigkeit größer, wann kleiner?
- An welcher Stelle war die Geschwindigkeit maximal?

Genau dafür braucht man die Differentialrechnung. Die erste Ableitung beschreibt die **Steigung** des Graphen und im Bewegungskontext die **Geschwindigkeit**. Die zweite Ableitung beschreibt, wie sich diese Steigung verändert, also im Bewegungskontext die **Beschleunigung**.

## Von der Strecke zur Änderungsrate

### Mittlere Änderungsrate

Die mittlere Änderungsrate beschreibt, wie stark sich eine Funktion in einem ganzen Intervall im Durchschnitt verändert. Für eine Funktion $f$ auf dem Intervall $[a;b]$ gilt:

$$m_{[a;b]} = \frac{f(b)-f(a)}{b-a}$$

Der Zähler misst die Änderung des Funktionswerts, der Nenner die Änderung der Stelle. Deshalb ist die mittlere Änderungsrate immer eine Art „Änderung pro Einheit“.

Im Bewegungskontext ist das besonders anschaulich:

- $f(b)-f(a)$ ist die zusätzlich zurückgelegte Strecke,
- $b-a$ ist die dafür benötigte Zeit,
- also ist der Quotient die **durchschnittliche Geschwindigkeit** in diesem Abschnitt.

Eine positive mittlere Änderungsrate bedeutet, dass der Funktionswert im Durchschnitt zunimmt. Eine negative mittlere Änderungsrate bedeutet, dass er im Durchschnitt abnimmt.

Für typische Aufgaben in diesem Lernschritt ist ein fester Ablauf hilfreich: zuerst die beiden Randwerte berechnen, dann in die Formel einsetzen und das Ergebnis als durchschnittliche Änderung im Intervall deuten. Genau diesen Ablauf greifen auch Tipps, Beispiel und Aufgabe am Check-Anker auf.

{% include check-anker.html nummer="1" %}

### Von der mittleren zur momentanen Änderungsrate

Die mittlere Änderungsrate betrachtet immer ein ganzes Intervall. Oft interessiert aber nicht der Durchschnitt über mehrere Sekunden oder Meter, sondern die Änderung **genau an einer Stelle**.

Die Idee ist: Man betrachtet immer kleinere Intervalle um einen Punkt $x_0$. Die mittlere Änderungsrate nähert sich dann einem festen Wert an. Dieser Grenzwert ist die **momentane Änderungsrate** oder **Ableitung** an der Stelle $x_0$.

Die sogenannte **h-Methode** beschreibt genau diesen Übergang. Man startet mit dem Punkt

$$P(x_0 \mid f(x_0))$$

und nimmt einen zweiten Punkt in kleinem Abstand $h$ dazu:

$$Q(x_0+h \mid f(x_0+h)).$$

Dann hat die Sekante durch $P$ und $Q$ die Steigung

$$m_h = \frac{f(x_0+h)-f(x_0)}{h}.$$ 

Wenn $h$ immer kleiner wird, rückt der Punkt $Q$ auf $P$ zu. Im Grenzfall wird aus der Sekante die Tangente.

Graphisch ist das die Steigung der Tangente an den Graphen von $f$ im Punkt $P(x_0 \mid f(x_0))$.

Sauber definiert ist die Ableitung an der Stelle $x_0$ deshalb durch

$$f'(x_0)=\lim_{h \to 0} \frac{f(x_0+h)-f(x_0)}{h}.$$ 

Im Widget ist die Funktion $f(x)=x^2$ fest eingestellt. Du kannst $x_0$ und $h$ verändern und sehen, wie die Sekante zur Tangente wird. Achte dabei auf zwei Dinge: Der Punkt $Q$ rückt an $P$ heran, und gleichzeitig nähert sich die Sekantensteigung $m_h$ einem festen Wert. Genau dieser angenäherte Wert ist die momentane Änderungsrate an der Stelle $x_0$.

{% include widgets/widget-h-methode-ableitung.html %}

Für $f(x)=x^2$ kann man die Ableitung direkt aus der Definition herleiten:

$$\begin{aligned}
f'(x_0) &= \lim_{h \to 0} \frac{f(x_0+h)-f(x_0)}{h} \\
&= \lim_{h \to 0} \frac{(x_0+h)^2-x_0^2}{h} \\
&= \lim_{h \to 0} \frac{x_0^2+2x_0h+h^2-x_0^2}{h} \\
&= \lim_{h \to 0} \frac{2x_0h+h^2}{h} \\
&= \lim_{h \to 0} (2x_0+h) \\
&= 2x_0
\end{aligned}$$

Das gilt an jeder Stelle $x_0$. Ersetzt man $x_0$ wieder durch die allgemeine Variable $x$, erhält man die Ableitungsfunktion

$$f'(x)=2x.$$ 

Für kompliziertere ganzrationale Funktionen wäre dieser Weg jedes Mal möglich, aber unnötig aufwendig. Deshalb arbeiten wir im weiteren Verlauf mit Ableitungsregeln.

### Ableitungsregeln für ganzrationale Funktionen

Ganzrationale Funktionen haben den großen Vorteil, dass ihre Ableitungen wieder ganzrationale Funktionen sind. Für das Ableiten braucht man vor allem drei Regeln:

- **Konstantenregel:** Die Ableitung einer konstanten Zahl ist $0$.
- **Potenzregel:** Aus $x^n$ wird $n \cdot x^{n-1}$.
- **Summenregel:** Eine Summe wird termweise abgeleitet.

In diesem Lernbereich tauchen Terme auch in Produktform auf. Dann ist der erste sinnvolle Schritt oft: **zuerst ausmultiplizieren, dann ableiten**. So landet man wieder bei einer übersichtlichen Normalform.

Genau das ist der Standardfall für den nächsten Check: Die Tipps erinnern an Normalform, Potenzregel und Summenregel, das Beispiel zeigt das Ausmultiplizieren an einem Produktterm, und in den Aufgaben musst du denselben Ablauf auf neue Funktionen übertragen.

{% include check-anker.html nummer="2" %}

### Funktionswerte, Stellen und Tangentensteigungen

Sobald $f$ und $f'$ bekannt sind, kann man sehr gezielt mit ihnen arbeiten:

- Ein **Funktionswert** entsteht durch Einsetzen eines $x$-Werts in $f(x)$.
- Eine **Stelle zu einem gegebenen Funktionswert** erhält man durch Lösen von $f(x)=y_0$.
- Eine **Tangentensteigung** an $x_0$ ist einfach der Wert $f'(x_0)$.
- Eine **Stelle zu einer gegebenen Steigung** findet man durch Lösen von $f'(x)=m$.

Man muss also immer sauber unterscheiden: Geht es um den Wert der Funktion selbst oder um den Wert ihrer Ableitung?

In Aufgaben werden diese Fragetypen oft bewusst gemischt. Manchmal ist nur ein $x$-Wert gesucht, manchmal ein Funktionswert, manchmal die Steigung und manchmal sogar der Punkt des Graphen, an dem eine bestimmte Steigung vorliegt. Im letzten Fall reicht $f'(x)=m$ allein noch nicht: Danach muss auch der zugehörige y-Wert mit $f(x)$ berechnet werden.

Genau diese Unterscheidung trainiert der nächste Check. Die Tipps trennen die vier Standardfälle sauber, das Beispiel rechnet sie nacheinander vor, und die Aufgaben mischen sie anschließend in neuer Reihenfolge.

{% include check-anker.html nummer="3" %}

## Was sagt der Ableitungsgraph?

### Graphische Bedeutung der ersten Ableitung

Zwischen dem Graphen von $f$ und dem Graphen von $f'$ gibt es einen engen Zusammenhang:

- Wo $f'(x)=0$ gilt, hat $f$ eine waagrechte Tangente.
- Wo $f'(x)>0$ gilt, steigt $f$.
- Wo $f'(x)<0$ gilt, fällt $f$.
- Je größer der Betrag $\lvert f'(x) \rvert$ ist, desto steiler verläuft der Graph von $f$.

Deshalb kann man viele Aussagen über $f$ schon am Graphen von $f'$ ablesen, ohne $f$ selbst vollständig berechnet zu haben.

Bei Zuordnungsaufgaben hilft oft ein fester Ablauf:

1. Zuerst auf Nullstellen und Vorzeichen von $f'$ achten.
2. Dann prüfen, welcher Funktionsgraph dazu passt.
3. Zusätzliche Angaben wie $g(0)$ oder $f'(x_0)$ als Anker verwenden.

Gerade solche Zusatzangaben entscheiden oft den ersten Schritt: Sie helfen, einen Graphen sicher zu identifizieren, bevor überhaupt Paare aus Funktion und Ableitung zugeordnet werden. Das Beispiel zum nächsten Check nutzt genau diese Strategie.

{% include check-anker.html nummer="4" %}

### Vom Ableitungsgraphen zurück zur Ausgangsfunktion

Wenn nur der Graph von $f'$ gegeben ist, lassen sich trotzdem wichtige Eigenschaften von $f$ bestimmen.

Für Extremstellen von $f$ schaut man auf die Nullstellen von $f'$:

- Vorzeichenwechsel von $-$ nach $+$: Tiefpunkt von $f$
- Vorzeichenwechsel von $+$ nach $-$: Hochpunkt von $f$

Für Wendestellen von $f$ schaut man auf Extremstellen von $f'$. Warum? An einer Wendestelle ist die Steigung von $f$ lokal besonders groß oder besonders klein. Genau das bedeutet: $f'$ hat dort einen Hochpunkt oder Tiefpunkt.

In solchen Aufgaben werden meist zuerst die **x-Werte** gesucht. Die y-Werte der Punkte müsste man erst mit der Ausgangsfunktion berechnen.

Für den nächsten Check ist genau diese Trennung wichtig: Aus dem Graphen von $f'$ lassen sich zunächst nur Aussagen über die Lage auf der x-Achse und über Vorzeichenwechsel ableiten. Die Tipps und das Beispiel führen deshalb systematisch über Nullstellen, Vorzeichenwechsel und Extremstellen von $f'$ zu Extrem- und Wendestellen von $f$.

{% include check-anker.html nummer="5" %}

## Extrempunkte und Monotonie

### Einfache Extrempunkte bestimmen

Ein Extrempunkt ist ein Hochpunkt oder Tiefpunkt der Funktion. Rechnerisch beginnt man immer mit der **notwendigen Bedingung**:

$$f'(x_0)=0$$

Solche Stellen sind zunächst nur **Kandidaten**. Ob dort wirklich ein Hoch- oder Tiefpunkt vorliegt, entscheidet in einfachen Fällen die zweite Ableitung:

- $f''(x_0)>0$: Tiefpunkt
- $f''(x_0)<0$: Hochpunkt

Ist die Art des Extrempunkts geklärt, gehört zum vollständigen Extrempunkt immer auch der zugehörige y-Wert $f(x_0)$.

Im einfachen Check reicht genau diese Dreischrittlogik: Kandidaten über $f'(x)=0$ bestimmen, die Art über $f''$ entscheiden und danach den Punkt mit $f(x)$ vervollständigen. Beispiel und Aufgaben bleiben dabei bewusst noch ohne Spezialfälle mit $f''(x_0)=0$.

{% include check-anker.html nummer="6" %}

### Monotonieintervalle mit der ersten Ableitung

Monotonie bedeutet: Eine Funktion steigt oder fällt auf einem Intervall durchgehend.

Das Vorzeichen von $f'$ liefert dafür den direkten Test:

- $f'(x)>0$: $f$ ist streng monoton wachsend
- $f'(x)<0$: $f$ ist streng monoton fallend

Praktisch geht man so vor:

1. Nullstellen von $f'$ bestimmen.
2. Diese Stellen zerlegen die Zahlengerade in Intervalle.
3. In jedem Intervall das Vorzeichen von $f'$ prüfen.
4. Aus dem Vorzeichen die Monotonie folgern.

Damit entsteht bereits die Grundidee der **Vorzeichentabelle**.

Genau dieses Schema greift der nächste Check auf: Die Nullstellen von $f'$ liefern die Intervallgrenzen, und erst danach wird jedes Intervall über das Vorzeichen von $f'$ gedeutet.

{% include check-anker.html nummer="7" %}

### Spezialfall bei Extremstellen: Auch die zweite Ableitung ist $0$

Manchmal klappt der übliche Test nicht. Dann gilt an einer Kandidatenstelle gleichzeitig

$$f'(x_0)=0 \quad\text{und}\quad f''(x_0)=0.$$

Dann ist die zweite Ableitung **nicht entscheidend**. Jetzt muss man direkt auf den Vorzeichenwechsel von $f'$ links und rechts von $x_0$ schauen.

Eine typische Vorzeichentabelle sieht dann so aus:

| Bereich | links von $x_0$ | bei $x_0$ | rechts von $x_0$ |
|---|---|---|---|
| Beispielwert in $f'$ | positiv oder negativ | $0$ | positiv oder negativ |
| Vorzeichen von $f'$ | $+$ oder $-$ | $0$ | $+$ oder $-$ |
| Folgerung | steigend/fallend | waagrechte Tangente | steigend/fallend |

Entscheidend ist nur die letzte Frage:

- **mit Vorzeichenwechsel**: echte Extremstelle
- **ohne Vorzeichenwechsel**: kein Extrempunkt

Wenn die Tangente waagrecht ist, aber kein Extrempunkt vorliegt, kann ein **Sattelpunkt** entstehen.

Im nächsten Check sind genau solche Fälle zentral. Die Tipps lenken deshalb auf den Vorzeichenwechsel von $f'$ links und rechts der Kandidatenstelle, und das Beispiel verbindet diese Entscheidung ausdrücklich mit Vorzeichentabelle und Graph von $f'$.

{% include check-anker.html nummer="8" %}

## Wendestellen und Krümmung

### Wendestellen als Stellen maximaler oder minimaler Steigung

An einer Wendestelle wechselt die Krümmung des Graphen. Gleichzeitig passiert dort noch etwas anderes: Die Steigung ist lokal besonders groß oder besonders klein.

Deshalb beginnt die Suche nach Wendestellen mit der zweiten Ableitung:

$$f''(x_0)=0$$

Das ist wieder nur die notwendige Bedingung. In einfachen Fällen genügt dann die dritte Ableitung als Entscheidungshilfe:

$$f'''(x_0) \neq 0.$$

Ist das erfüllt, liegt tatsächlich eine Wendestelle vor. Zusätzlich kann man dann inhaltlich deuten:

- Wechsel von rechtsgekrümmt nach linksgekrümmt: minimale Steigung
- Wechsel von linksgekrümmt nach rechtsgekrümmt: maximale Steigung

Im zugehörigen Check sind meist zuerst die **x-Werte** der Wendestellen gefragt. Der y-Wert hilft beim geometrischen Verständnis des Punkts, gehört aber oft noch nicht zur eigentlichen Antwort.

{% include check-anker.html nummer="9" %}

### Krümmungsintervalle über das Vorzeichen von $f''$

So wie $f'$ die Monotonie steuert, steuert $f''$ die Krümmung:

- $f''(x)>0$: linksgekrümmt bzw. konvex
- $f''(x)<0$: rechtsgekrümmt bzw. konkav

Auch hier ist das Vorgehen analog:

1. Nullstellen von $f''$ bestimmen.
2. Die Zahlengerade dadurch in Intervalle zerlegen.
3. In jedem Intervall das Vorzeichen von $f''$ prüfen.
4. Daraus die Krümmung folgern.

Damit sind Monotonie und Krümmung didaktisch parallel aufgebaut: erst Kandidaten bestimmen, dann über Vorzeichen argumentieren.

Genau diese Parallelität nutzt der nächste Check. Wer Monotonieintervalle über $f'$ schon sicher untersucht, kann Krümmungsintervalle mit derselben Struktur über $f''$ bestimmen.

{% include check-anker.html nummer="10" %}

### Spezialfall bei Wendestellen: $f''(x_0)=0$ und $f'''(x_0)=0$

Auch bei Wendestellen gibt es schwierige Fälle. Wenn an einer Kandidatenstelle zusätzlich noch $f'''(x_0)=0$ gilt, ist die dritte Ableitung nicht hilfreich.

Dann gilt wieder dasselbe Prinzip wie bei den Extremstellen: **Nicht die formale Ableitung entscheidet, sondern der Vorzeichenwechsel.**

Diesmal schaut man auf $f''$ links und rechts von $x_0$:

- mit Vorzeichenwechsel: echte Wendestelle
- ohne Vorzeichenwechsel: keine Wendestelle

Auch dafür ist eine Vorzeichentabelle das sauberste Werkzeug. Man trägt Teststellen, Vorzeichen und die Folgerung zur Krümmung systematisch ein.

Im nächsten Check entscheidet also nicht die bloße Gleichung $f''(x_0)=0$, sondern der tatsächliche Vorzeichenwechsel von $f''$. Genau darauf richten Tipps, Beispiel und Aufgabe den Blick.

{% include check-anker.html nummer="11" %}

## Lokale und globale Aussagen

### Globale Extremwerte auf Intervallen

Lokale Extrempunkte sind noch keine globalen Extremwerte. Eine Funktion kann lokal einen Hochpunkt haben und trotzdem an einem Randpunkt oder für große $x$ noch größere Werte annehmen.

Für **globale** Extremwerte auf einem Intervall müssen deshalb alle Kandidaten verglichen werden:

- lokale Extremstellen im Inneren des Intervalls,
- Randpunkte des Intervalls,
- bei unbeschränkten Intervallen zusätzlich das Verhalten für $x \to \pm\infty$.

Erst der Vergleich der Funktionswerte entscheidet:

- größter Wert: globales Maximum
- kleinster Wert: globales Minimum

Wichtig ist auch: Auf unbeschränkten Intervallen kann es vorkommen, dass nur eines der beiden globalen Extrema existiert oder sogar keines.

Im nächsten Check müssen deshalb innere Kandidaten, Randpunkte und gegebenenfalls das Verhalten für $x\to\pm\infty$ immer gemeinsam betrachtet werden. Erst danach steht fest, ob ein globales Maximum oder Minimum wirklich existiert.

{% include check-anker.html nummer="12" %}

### Wo ist die Steigung am größten oder am kleinsten?

Jetzt wird nicht mehr $f(x)$ selbst optimiert, sondern die **Steigung**, also $f'(x)$.

Die Frage lautet also in Wahrheit: Wo hat die Funktion $f'$ auf dem betrachteten Intervall ein globales Maximum oder Minimum?

Die Kandidatenlogik bleibt dieselbe:

- innere Kandidaten: Stellen, an denen $f''(x)=0$ und damit die Steigung lokal maximal oder minimal sein kann,
- Randpunkte des Intervalls,
- bei unbeschränkten Intervallen zusätzlich das Verhalten von $f'(x)$ für $x \to \pm\infty$.

Didaktisch ist das ein wichtiger Perspektivwechsel: Man untersucht weiter dieselbe Funktion $f$, aber die Größe, die verglichen wird, ist jetzt **nicht** der Funktionswert, sondern der Wert der Ableitung.

Genau darauf zielt der nächste Check. Das Beispiel vergleicht deshalb ausdrücklich Werte von $f'$ an inneren Kandidaten und Randpunkten, und die Aufgaben variieren dann nur Funktion und Intervall.

{% include check-anker.html nummer="13" %}

## Steckbriefaufgaben für kubische Funktionen

Bei Steckbriefaufgaben ist die Funktionsgleichung nicht gegeben, sondern soll aus Bedingungen erst aufgebaut werden. Für kubische Funktionen startet man mit der allgemeinen Form

$$f(x)=ax^3+bx^2+cx+d.$$

Danach werden die gegebenen Informationen in Gleichungen übersetzt.

Typische Bedingungen sind:

- **Punktbedingung:** Ein Punkt $P(x_P \mid y_P)$ liegt auf dem Graphen, also $f(x_P)=y_P$.
- **Extrempunktbedingung:** Bei $E(x_E \mid y_E)$ gilt $f(x_E)=y_E$ und $f'(x_E)=0$.
- **Wendepunktbedingung:** Bei $W(x_W \mid y_W)$ gilt $f(x_W)=y_W$ und $f''(x_W)=0$.

So entsteht ein lineares Gleichungssystem für $a$, $b$, $c$ und $d$. Der Schwerpunkt liegt dabei auf dem **sauberen Aufstellen der Bedingungen**. Das Lösen des Systems kann anschließend mit dem Taschenrechner oder mit dem Gauß-Algorithmus erfolgen.

Wenn zusätzlich „Hochpunkt“ oder „Tiefpunkt“ angegeben ist, dient das als Plausibilitätskontrolle für die gefundene Funktion.

Im nächsten Check steht deshalb vor allem das präzise Übersetzen der Punkt- und Ableitungsinformationen in vier Gleichungen für $a$, $b$, $c$ und $d$ im Mittelpunkt. Das Beispiel zeigt diesen Aufbau vollständig; in den Aufgaben ändern sich anschließend nur die konkreten Daten.

{% include check-anker.html nummer="14" %}

## Zurück zur E-Scooter-Fahrt

Jetzt lässt sich die Ausgangsfrage präzise beantworten: Aus der Weg-Funktion gewinnt man durch Ableiten die Geschwindigkeitsfunktion. Wer wissen will, wo die Fahrt am schnellsten war, sucht also nicht den Hochpunkt des Weggraphen, sondern das **globale Maximum der Geschwindigkeitsfunktion** auf dem betrachteten Zeitintervall.

Damit greifen die Bausteine dieses Lernbereichs ineinander:

- mittlere Änderungsrate für den Durchschnitt,
- erste Ableitung für momentane Geschwindigkeit,
- zweite Ableitung für die Veränderung der Steigung,
- Extremstellen, Monotonie, Wendestellen und Krümmung für die qualitative Analyse,
- globale Betrachtungen für die eigentliche Entscheidungsfrage.

Genau deshalb ist die Differentialrechnung mehr als nur „ableiten können“: Sie übersetzt einen Funktionsterm in Aussagen über Verhalten, Bewegung und Struktur.


