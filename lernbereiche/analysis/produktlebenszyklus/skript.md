---
layout: module
title: "Produktlebenszyklus erklärt – Absatz, Kennzahlen und Gesamtabsatz"
description: "Produktlebenszyklus mathematisch erklärt: Phasen, Kennzahlen graphisch und rechnerisch bestimmen, Gesamtabsatz als Fläche unter dem Graphen deuten und mit Integralen berechnen."
page_context: Lernbereich
nav: dashboard
body_class: page-module
module_key: skript
published: true
lernbereich: produktlebenszyklus
gebiet: analysis
permalink: /lernbereiche/analysis/produktlebenszyklus/skript.html
---

# Produktlebenszyklus: Absatz und Gesamtabsatz eines Produkts

## Einführung

Ein Hersteller bringt eine neue Spielkonsole auf den Markt. Die Marketingabteilung erwartet, dass sich der monatliche Absatz gemäß

$$
a(t)=(t^2+t-4)\cdot e^{-0{,}25t}+4
$$

entwickelt. Dabei ist $t$ die Zeit in Monaten seit der Markteinführung und $a(t)$ der Absatz in Mengeneinheiten pro Monat (ME/Monat), 1 ME entspricht 1000 Konsolen.

Wichtig ist die Einheit: $a(t)$ ist kein Bestand, sondern eine **Rate**. $a(4)\approx 9{,}89$ bedeutet: Vier Monate nach der Markteinführung werden ca. $9\,890$ Konsolen *pro Monat* verkauft. Wie viele Konsolen insgesamt verkauft wurden, klären wir erst im Abschnitt zum Gesamtabsatz.

Typisch für einen Produktlebenszyklus ist der Verlauf: Der Absatz steigt zunächst immer schneller, dann langsamer, erreicht ein Maximum und geht anschließend zurück. Die Wendepunkte und der Hochpunkt teilen den Verlauf in vier Phasen:

{% include graph.html
   funktionen='[
    {"name":"a(t)", "term":"(x^2+x-4)*exp(-0.25*x)+4", "beschreibung":"monatlicher Absatz der Spielkonsole"},
    {"name":"y = 4", "term":"4+0*x", "beschreibung":"langfristiger Absatz", "dash":"dash", "color":"#888888"}
   ]'
   flaechen='[
    {"term":"(x^2+x-4)*exp(-0.25*x)+4", "von":0, "bis":1.48, "farbe":"rgba(46,160,67,0.25)", "name":"Einführung"},
    {"term":"(x^2+x-4)*exp(-0.25*x)+4", "von":1.48, "bis":8, "farbe":"rgba(31,119,180,0.25)", "name":"Wachstum"},
    {"term":"(x^2+x-4)*exp(-0.25*x)+4", "von":8, "bis":13.52, "farbe":"rgba(255,165,0,0.25)", "name":"Sättigung"},
    {"term":"(x^2+x-4)*exp(-0.25*x)+4", "von":13.52, "bis":30, "farbe":"rgba(214,39,40,0.2)", "name":"Rückgang"}
   ]'
   punkte='[
     {"x":1.48,"y":3.77,"text":"1. Wendepunkt: stärkster Anstieg"},
     {"x":8,"y":13.2,"text":"Hochpunkt: höchster Absatz"},
     {"x":13.52,"y":10.55,"text":"2. Wendepunkt: stärkster Rückgang"}
   ]'
   titel="Phasen im Produktlebenszyklus der Spielkonsole"
   xachse="Zeit t in Monaten"
   yachse="Absatz in ME/Monat"
   xmin=0
   xmax=30
   ymin=0
   ymax=15
%}

| Phase | Zeitraum | Verlauf des Absatzes | Graph von $a$ |
|---|---|---|---|
| Einführung | bis zum 1. Wendepunkt ($t\approx 1{,}48$) | steigt immer schneller (**progressiv**) | steigend, linksgekrümmt |
| Wachstum | bis zum Hochpunkt ($t=8$) | steigt immer langsamer (**degressiv**) | steigend, rechtsgekrümmt |
| Sättigung | bis zum 2. Wendepunkt ($t\approx 13{,}52$) | sinkt immer schneller | fallend, rechtsgekrümmt |
| Rückgang | danach | sinkt immer langsamer | fallend, linksgekrümmt |

