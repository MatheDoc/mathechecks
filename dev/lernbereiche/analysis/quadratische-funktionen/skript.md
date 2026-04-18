---
layout: dev-module
title: Quadratische Funktionen - Skript (Dev)
description: Dev-Lernbereich Quadratische Funktionen, Modul Skript.
page_context: Lernbereich
nav: dashboard
body_class: page-module-designs
module_key: skript
published: true
lernbereich: quadratische-funktionen
gebiet: analysis
permalink: /dev/lernbereiche/analysis/quadratische-funktionen/skript.html
---

<!--## Ein Brückenbogen als Parabel

Ein Architekt plant einen parabelförmigen Brückenbogen über einen 40 m breiten Fluss. Der Bogen soll in der Mitte 12 m hoch sein. Wie lautet die Gleichung des Bogens — und passt ein 10 m hohes Schiff noch durch, wenn es 8 m vom Ufer entfernt fährt?

Um diese Frage zu beantworten, brauchen wir die Werkzeuge der quadratischen Funktionen: Darstellungsformen, Nullstellen, Scheitelpunkte und die Fähigkeit, Sachsituationen in Gleichungen zu übersetzen.-->

## Darstellungsformen

Quadratische Funktionen können in drei verschiedenen Formen dargestellt werden. Jede Form hat ihre Stärken — je nach Situation wählt man die passende.

### Normalform

Die allgemeine Form lautet

$$f(x) = ax^2 + bx + c$$

mit drei Parametern:

- $a$ heißt **Öffnungsfaktor**. Er bestimmt, ob die Parabel nach oben ($a > 0$) oder nach unten ($a < 0$) geöffnet ist, und wie breit oder schmal sie verläuft.
- $b$ beeinflusst die Lage der Parabel — genauer die horizontale Position des Scheitels.
- $c$ ist der **$y$-Achsenabschnitt**: der Funktionswert an der Stelle $x = 0$.

### Scheitelpunktform

$$f(x) = a(x - d)^2 + e$$

Der **Scheitelpunkt** $S(d \mid e)$ ist der tiefste Punkt (bei $a > 0$) bzw. höchste Punkt (bei $a < 0$) der Parabel. In dieser Form liest man ihn direkt ab.

### Faktorisierte Form

$$f(x) = a(x - x_1)(x - x_2)$$

Hier sind $x_1$ und $x_2$ die **Nullstellen** — also die Stellen, an denen der Graph die $x$-Achse schneidet. Diese Form existiert nur, wenn die Funktion tatsächlich Nullstellen hat.

### Graph und Wertetabelle

Der Graph einer quadratischen Funktion ist eine **Parabel**. Sie ist achsensymmetrisch zur senkrechten Geraden durch den Scheitel (der **Symmetrieachse** $x = d$).

Wie bei linearen Funktionen kann man auch hier Wertetabellen erstellen: $x$-Werte einsetzen und $f(x)$ berechnen. Bei quadratischen Funktionen erkennt man die Symmetrie daran, dass gleich weit links und rechts vom Scheitel die gleichen $y$-Werte auftreten.

### Darstellungswechsel

| Von → Nach | Vorgehen |
|---|---|
| Gleichung → Wertetabelle | $x$-Werte einsetzen, $f(x)$ berechnen |
| Gleichung → Graph | Wertetabelle erstellen, Punkte eintragen, Parabel zeichnen |
| Graph → Scheitelpunktform | Scheitel $(d \mid e)$ ablesen, $a$ über weiteren Punkt bestimmen |
| Graph → Faktorisierte Form | Nullstellen $x_1, x_2$ ablesen, $a$ über weiteren Punkt bestimmen |
| SPF / FF → Normalform | Ausmultiplizieren |
| NF → SPF | Quadratische Ergänzung (→ Check 8) |
| NF → FF | Nullstellen berechnen (→ Checks 4–6) |

