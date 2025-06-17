---
layout: skript
title: Zufallsexperimente und Wahrscheinlichkeiten
description: Zufallsexperimente und Wahrscheinlichkeiten - Skript
lernbereich: zufallsexperimente-und-wahrscheinlichkeiten
---

## Mengen

In der Stochastik befassen wir uns mit der Berechnung von Wahrscheinlichkeiten. Um diese präzise und eindeutig zu beschreiben, bedienen wir uns der Sprache der Mengenlehre. Eine Menge ist eine Zusammenfassung einzelner Elemente.

### Beispiele: Einfache Mengen

- Die Menge der besten Schulfächer: $ S=\\{\text{Mathe}, \text{Physik}\\} $
- Die Menge der natürlichen Zahlen: $ N=\\{1, 2, 3, \ldots\\} $
- Die Menge der beliebtesten Fußballmannschaften: $ F=\\{\text{FC Bayern München}\\} $
- Die Menge der Würfelergebnisse: $ W=\\{1, 2, 3, 4, 5, 6\\} $
- Die Menge der Ergebnisse eines Münzwurfs: $ M=\\{K, Z\\} $

### Grundbegriffe

- Die Elemente einer Menge werden häufig geeignet abgekürzt.
- Die Elemente einer Menge werden immer in geschweiften Klammern $\\{…\\}$ angegeben.
- Die leere Menge enthält keine Elemente und wird mit $\emptyset$ bezeichnet.
- Liegen alle Elemente einer Menge $A$ auch in einer Menge $X$, so ist $A$ eine Teilmenge von $X$. Wir schreiben auch $A \subset X$.
- Beispiel: Die Menge $X = \\{1, 3, 4, 6, 8\\}$ hat die Teilmenge $A = \\{3, 6\\}$.
- Beispiel: Die Menge einer Spielgruppe von Kindern ist $X = \\{\text{Tobias},  \text{Jessica},  \text{Achmed},  \text{Lydia}\\}$. Dann ist die Teilmenge der Mädchen $A = \\{\text{Jessica},  \text{Lydia}\\}$.
- Ist $A$ eine Teilmenge von $X$, so bilden alle Elemente von $X$, die nicht in $A$ liegen, das Komplement von $A$. Das Komplement von $A$ wird mit $\overline{A}$ bezeichnet.
- Beispiel: Für $X = \\{1, 3, 4, 6, 8\\}$ und der Teilmenge $A = \\{3, 6\\}$ ist das Komplement $\overline{A} = \\{1, 4, 8\\}$.
- Beispiel: Für $X = \\{\text{Tobias},  \text{Jessica},  \text{Achmed},  \text{Lydia}\\}$ und der Teilmenge der Mädchen $A = \\{\text{Jessica},  \text{Lydia}\\}$ ist das Komplement die Teilmenge der Jungen $\overline{A} = \\{\text{Tobias}, \text{Achmed}\\}$.

### Exkurs: Das Russellsche Paradoxon

Der Mengenbegriff erscheint zunächst klar und einfach: Eine Menge ist eine Zusammenfassung von verschiedenen Objekten. Doch wenn wir genauer hinschauen, können Widersprüche auftreten.
Ein bekanntes Beispiel ist das Russellsche Paradoxon:

Wir betrachten die Menge $M$, die alle Mengen enthält, die sich nicht selbst enthalten.
Nun stellen wir die Frage: Enthält $M$ sich selbst?

- Wenn ja, dann dürfte sie sich nicht enthalten (denn sie enthält ja nur Mengen, die sich nicht selbst enthalten).
- Wenn nein, dann müsste sie sich enthalten (denn sie erfüllt ja die Bedingung, sich nicht selbst zu enthalten).

Beides führt zu einem Widerspruch.
Dieses Paradoxon zeigt, dass der naive Mengenbegriff überarbeitet werden muss. Deshalb arbeiten Mathematiker heute mit exakteren, axiomatischen Grundlagen der Mengenlehre.

### Mengenoperationen

Sind $A$ und $B$ Teilmengen einer Menge $X$, so entstehen durch Vereinigungen, Durchschnitte und Komplemente neue Teilmengen.

### Beispiel: Ausgänge eines Würfelwurfs

Es sei $ X=\\{1, 2, 3, 4, 5, 6\\} $.