Die Namen und Grenzen der Phasen werden in der Literatur nicht einheitlich verwendet. In Aufgaben kommt es auf die zugehörigen **Kennzahlen** an, die wir im Folgenden graphisch und rechnerisch bestimmen.

Statt des Absatzes (ME pro Monat) wird manchmal der **Umsatz** (GE pro Jahr) betrachtet, meist mit $u(t)$ bezeichnet. Die Mathematik bleibt dieselbe, nur die Einheiten und Formulierungen ändern sich.

### Funktionstyp und Ende des Zyklus

Produktlebenszyklusfunktionen sind meist ein Produkt aus einem Polynom $p(t)$ und einer fallenden $e$-Funktion, eventuell mit einem konstanten Summanden $d\ge 0$:

$$
a(t)=p(t)\cdot e^{-ct}+d \qquad (c>0)
$$

Da $e^{-ct}$ für große $t$ schneller gegen $0$ geht, als jedes Polynom wächst, gilt $p(t)\cdot e^{-ct}\to 0$. Daraus ergeben sich zwei Arten, wie der Zyklus endet:

- **Langfristiger Absatz** ($d>0$): Der Absatz nähert sich dem Wert $d$, es gilt $\lim\limits_{t\to\infty} a(t)=d$. Der Graph hat die waagrechte Asymptote $y=d$. Bei der Spielkonsole ist $d=4$: Auch langfristig werden ca. $4\,000$ Konsolen pro Monat verkauft. Der Startwert $a(0)=0$ hat damit nichts zu tun – er hängt auch vom Polynom $p$ ab: $a(0)=p(0)+d=-4+4$.
- **Marktaustritt** ($d=0$ und $p$ hat eine positive Nullstelle $T$): Der Absatz sinkt bei $t=T$ auf null, das Produkt wird vom Markt genommen. Danach ist das Modell nicht mehr sinnvoll.

## Kennzahlen graphisch bestimmen

### Der Graph der Absatzfunktion

Die Kennzahlen eines Produktlebenszyklus entsprechen typischen Merkmalen des Graphen:

| Frage im Sachzusammenhang | Merkmal des Graphen von $a$ |
|---|---|
| Absatz bei der Markteinführung | $y$-Achsenabschnitt $a(0)$ |
| Zeitpunkt und Höhe des höchsten Absatzes | Hochpunkt |
| Zeitpunkt des stärksten Anstiegs bzw. Rückgangs | Wendepunkte (oder Randstellen) |
| Absatz steigt progressiv bzw. degressiv | Graph linksgekrümmt bzw. rechtsgekrümmt |
| Marktaustritt | positive Nullstelle |
| langfristiger Absatz | waagrechte Asymptote |

Bei der Spielkonsole liest man ab: Bei der Markteinführung wird noch nichts abgesetzt ($a(0)=0$), nach $8$ Monaten ist der Absatz mit ca. $13{,}2$ ME/Monat am höchsten, und langfristig pendelt er sich bei $4$ ME/Monat ein.

Achtung bei Randstellen: Ist ein Graph schon bei $t=0$ rechtsgekrümmt, steigt der Absatz von Anfang an degressiv. Dann gibt es keinen Wendepunkt mit stärkstem Anstieg, und der stärkste Anstieg liegt bei der Markteinführung.

{% include check-anker.html nummer="1" %}

### Der Graph der Ableitungsfunktion

Die Ableitung $a'(t)$ ist die momentane **Änderungsrate** des monatlichen Absatzes (Einheit: ME/Monat pro Monat). Ihr Graph zeigt, *wie schnell* sich der Absatz ändert, aber nicht, *wie hoch* er ist:

- $a'(t)>0$: Der Absatz nimmt zu. $a'(t)<0$: Der Absatz nimmt ab.
- Nullstelle von $a'$ mit Vorzeichenwechsel von $+$ nach $-$: Zeitpunkt des höchsten Absatzes.
- Hochpunkt bzw. Tiefpunkt von $a'$: Zeitpunkt des stärksten Anstiegs bzw. Rückgangs, also die Wendestellen von $a$. Auch hier können Randstellen die Extremwerte liefern.