Im interaktiven Diagramm können Sie beobachten, wie Änderungen an $a$, $b$ und $c$ gleichzeitig die Gleichung, den Graphen und die Wertetabelle verändern.

{% include dev/widgets/widget-quadratische-funktionen.html %}

{% include dev/check-anker.html nummer="1" %}

{% include dev/check-anker.html nummer="2" %}

{% include dev/check-anker.html nummer="3" %}

## Nullstellen

Die **Nullstellen** einer quadratischen Funktion sind die $x$-Werte, für die $f(x) = 0$ gilt — also die Schnittpunkte des Graphen mit der $x$-Achse. Je nach Darstellungsform gibt es unterschiedliche Wege, sie zu finden.

### Nullstellen mit der $p$-$q$-Formel

Liegt die Funktion in Normalform vor, bringt man die Gleichung $ax^2 + bx + c = 0$ zunächst auf die Form $x^2 + px + q = 0$ (durch $a$ dividieren, falls $a \neq 1$). Dann gilt:

$$x_{1{,}2} = -\frac{p}{2} \pm \sqrt{\left(\frac{p}{2}\right)^2 - q}$$

Der Ausdruck unter der Wurzel heißt **Diskriminante**:

$$D = \left(\frac{p}{2}\right)^2 - q$$

Sie entscheidet über die Anzahl der Nullstellen:

| Diskriminante | Nullstellen |
|---|---|
| $D > 0$ | zwei verschiedene Nullstellen |
| $D = 0$ | genau eine Nullstelle (Scheitel auf der $x$-Achse) |
| $D < 0$ | keine Nullstelle (Parabel schneidet die $x$-Achse nicht) |

{% include dev/check-anker.html nummer="4" %}

### Nullstellen aus der faktorisierten Form

Liegt die Funktion als $f(x) = a(x - x_1)(x - x_2)$ vor, liest man die Nullstellen direkt ab: $x_1$ und $x_2$. Der **Satz vom Nullprodukt** liefert die Begründung: Ein Produkt ist genau dann null, wenn mindestens einer der Faktoren null ist.

{% include dev/check-anker.html nummer="5" %}

### Nullstellen aus der Scheitelpunktform

Aus $a(x - d)^2 + e = 0$ löst man schrittweise:

$$(x - d)^2 = -\frac{e}{a}$$

Nullstellen existieren nur, wenn $-\frac{e}{a} \geq 0$. Falls ja:

$$x_{1{,}2} = d \pm \sqrt{-\frac{e}{a}}$$

{% include dev/check-anker.html nummer="6" %}

### Exkurs: Herleitung der $p$-$q$-Formel

Die $p$-$q$-Formel lässt sich durch **quadratische Ergänzung** aus $x^2 + px + q = 0$ herleiten:

$$\begin{aligned}
x^2 + px + q &= 0 \\
x^2 + px &= -q \\
x^2 + px + \left(\frac{p}{2}\right)^2 &= -q + \left(\frac{p}{2}\right)^2 \\
\left(x + \frac{p}{2}\right)^2 &= \left(\frac{p}{2}\right)^2 - q \\
x + \frac{p}{2} &= \pm\sqrt{\left(\frac{p}{2}\right)^2 - q} \\
x_{1{,}2} &= -\frac{p}{2} \pm \sqrt{\left(\frac{p}{2}\right)^2 - q}
\end{aligned}$$

## Funktionswerte und Umkehrwerte

Bei quadratischen Funktionen unterscheidet man zwei Grundaufgaben:

- **Funktionswert**: Einen $x$-Wert einsetzen und $f(x_0)$ berechnen. Das ist reines Einsetzen in die Funktionsgleichung.
- **Umkehrwert**: Einen $y$-Wert vorgeben und alle $x$ bestimmen, für die $f(x) = y_0$ gilt.