| Textuelle Beschreibung                | Symbol         | Operation                    | Mengenschreibweise |
| ------------------------------------- | -------------- | ---------------------------- | ------------------ |
| Eine Zahl ist durch 2 teilbar.        | $A$            |                              | $\\{2, 4, 6\\}$    |
| Eine Zahl ist durch 3 teilbar.        | $B$            |                              | $\\{3, 6\\}$       |
| Eine Zahl ist durch 2 oder 3 teilbar. | $A \cup B$     | Vereinigung von $A$ und $B$  | $\\{2, 3, 4, 6\\}$ |
| Eine Zahl ist durch 2 und 3 teilbar.  | $A \cap B$     | Durchschnitt von $A$ und $B$ | $\\{6\\}$          |
| Eine Zahl ist nicht durch 2 teilbar.  | $\overline{A}$ | Komplement von $A$           | $\\{1, 3, 5\\}$    |
| Eine Zahl ist nicht durch 3 teilbar.  | $\overline{B}$ | Komplement von $B$           | $\\{1, 2, 4, 5\\}$ |

Elemente werden nicht doppelt aufgeführt. Für die Vereinigung von $A=\\{2, 4, 6\\}$ und $B=\\{3, 6\\}$ schreiben wir $\\{2, 3, 4, 6\\}$ und nicht $\\{2, 3, 4, 6, 6\\}$ (obwohl es formal nicht verkehrt wäre).

Mit Hilfe dieser Operationen, lassen sich weitere Mengen beschreiben, z.B.:

- Eine Zahl ist weder durch 2 noch durch 3 teilbar: $\overline{A}\cap{\overline{B}}=\\{1, 5\\}$
- Eine Zahl ist entweder durch 2 oder durch 3 teilbar (aber eben nicht durch 2 und 3): $(A\cap\overline{B}) \cup (\overline{A}\cap B)=\\{2, 3, 4\\}$

### Rechenregeln

Es seien $A$ und $B$ Teilmengen einer Menge $X$.

| Aussage                                                | Bedeutung                                                                                      |
| ------------------------------------------------------ | ---------------------------------------------------------------------------------------------- |
| $A \cap \overline{A} = \emptyset$                      | Es gibt kein Element, das in $A$ liegt und in $\overline{A}$.                                  |
| $A \cup \overline{A} = X$                              | Jedes Element liegt in $A$ oder in $\overline{A}$.                                             |
| $\overline{\overline{A}} = A$                          | Doppelte Verneinung.                                                                           |
| $A = (A \cap B) \cup (A \cap \overline{B})$            | $A$ wird zerlegt in einen Teil, der in $B$ liegt, und einen Teil, der in $\overline{B}$ liegt. |
| $\overline{A} \cup \overline{B} = \overline{A \cap B}$ | Gesetz von de Morgan                                                                           |
| $\overline{A} \cap \overline{B} = \overline{A \cup B}$ | Gesetz von de Morgan                                                                           |

<div id="skript-aufgabe-1"></div>

## Zufallsexperimente

In der Stochastik treffen wir Aussagen über (vermeintlich) zufällige Ausgänge von Vorgängen aus der alltäglichen Welt. Wir präzisieren:

- Ein **Zufallsexperiment** ist ein Vorgang, der unter genau festgelegten Bedingungen durchgeführt wird und einen (vermeintlich) zufälligen Ausgang besitzt.
- Die möglichen Ausgänge eines Zufallsexperiments werden **Ergebnisse** des Zufallsexperiments genannt.
- Die einzelnen Ergebnisse werden zu der **Ergebnismenge** zusammengefasst. Die Ergebnismenge wird häufig mit $S$ oder $\Omega$ (lies: Omega) bezeichnet.
- Ein **Ereignis** besteht aus mehreren Ergebnissen. Ereignisse sind also Teilmengen des Ergebnisraums. Ein Ereignis $A$ tritt ein, falls der Ausgang des Zufallsexperiments ein Ergebnis aus $A$ ist.
- Ergebnisse werden auch **Elementarereignisse** genannt.
- Das **Gegenereignis** eines Ereignisses $A$ wird mit $\overline{A}$ bezeichnet und enthält alle Ergebnisse, die nicht in $A$ liegen.
- Das **sichere Ereignis** ist die gesamte Ergebnismenge, es tritt immer ein.
- Das **unmögliche Ereignis** ist die leere Menge, es tritt nie ein.