Bei der Spielkonsole ist $a'(t)=(-0{,}25t^2+1{,}75t+2)\cdot e^{-0{,}25t}$. Der Graph von $a'$ hat seinen Hochpunkt bei $t\approx 1{,}48$, seine Nullstelle mit Vorzeichenwechsel bei $t=8$ und seinen Tiefpunkt bei $t\approx 13{,}52$. Das sind genau die Phasengrenzen von oben.

{% include check-anker.html nummer="2" %}

## Kennzahlen rechnerisch bestimmen

Für die rechnerische Bestimmung braucht man $a$, $a'$ und $a''$ (die Ableitungen werden mit Produkt- und Kettenregel gebildet und in Aufgaben oft vorgegeben). Entscheidend ist eine Eigenschaft der $e$-Funktion:

$$
e^{-ct}>0 \text{ für alle } t \qquad\Rightarrow\qquad p(t)\cdot e^{-ct}=0 \quad\Leftrightarrow\quad p(t)=0
$$

Bei Gleichungen wie $a'(t)=0$ oder $a''(t)=0$ genügt es deshalb, den Klammerterm null zu setzen. Bei der Spielkonsole:

$$
\begin{align*}
a'(t)=0 \quad&\Leftrightarrow\quad -0{,}25t^2+1{,}75t+2=0 \quad\Leftrightarrow\quad t^2-7t-8=0 \quad\Leftrightarrow\quad t=-1 \ \text{ oder } \ t=8\\
a''(t)=0 \quad&\Leftrightarrow\quad 0{,}0625t^2-0{,}9375t+1{,}25=0 \quad\Leftrightarrow\quad t^2-15t+20=0 \quad\Leftrightarrow\quad t\approx 1{,}48 \ \text{ oder } \ t\approx 13{,}52
\end{align*}
$$

Ob tatsächlich ein Hochpunkt bzw. eine Wendestelle vorliegt, zeigt der **Vorzeichenwechsel** des Klammerterms: $-0{,}25t^2+1{,}75t+2$ wechselt bei $t=8$ von $+$ nach $-$, also liegt dort ein Maximum ($t=-1$ liegt außerhalb des Zeitraums). Alternativ prüft man $a''(8)<0$. Kandidaten außerhalb des betrachteten Zeitraums werden verworfen, und die Randstellen (z. B. $t=0$) werden immer mitgeprüft.

Den **langfristigen Absatz** erhält man über den Grenzwert $\lim\limits_{t\to\infty} a(t)$, den **Marktaustritt** über die positive Nullstelle von $p(t)$.

Häufig wird auch nach einem Zeitraum gefragt, in dem der Absatz über einem Schwellenwert $c$ liegt, etwa weil ab $10$ ME/Monat zusätzliches Personal nötig ist. Dazu löst man $a(t)=c$ mit dem Rechner. Zwischen den beiden Lösungen liegt der Absatz über $c$, sofern das Maximum größer als $c$ ist. Bei der Spielkonsole ergibt $a(t)=10$ die Lösungen $t_1\approx 4{,}06$ und $t_2\approx 14{,}33$.

{% include check-anker.html nummer="3" %}

## Gesamtabsatz als Fläche unter dem Graphen

Wie viele Konsolen werden im ersten Halbjahr *insgesamt* verkauft? Die Funktionswerte $a(t)$ beantworten das nicht, denn sie geben nur an, wie viel *pro Monat* verkauft wird.

Denken wir uns den Zeitraum in einzelne Monate zerlegt: Wird in einem Monat etwa $a(t)$ ME pro Monat abgesetzt, dann sind das in diesem Monat

$$
\underbrace{a(t)}_{\text{Höhe in ME/Monat}}\cdot \underbrace{1}_{\text{Breite in Monaten}} \quad\text{ME}.
$$

Jeder Monatsabsatz ist also die Fläche eines schmalen Rechtecks unter dem Graphen. Addiert man die Rechtecke, erhält man den Gesamtabsatz, und mit immer schmaleren Streifen genau die **Fläche unter dem Graphen**:

