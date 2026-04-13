---
layout: dev-module
title: Lineare Funktionen - Skript (Dev)
description: Dev-Lernbereich Lineare Funktionen, Modul Skript.
page_context: Lernbereich
nav: dashboard
body_class: page-module-designs
module_key: skript
published: true
lernbereich: lineare-funktionen
gebiet: analysis
permalink: /dev/lernbereiche/analysis/lineare-funktionen/skript.html
---

## Einführung

Lineare Funktionen beschreiben Zusammenhänge mit konstanter Änderungsrate. Ihr Graph ist eine Gerade. In vielen Alltagssituationen — vom Handytarif über Mietkosten bis zur Temperaturentwicklung — treten solche Zusammenhänge auf.

In diesem Lernbereich geht es um die drei zentralen Darstellungsformen linearer Funktionen, um typische Rechenverfahren und um die Anwendung auf Sachsituationen.

## Darstellungsformen

Eine lineare Funktion lässt sich auf drei verschiedene Weisen darstellen, die alle gleichwertig sind und ineinander umgewandelt werden können:

### Funktionsgleichung

Die allgemeine Form lautet

$$f(x)=mx+b$$

mit zwei Parametern:

- $m$ heißt **Steigung**. Sie gibt an, um wie viele Einheiten sich der $y$-Wert ändert, wenn der $x$-Wert um 1 zunimmt.
- $b$ heißt **$y$-Achsenabschnitt**. Er gibt an, wo der Graph die $y$-Achse schneidet, also den Funktionswert an der Stelle $x=0$.

Einige Beispiele:

| Gleichung | Steigung $m$ | $y$-Achsenabschnitt $b$ |
|---|---|---|
| $f(x)=2x+3$ | $2$ | $3$ |
| $g(x)=-0{,}5x+4$ | $-0{,}5$ | $4$ |
| $h(x)=3x$ | $3$ | $0$ |
| $k(x)=-2$ | $0$ | $-2$ |

### Graph

Der Graph einer linearen Funktion ist eine **Gerade**. Die Steigung $m$ bestimmt die Neigung der Geraden, der $y$-Achsenabschnitt $b$ bestimmt die Lage.

- $m>0$: Der Graph steigt von links nach rechts.
- $m<0$: Der Graph fällt von links nach rechts.
- $m=0$: Der Graph verläuft horizontal.

Die Steigung lässt sich am Graphen mit dem **Steigungsdreieck** ablesen: Man geht vom Graphen aus 1 Einheit nach rechts und liest ab, um wie viele Einheiten sich der $y$-Wert ändert. Diese Änderung ist $m$.

### Wertetabelle

Für ausgewählte $x$-Werte werden die zugehörigen Funktionswerte $f(x)$ berechnet und in einer Tabelle zusammengefasst. Die Wertetabelle zeigt das Steigungsverhalten konkret: In jeder Spalte wächst der $y$-Wert um den gleichen Betrag $m$, wenn der $x$-Wert um 1 zunimmt.

### Darstellungswechsel

Diese drei Darstellungsformen lassen sich ineinander überführen:

| Von → Nach | Vorgehen |
|---|---|
| Gleichung → Wertetabelle | $x$-Werte einsetzen, $f(x)$ berechnen |
| Gleichung → Graph | Wertetabelle erstellen, Punkte eintragen, Gerade zeichnen |
| Graph → Gleichung | $m$ per Steigungsdreieck ablesen, $b$ an der $y$-Achse ablesen |
| Wertetabelle → Gleichung | $m$ aus gleichmäßiger Differenz berechnen, $b$ bestimmen |
| Zwei Punkte → Gleichung | $m=\frac{y_2-y_1}{x_2-x_1}$, dann $b=y_1-m\cdot x_1$ |

Im interaktiven Diagramm können Sie beobachten, wie Änderungen an $m$ und $b$ gleichzeitig die Gleichung, den Graphen und die Wertetabelle verändern.

{% include dev/lineare-funktionen-explorer.html %}

{% include dev/check-anker.html nummer="1" %}

{% include dev/check-anker.html nummer="2" %}

{% include dev/check-anker.html nummer="3" %}

{% include dev/check-anker.html nummer="4" %}


## Rechnen mit linearen Funktionen

### Punktprobe