<div id="skript-aufgabe-2"></div>

## Wahrscheinlichkeiten - Einführung

Eine Wahrscheinlichkeitsverteilung $P$ eines Zufallsexperiments, ordnet dann jedem Ereignis des Zufallsexperiments eine Zahl zwischen 0 und 1 zu.

### Beispiel: Einmaliger Münzwurf

- Ergebnismenge: $S = \\{1,  2,  3,  4,  5,  6\\}$
  - Ergebnisse: $\\{1\\}, \\{2\\}, \\{3\\}, \\{4\\}, \\{5\\}, \\{6\\}$
  - $P(\\{1\\}) = \frac{1}{6}$, $P(\\{2\\}) = \frac{1}{6}$, $P(\\{3\\}) = \frac{1}{6}$, $P(\\{4\\}) = \frac{1}{6}$, $P(\\{5\\}) = \frac{1}{6}$, $P(\\{6\\}) = \frac{1}{6}$
- $A$: Es wird eine Zahl größer als 4 geworfen.
  - $A = \\{5,  6\\}$
  - $P(A) = \frac{2}{6} = \frac{1}{3}$
- $\overline{A}$: Es wird eine Zahl kleiner als 5 geworfen.
  - $\overline{A} = \\{1, 2, 3, 4\\}$
  - $P(\overline{A})=\frac{4}{6} = \frac{2}{3}$
- $B$: Es wird eine geraden Zahl geworfen.
  - $B=\\{2, 4, 6\\}$
  - $P(B)=\frac{3}{6} = \frac{1}{2}$
- $\overline{A}\cup B$: Es wird eine Zahl kleiner als 5 oder eine gerade Zahl geworfen.
  - $\overline{A}\cup B= \\{1, 2, 3, 4, 6\\}$
  - $P(\overline{A}\cup B) = \frac{5}{6}$
- $(A\cap\overline{B}) \cup (\overline{A}\cap B)$: Es wird entweder eine Zahl größer als 4 oder eine gerade Zahl geworfen.
  - $(A\cap\overline{B}) \cup (\overline{A}\cap B)= \\{2, 4, 5\\}$
  - $P((A\cap\overline{B}) \cup (\overline{A}\cap B))=\frac{3}{6} =\frac{1}{2}$

### Beispiel: Zweimaliger Münzwurf

- Ergebnismenge: $S = \\{KK, KZ, ZK, ZZ\\}$
  - Ergebnisse: $\\{KK\\}, \\{KZ\\}, \\{ZK\\}, \\{ZZ\\}$
  - $P(\\{KK\\}) = 0{,}25$, $P(\\{KZ\\}) = 0{,}25$, $P(\\{ZK\\}) = 0{,}25$, $P(\\{ZZ\\}) = 0{,}25$
- $A$: Es wird das Gleiche geworfen.
  - $A = \\{KK, ZZ\\}$
  - $P(A) = 0{,}5$
- $\overline{A}$: Es wird etwas Unterschiedliches geworfen.
  - $\overline{A} = \\{KZ, ZK\\}$
  - $P(\overline{A}) =0{,}5$
- $B$: Es wird die Kombination Kopf-Zahl geworfen.
  - $B=\\{KZ\\}$
  - $P(B)=\frac{1}{4}$
- $\overline{A}\cap{\overline{B}}$: Es wird weder das Gleiche noch die Kombination Kopf-Zahl geworfen.
  - $\overline{A}\cap{\overline{B}}=\\{ZK\\}$
  - $P(\overline{A}\cap{\overline{B}})=\frac{1}{4}$

### Beispiel: Häufigkeit von Buchstaben

Die 30 Buchstaben des Alphabets (a-z, ä, ö, ü, ß) treten in Texten mit unterschiedlichen Häufigkeiten auf (untersucht wurde 99.586 Buchstaben):

<figure>
  <img src="buchstaben.png"><figcaption>https://de.wikipedia.org/wiki/Buchstabenhäufigkeit</figcaption>
</figure>

Wir betrachten das Zufallsexperiment, bei dem ein Buchstabe zufällig ausgewählt wird.