Der Umkehrwert führt auf eine quadratische Gleichung: Aus $ax^2 + bx + c = y_0$ wird $ax^2 + bx + (c - y_0) = 0$. Diese löst man mit der $p$-$q$-Formel. Da eine Parabel achsensymmetrisch ist, gibt es in der Regel **zwei Lösungen** — außer der gesuchte $y$-Wert liegt genau am Scheitel (eine Lösung) oder unterhalb/oberhalb der Parabel (keine Lösung).

{% include dev/check-anker.html nummer="7" %}

## Schnittpunkte

Um die **Schnittpunkte** einer Parabel mit einer Geraden oder einer zweiten Parabel zu berechnen, setzt man die Funktionsterme gleich und löst die entstehende Gleichung.

### Parabel und Gerade

Gegeben: $f(x) = ax^2 + bx + c$ und $g(x) = mx + n$. Gleichsetzen:

$$ax^2 + bx + c = mx + n$$

Umstellen liefert eine quadratische Gleichung, die man mit der $p$-$q$-Formel löst.

### Zwei Parabeln

Gegeben: $f(x) = a_1 x^2 + b_1 x + c_1$ und $g(x) = a_2 x^2 + b_2 x + c_2$. Gleichsetzen und umstellen:

$$(a_1 - a_2)x^2 + (b_1 - b_2)x + (c_1 - c_2) = 0$$

Falls $a_1 = a_2$, reduziert sich das auf eine lineare Gleichung.

Die $y$-Koordinaten der Schnittpunkte erhält man jeweils durch Einsetzen in eine der beiden Funktionen.

{% include dev/check-anker.html nummer="8" %}

## Umwandlung zwischen Darstellungsformen

Die drei Darstellungsformen — Normalform, Scheitelpunktform und faktorisierte Form — lassen sich ineinander umwandeln. Zwei der Umwandlungen erfordern Rechentechniken aus den vorherigen Abschnitten.

### Ausmultiplizieren (SPF → NF, FF → NF)

In beiden Fällen multipliziert man die Klammern aus und fasst zusammen. Das führt stets zur Normalform $ax^2 + bx + c$.

### Normalform → Faktorisierte Form

Man berechnet die Nullstellen (z. B. mit der $p$-$q$-Formel) und setzt sie in die faktorisierte Form ein:

$$f(x) = a(x - x_1)(x - x_2)$$

Das geht nur, wenn Nullstellen existieren ($D \geq 0$).

### Normalform → Scheitelpunktform (quadratische Ergänzung)

Aus $f(x) = ax^2 + bx + c$ klammert man zunächst $a$ aus den ersten beiden Termen:

$$f(x) = a\left(x^2 + \frac{b}{a}x\right) + c$$

Dann ergänzt man innerhalb der Klammer zu einem vollständigen Quadrat:

$$f(x) = a\!\left(x^2 + \frac{b}{a}x + \left(\frac{b}{2a}\right)^2 - \left(\frac{b}{2a}\right)^2\right) + c = a\!\left(x + \frac{b}{2a}\right)^2 + c - \frac{b^2}{4a}$$

Der Scheitel liegt bei $S\!\left(-\frac{b}{2a} \mid c - \frac{b^2}{4a}\right)$.

{% include dev/check-anker.html nummer="9" %}

## Gleichung aufstellen

In vielen Aufgaben sind Informationen über eine quadratische Funktion gegeben (Punkte, Nullstellen, Scheitel), und die Gleichung soll bestimmt werden. Die Kunst besteht darin, die passende Darstellungsform zu wählen:

| Gegebene Information | Günstige Form | Vorgehen |
|---|---|---|
| Scheitel + weiterer Punkt | Scheitelpunktform | $S$ einsetzen → $a$ über den Punkt bestimmen |
| Zwei Nullstellen + weiterer Punkt | Faktorisierte Form | $x_1, x_2$ einsetzen → $a$ über den Punkt bestimmen |
| Drei Punkte | Normalform | Drei Gleichungen mit drei Unbekannten ($a$, $b$, $c$) aufstellen und lösen |