Um zu prüfen, ob ein Punkt $P(x_0 \mid y_0)$ auf dem Graphen von $f$ liegt, berechnet man den Funktionswert $f(x_0)$ und vergleicht:

- $f(x_0) = y_0$: $P$ liegt **auf** dem Graphen.
- $y_0 > f(x_0)$: $P$ liegt **oberhalb** des Graphen.
- $y_0 < f(x_0)$: $P$ liegt **unterhalb** des Graphen.

{% include dev/check-anker.html nummer="5" %}

### Funktionswerte und Umkehrwerte

Zwei grundlegende Berechnungen treten immer wieder auf:

- **Funktionswert**: Gegeben ist ein $x$-Wert, gesucht ist $f(x)$. Lösung: Einsetzen in $f(x)=mx+b$.
- **Umkehrwert**: Gegeben ist ein $y$-Wert, gesucht ist $x$. Lösung: $f(x)=y_0$ setzen und nach $x$ auflösen:

$$x=\frac{y_0-b}{m}$$

{% include dev/check-anker.html nummer="6" %}

### Nullstellen und Vorzeichenbereiche

Die **Nullstelle** einer linearen Funktion ist die Stelle, an der der Graph die $x$-Achse schneidet, also $f(x)=0$:

$$mx+b=0 \quad\Rightarrow\quad x_0=-\frac{b}{m}$$

Links und rechts der Nullstelle hat die Funktion ein festes Vorzeichen. Welches Vorzeichen wo vorliegt, hängt von der Steigung ab:

| Steigung | für $x < x_0$ | für $x > x_0$ |
|---|---|---|
| $m > 0$ | $f(x) < 0$ | $f(x) > 0$ |
| $m < 0$ | $f(x) > 0$ | $f(x) < 0$ |

{% include dev/check-anker.html nummer="7" %}

### Schnittpunkte und Vergleichsbereiche

Um den **Schnittpunkt** zweier linearer Funktionen $f(x)=m_1x+b_1$ und $g(x)=m_2x+b_2$ zu berechnen, setzt man die Funktionsterme gleich:

$$m_1x+b_1=m_2x+b_2 \quad\Rightarrow\quad x_S=\frac{b_2-b_1}{m_1-m_2}$$

Den zugehörigen $y$-Wert erhält man durch Einsetzen: $y_S=f(x_S)$.

Voraussetzung: $m_1\neq m_2$ (sonst sind die Geraden parallel und haben keinen Schnittpunkt).

**Vergleichsbereiche**: Links und rechts des Schnittpunkts liegt der Graph der einen Funktion ober- bzw. unterhalb des Graphen der anderen. Um zu bestimmen, welcher Graph wo oben liegt, prüft man das Vorzeichen der Differenz $f(x)-g(x)=(m_1-m_2)x+(b_1-b_2)$ links und rechts von $x_S$.

{% include dev/check-anker.html nummer="8" %}

## Anwendungen

Lineare Funktionen eignen sich zur Modellierung von Sachsituationen, in denen eine Größe mit konstanter Rate wächst oder fällt. Der Grundaufbau ist stets:

1. **Modellierung**: Aus der Sachsituation die Steigung $m$ (Änderungsrate) und den $y$-Achsenabschnitt $b$ (Startwert) ablesen und die Funktionsgleichung aufstellen.
2. **Auswertung**: Funktionswerte, Umkehrwerte oder Nullstellen berechnen und im Sachzusammenhang interpretieren.

| Sachgröße | Steigung $m$ | $y$-Achsenabschnitt $b$ |
|---|---|---|
| Taxikosten | Preis pro km | Grundgebühr |
| Wasserstand | Änderung pro Stunde | Anfangsstand |
| Produktionskosten | variable Stückkosten | Fixkosten |

{% include dev/check-anker.html nummer="9" %}

### Modellvergleich und Break-Even

Wenn zwei Sachsituationen jeweils durch eine lineare Funktion modelliert werden, kann man sie vergleichen. Der **Break-Even-Punkt** (Schnittpunkt) gibt an, ab welchem Wert die eine Alternative günstiger wird als die andere.

Typisches Vorgehen:

1. Beide Funktionsgleichungen aufstellen.
2. Gleichsetzen und Schnittpunkt berechnen.
3. Bereiche links und rechts des Schnittpunkts vergleichen und im Sachzusammenhang interpretieren.

{% include dev/check-anker.html nummer="10" %}