- Ergebnismenge: $S = \\{a, b, c, \ldots \\}$
  - Ergebnisse: $\\{a\\}, \\{b\\}, \\{c\\}, \ldots$
  - $P(\\{a\\}) = 0{,}0560$, $P(\\{b\\}) = 0{,}0219$, $P(\\{c\\}) = 0{,}0340$, $\ldots$
- $A$: Es wird ein Vokal ausgewählt (ohne Umlaute).
  - $A = \\{a, e, i, o, u\\}$
  - $P(A) = 0{,}056+0{,}1611+0{,}0905+0{,}0232+0{,}0370=0{,}3678$
- $B$: Es wird ein Buchstabe aus der ersten Hälfte (a-o) des Alphabets ausgewählt.
  - $B = \\{a,  b,  c,  \ldots ,  o\\}$
  - $P(B)=0{,}0560 + 0{,}0219 + 0{,}0340 + \ldots + 0{,}0251 = 0{,}7066$
- $A\cap \overline{B}$: Es wird ein Vokal ausgewählt, der sich in der zweiten Hälfte (p-ß) des Alphabets befindet.
  - $A\cap\overline{B} = \\{u\\}$
  - $P(A\cap\overline{B}) = 0{,}0370$

<div id="skript-aufgabe-3"></div>

## Laplace-Experiment

In einfachen Alltagssituationen funktioniert unser intuitiver Umgang mit Wahrscheinlichkeiten oft gut (wie in den obigen Beispielen), und wir können mit einfachen Methoden die Wahrscheinlichkeiten berechnen.

Ein Laplace-Experiment ist ein Zufallsexperiment, bei dem alle Ergebnisse die gleiche Wahrscheinlichkeit besitzen. Die Wahrscheinlichkeit eines Ereignisses $A$ ist damit:

$$
P(A) = \frac{\text{Anzahl Ergebnisse in } A}{\text{Gesamtanzahl der Ergebnisse}}
$$

### Beispiel: Würfelwurf

Würfelwurf: Es sei $A$ das Ereignis „Es wird eine Primzahl geworfen.“ $\Rightarrow A = \\{2, 3, 5\\} $
Dann gilt:

$$
P(A) = \frac{3}{6} = \frac{1}{2}
$$

### Beispiel: Roulette

Es sei $A$ das Ereignis „Die Kugel landet auf einem roten Feld.“
Dann gilt:

$$
P(A) = \frac{18}{37}
$$

<figure>
  <img src="ChatGPTImage19.Apr.2025,14_05_47.png">
  <figcaption>KI-generiert mit ChatGPT</figcaption>
</figure>

<div id="skript-aufgabe-5"></div>

## Relative Häufigkeiten

Relative Häufigkeiten (Aussagen über die Vergangenheit) können als Wahrscheinlichkeiten (Aussagen über die Zukunft) interpretiert werden.

### Beispiel: Lieblingsgerichte

Aus persönlichen Beobachtungen sei bekannt, dass 50&nbsp;% aller Kinder am liebsten Pizza essen, 30&nbsp;% Pommes und 20&nbsp;% Nudeln mit Ketchup. Dann ist die Wahrscheinlichkeit, dass ein zufällig ausgewähltes Kind am liebsten Pommes isst, 30&nbsp;%.

### Beispiel: Spicken

In einer Klausur spicken 2 von 20 Schülern. Dann ist die Wahrscheinlichkeit, dass ein zufällig ausgewählter Schüler spickt, $\frac{2}{20}$ oder 10&nbsp;%.

<div id="skript-aufgabe-4"></div>

Das **Gesetz der großen Zahlen** beschreibt den Zusammnehang zwischen Laplace-Wahrscheinlochkeiten und relativen Häufigkeiten genauer.

## Axiome von Kolmogorov

Eine solide mathematische Fundierung der Stochastik wurde erst in den 1930er Jahren von Andrej Nikolajewitsch Kolmogorov (1903-1987) entwickelt. Kolmogorov formulierte die folgenden Grundsätze (Axiome), aus denen sich dann weitere Rechenregeln folgern lassen.
Betrachtet wird ein Zufallsexperiment mit Ergebnismenge $S$ und Ereignissen $A$ und $B$. Eine Wahrscheinlichkeitsverteilung $P$ ordnet jeder Teilmenge von $S$, also jedem Ereignis, eine reelle Zahl zu, so dass gilt:

- $P(A)\geq 0$
- $P(S)=1$
- $P(A\cup B)=P(A)+P(B)$, falls $A\cap B=\emptyset$,

für alle Teilmenge $A$ und $B$ von $S$.

### Folgerungen

1. $P(\emptyset)=0$
2. Alle Wahrscheinlichkeiten liegen immer zwischen einschließlich 0 und einschließlich 1.
3. **Satz von der Gegenwahrscheinlichkeit:** $P(\overline{A})=1-P(A)$. Beispiel: Aus $P(A)=0{,}3$ folgt $P(\overline{A})=1-0{,}3=0{,}7$.
4. **Zerlegung von Ereignissen:** $P(B)=P(A\cap B)+P(\overline{A}\cap B)$
5. **Satz von Sylvester:** $P(A\cup B)=P(A)+P(B)-P(A\cap B)$ Hieraus folgt, dass wir, wenn drei der vier Wahrscheinlichkeiten $P(A)$, $P(B)$, $P(A\cap B)$ und $P(A\cup B)$ bekannt sind, die vierte berechnen können.
   Beispiel: Aus $P(A)=0{,}3$, $P(B)=0{,}4$ und $P(A\cap B)=0{,}2$ folgt $P(A\cup B)=0{,}3+0{,}4-0,2=0{,}5$.

### Exkurs: Beweise

1. $P(\emptyset)=P(\emptyset\cup\emptyset)=P(\emptyset)+P(\emptyset)$. Es folgt $P(\emptyset)=0$.
2. Aus $X=A\cup\overline{A}$ folgt $P(X)=P(A)+P(\overline{A})$ und so $1=P(A)+P(\overline{A})$. Da $P(\overline{A})\geq 0$ muss $P(A)\leq 1$ gelten.
3. Aus $1=P(A)+P(\overline{A})$ folgt $P(\overline{A})=1-P(A)$.
4. Wir zerlegen $B=(A\cap B)\cup (\overline{A}\cap B)$. Da $(A\cap B)\cap(\overline{A}\cap B)=\emptyset$ folgt $P(B)=P(A\cap B)+P(\overline{A}\cap B)$.
5. Es gilt $A\cup B=(A\cap\overline{B}) \cup (A\cap B) \cup (\overline{A}\cap B)$. Damit folgt

$$
\begin{align*}
P(A\cup B)&=P(A\cap\overline{B}) + P(A\cap B) + P(\overline{A}\cap B)\\
&=P(A)-P(A\cap B) + P(A\cap B) + P(B)-P(A\cap B)\\
&=P(A)+P(B)-P(A\cap B).
\end{align*}
$$

<!--
### Noch einzufügen: einfache Wahrscheinlichkeiten mit Mengenoperationen, dazu auch

Ausschließendes Oder: Die Wahrscheinlichkeit für entweder $A$ oder $B$ (aber nicht $A$ und $B$ gleichzeitig) ist $P(A\cup B)- P(A\cap B)=P(A\cap\overline{B})+P(\overline{A}\cap B)$.
-->

<div id="skript-aufgabe-6"></div>

## Venn-Diagramme

Die Mengenoperationen und Axiome von Kolmogorov mit ihren Folgerungen lassen sich anschaulich anhand sogenannter Venn-Diagramme nachvollziehen: Ereignisse können als Teilflächen einer Fläche $X$ interpretiert werden. Die Wahrscheinlichkeiten der Ereignisse entsprechen dann den Inhalten dieser Teilflächen. Der Inhalt der Fläche $X$ ist nach Definition 1. Wir erhalten z.B.:

| $P(B)$                                                   | $P(A\cap B)$                                              | $P(\overline{A}\cap B)$                                   | $P(A\cup B)$                                              | $P(A\cup B)-P(A\cap B)$                                   |
| -------------------------------------------------------- | --------------------------------------------------------- | --------------------------------------------------------- | --------------------------------------------------------- | --------------------------------------------------------- |
| <figure><img src="v1.png" style="width: 15vw"> </figure> | <figure> <img src="v2.png" style="width: 15vw"> </figure> | <figure> <img src="v3.png" style="width: 15vw"> </figure> | <figure> <img src="v4.png" style="width: 15vw"> </figure> | <figure> <img src="v5.png" style="width: 15vw"> </figure> |

<div id="skript-aufgabe-7"></div>