$$
\text{Gesamtabsatz von } t_1 \text{ bis } t_2 = \int_{t_1}^{t_2} a(t)\,dt \quad\text{(in ME)}
$$

Im folgenden Widget kannst du den Zeitraum verändern und die Monatsbalken einblenden. Der rechte Graph zeigt den **kumulierten Absatz** $A(t)=\int_0^t a(s)\,ds$, also die bis zum Zeitpunkt $t$ insgesamt verkauften ME. Die Differenz $A(t_2)-A(t_1)$ ist genau die markierte Fläche.

{% include widgets/widget-gesamtabsatz.html term="(t^2+t-4)*exp(-0.25*t)+4" tmax=30 t1=0 t2=6 %}

Für das erste Halbjahr ergibt sich $\int_0^6 a(t)\,dt\approx 43{,}11$ ME, also ca. $43\,110$ Konsolen.

Ohne Rechner lässt sich die Fläche **abschätzen**:

- **Kästchen zählen:** Ein Kästchen im Koordinatensystem entspricht Breite $\cdot$ Höhe, z. B. $1$ Monat $\cdot\ 2$ ME/Monat $=2$ ME.
- **Rechtecke:** Liegt der Graph auf $[t_1;t_2]$ zwischen den Werten $m$ und $M$, dann liegt die Fläche zwischen $(t_2-t_1)\cdot m$ und $(t_2-t_1)\cdot M$. Damit lassen sich Aussagen wie „Im ersten Halbjahr werden mindestens $60$ ME abgesetzt“ prüfen: Auf $[0;6]$ ist $a(t)\le a(6)\approx 12{,}48$, also ist der Gesamtabsatz kleiner als $6\cdot 12{,}48\approx 75$ ME. Diese grobe Grenze reicht hier noch nicht aus. Mit den Monatsbalken (rechte Ränder) ergibt sich die engere Grenze $a(1)+a(2)+\dots+a(6)\approx 49{,}2$ ME, die Aussage ist also falsch.

Der **durchschnittliche monatliche Absatz** ist die Höhe des Rechtecks, das über demselben Zeitraum dieselbe Fläche hat. Im ersten Halbjahr: $\frac{43{,}11}{6}\approx 7{,}19$ ME/Monat.

{% include check-anker.html nummer="4" %}

## Kennzahlen mit Integralen berechnen

Mit dem Rechner werden die Integrale exakt bestimmt. Man muss dabei genau unterscheiden zwischen dem **monatlichen Absatz** $a(t)$ (Funktionswert, ME/Monat) und dem **Gesamtabsatz** (Integral, ME).

| Gesucht | Ansatz |
|---|---|
| monatlicher Absatz nach $t_0$ Monaten | $a(t_0)$ |
| Gesamtabsatz vom Ende des $t_1$-ten bis zum Ende des $t_2$-ten Monats | $\int_{t_1}^{t_2} a(t)\,dt$ |
| Gesamtabsatz während des gesamten Lebenszyklus (bis $T$) | $\int_0^{T} a(t)\,dt$ |
| durchschnittlicher monatlicher Absatz von $t_1$ bis $t_2$ | $\frac{1}{t_2-t_1}\int_{t_1}^{t_2} a(t)\,dt$ |
| Zeitpunkt, zu dem der Gesamtabsatz $X$ erreicht | $\int_0^{z} a(t)\,dt=X$ nach $z$ lösen |

Dabei ist $T$ der Zeitpunkt des Marktaustritts oder das in der Aufgabe angegebene Ende des Lebenszyklus.

Bei der Spielkonsole gilt zum Beispiel $\int_0^{z} a(t)\,dt=100 \Rightarrow z\approx 10{,}39$: Nach knapp $10{,}4$ Monaten sind $100\,000$ Konsolen verkauft.

Ob ein Gesamtabsatz überhaupt erreicht wird, hängt vom Ende des Zyklus ab: Mit Marktaustritt ist der Gesamtabsatz durch $\int_0^T a(t)\,dt$ begrenzt. Bei einem langfristigen Absatz $d>0$ kommen jeden Monat ca. $d$ ME hinzu, der Gesamtabsatz wächst unbegrenzt.

{% include check-anker.html nummer="5" %}