Bei drei Punkten entsteht ein lineares Gleichungssystem. Es wird mit Einsetzen oder dem Additionsverfahren gelöst — die Werte sind dabei so gewählt, dass sie ganzzahlig oder einfach bleiben.

{% include dev/check-anker.html nummer="10" %}

## Anwendungen

Quadratische Funktionen tauchen in vielen Sachsituationen auf — manchmal, weil ein Objekt tatsächlich eine Parabelform hat, manchmal, weil ein Optimierungsproblem zu einer quadratischen Gleichung führt.

### Geometrische Szenarien

In der Geometrie und Physik beschreiben Parabeln die Form von Brückenbögen, Wurfbahnen, Parabolspiegeln oder Wasserstrahlkurven. Typische Aufgaben:

- Koordinatensystem sinnvoll festlegen (z. B. Scheitel im Ursprung oder Nullstellen auf der $x$-Achse)
- Aus dem Sachkontext Punkte oder Nullstellen ablesen
- Funktionsgleichung aufstellen und Fragen beantworten (Höhe, Weite, Durchfahrtshöhe)

{% include dev/check-anker.html nummer="11" %}

### Optimierung

Wenn eine Zielgröße durch eine quadratische Funktion beschrieben wird (z. B. Gewinn, Fläche, Höhe), liefert der **Scheitel** direkt das Maximum oder Minimum.

Typisches Vorgehen:

1. Zielfunktion aufstellen (quadratisch)
2. Scheitelpunkt bestimmen (quadratische Ergänzung oder Formel $d = -\frac{b}{2a}$)
3. Ergebnis im Sachkontext interpretieren

{% include dev/check-anker.html nummer="12" %}

## Parametereinfluss

Wie verändern sich Form und Lage einer Parabel, wenn man die Parameter in der Scheitelpunktform $f(x) = a(x - d)^2 + e$ variiert?

| Parameter | Wirkung |
|---|---|
| $a > 1$ | Parabel wird schmaler (gestaucht) |
| $0 < a < 1$ | Parabel wird breiter (gestreckt) |
| $a < 0$ | Parabel öffnet nach unten |
| $d$ | Verschiebung des Scheitels in $x$-Richtung (nach rechts für $d > 0$) |
| $e$ | Verschiebung des Scheitels in $y$-Richtung (nach oben für $e > 0$) |

Typische Falle: In der Scheitelpunktform steht $f(x) = a(x - d)^2 + e$. Bei $f(x) = a(x + 3)^2$ ist $d = -3$, nicht $d = 3$.

Im interaktiven Diagramm können Sie die Wirkung jedes Parameters einzeln beobachten.

{% include dev/widgets/widget-quadratische-funktionen-parameter.html %}

{% include dev/check-anker.html nummer="13" %}

<!--## Zurück zum Brückenbogen

Jetzt können wir die Eingangsfrage beantworten. Der Brückenbogen spannt sich über 40 m, der Scheitel liegt in der Mitte bei 12 m Höhe.

Wir legen das Koordinatensystem so, dass die Auflagepunkte bei $x_1 = 0$ und $x_2 = 40$ liegen. Der Scheitel befindet sich dann bei $S(20 \mid 12)$.

**Gleichung aufstellen** (Scheitelpunktform):

$$f(x) = a(x - 20)^2 + 12$$

Den Auflagepunkt $f(0) = 0$ einsetzen:

$$a(0 - 20)^2 + 12 = 0 \quad\Rightarrow\quad 400a = -12 \quad\Rightarrow\quad a = -0{,}03$$

Also: $f(x) = -0{,}03(x - 20)^2 + 12$.

**Durchfahrtshöhe bei 8 m vom Ufer** (also $x = 8$):

$$f(8) = -0{,}03(8 - 20)^2 + 12 = -0{,}03 \cdot 144 + 12 = -4{,}32 + 12 = 7{,}68$$

Die Durchfahrtshöhe beträgt $7{,}68$ m — das 10 m hohe Schiff passt leider **nicht** durch.
-->