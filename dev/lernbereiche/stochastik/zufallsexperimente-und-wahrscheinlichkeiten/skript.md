---
layout: dev-module
title: Zufallsexperimente und Wahrscheinlichkeiten - Skript (Dev)
description: Dev-Lernbereich Zufallsexperimente und Wahrscheinlichkeiten, Modul Skript.
page_context: Lernbereich
nav: dashboard
body_class: page-module-designs
module_key: skript
published: true
lernbereich: zufallsexperimente-und-wahrscheinlichkeiten
gebiet: stochastik
permalink: /dev/lernbereiche/stochastik/zufallsexperimente-und-wahrscheinlichkeiten/skript.html
---

## Einführung

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
- Beispiel: Die Menge einer Spielgruppe von Kindern ist

  $$
  X = \{\text{Tobias},  \text{Jessica},  \text{Achmed},  \text{Lydia}\}.
  $$

  Dann ist die Teilmenge der Mädchen $A = \\{\text{Jessica},  \text{Lydia}\\}$.

- Ist $A$ eine Teilmenge von $X$, so bilden alle Elemente von $X$, die nicht in $A$ liegen, das Komplement von $A$. Das Komplement von $A$ wird mit $\overline{A}$ bezeichnet.
- Beispiel: Für $X = \\{1, 3, 4, 6, 8\\}$ und der Teilmenge $A = \\{3, 6\\}$ ist das Komplement $\overline{A} = \\{1, 4, 8\\}$.
- Beispiel: Für

  $$
  X = \{\text{Tobias},  \text{Jessica},  \text{Achmed},  \text{Lydia}\}
  $$

  und der Teilmenge der Mädchen $A = \\{\text{Jessica},  \text{Lydia}\\}$ ist das Komplement die Teilmenge der Jungen $\overline{A} = \\{\text{Tobias}, \text{Achmed}\\}$.



### Mengenoperationen

Sind $A$ und $B$ Teilmengen einer Menge $X$, so entstehen durch Vereinigungen, Durchschnitte und Komplemente neue Teilmengen. 

Wir betrachten einen Würfelwurf und die Menge $X$ aller möglichen Ergebnisse: $X=\\{1, 2, 3, 4, 5, 6\\}$. Nun können wir verschiedene Mengen von Ergebnissen beschreiben, z.B.:

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


{% include dev/check-anker.html nummer="1" %}

### Weitere Rechenregeln

Es seien $A$ und $B$ Teilmengen einer Menge $X$. Dann gelten die folgenden weiteren Rechenregeln:

| Aussage                                                | Bedeutung                                                                                      |
| ------------------------------------------------------ | ---------------------------------------------------------------------------------------------- |
| $A \cap \overline{A} = \emptyset$                      | Es gibt kein Element, das in $A$ liegt und in $\overline{A}$.                                  |
| $A \cup \overline{A} = X$                              | Jedes Element liegt in $A$ oder in $\overline{A}$.                                             |
| $\overline{\overline{A}} = A$                          | Doppelte Verneinung.                                                                           |
| $A = (A \cap B) \cup (A \cap \overline{B})$            | $A$ wird zerlegt in einen Teil, der in $B$ liegt, und einen Teil, der in $\overline{B}$ liegt. |
| $\overline{A} \cup \overline{B} = \overline{A \cap B}$ | Gesetz von de Morgan                                                                           |
| $\overline{A} \cap \overline{B} = \overline{A \cup B}$ | Gesetz von de Morgan                                                                           |




### Exkurs: Das Russellsche Paradoxon

Der Mengenbegriff erscheint zunächst klar und einfach: Eine Menge ist eine Zusammenfassung von verschiedenen Objekten. Doch wenn wir genauer hinschauen, können Widersprüche auftreten.
Ein bekanntes Beispiel ist das Russellsche Paradoxon:

Wir betrachten die Menge $M$, die alle Mengen enthält, die sich nicht selbst enthalten.
Nun stellen wir die Frage: Enthält $M$ sich selbst?

- Wenn ja, dann dürfte sie sich nicht enthalten (denn sie enthält ja nur Mengen, die sich nicht selbst enthalten).
- Wenn nein, dann müsste sie sich enthalten (denn sie erfüllt ja die Bedingung, sich nicht selbst zu enthalten).

Beides führt zu einem Widerspruch.
Dieses Paradoxon zeigt, dass der naive Mengenbegriff überarbeitet werden muss. Deshalb arbeiten Mathematiker heute mit exakteren, axiomatischen Grundlagen der Mengenlehre.

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

## Wahrscheinlichkeiten - Einführung

Eine Wahrscheinlichkeitsverteilung $P$ ordnet jedem Ereignis eines Zufallsexperiments eine Zahl zwischen $0$ und $1$ zu. Diese Zahl heißt **Wahrscheinlichkeit**. Je näher die Wahrscheinlichkeit an $1$ liegt, desto eher erwarten wir das Ereignis; je näher sie an $0$ liegt, desto weniger erwarten wir es.

Für ein endliches Zufallsexperiment gilt: Die Wahrscheinlichkeiten aller einzelnen Ergebnisse ergeben zusammen $1$. Die Wahrscheinlichkeit eines Ereignisses erhält man, indem man die Wahrscheinlichkeiten der Ergebnisse addiert, die zu diesem Ereignis gehören.

### Wahrscheinlichkeiten sprachlich lesen

Wahrscheinlichkeiten enthalten immer zwei Ebenen: den Sachzusammenhang und die Symbolsprache. Die Symbole $A$, $B$, $\overline{A}$, $A\cap B$ und $A\cup B$ beschreiben zuerst Ereignisse. Erst durch $P(\ldots)$ wird daraus eine Wahrscheinlichkeit.

Bei einem Würfelwurf sei

- $A$: Es wird eine Zahl größer als $4$ geworfen.
- $B$: Es wird eine gerade Zahl geworfen.

Dann bedeutet zum Beispiel:

| Symbol | Bedeutung im Sachzusammenhang |
|---|---|
| $P(A)$ | Wahrscheinlichkeit, dass eine Zahl größer als $4$ geworfen wird |
| $P(\overline{A})$ | Wahrscheinlichkeit, dass keine Zahl größer als $4$ geworfen wird |
| $P(A\cap B)$ | Wahrscheinlichkeit, dass die geworfene Zahl größer als $4$ und gerade ist |
| $P(A\cup B)$ | Wahrscheinlichkeit, dass die geworfene Zahl größer als $4$ oder gerade ist |
| $P(A\cap\overline{B})+P(\overline{A}\cap B)$ | Wahrscheinlichkeit, dass genau eine der beiden Bedingungen erfüllt ist |

Der nächste Check trainiert genau diese Übersetzung zwischen Text und Symbolsprache. Das zugehörige Beispiel nutzt denselben Aufgabentyp wie das Training: Zwei Ereignisse werden vorgegeben, und mehrere Wahrscheinlichkeitsausdrücke müssen im Sachzusammenhang gedeutet werden.

{% include dev/check-anker.html nummer="2" %}

### Beispiel: Buchstabenhäufigkeiten und Verschlüsselungen

Relative Häufigkeiten können helfen, unbekannte Texte zu untersuchen. In deutschen Texten treten Buchstaben nicht gleich häufig auf: $E$ ist sehr häufig, $Q$, $X$ und $Y$ sind selten. Wenn ein Text mit einer **monoalphabetischen Substitution** verschlüsselt wurde, wird jeder Klartextbuchstabe immer durch denselben Geheimtextbuchstaben ersetzt. Die Häufigkeitsstruktur bleibt dadurch teilweise erhalten.

Eine Caesar-Verschlüsselung ist ein besonders einfacher Fall einer solchen Substitution: Alle Buchstaben werden um dieselbe Anzahl Stellen verschoben. Bei allgemeinen monoalphabetischen Substitutionen ist die Zuordnung beliebig, aber die Idee der Häufigkeitsanalyse bleibt ähnlich. Je länger der Geheimtext ist, desto eher lassen sich häufige Geheimtextbuchstaben mit typischen häufigen Buchstaben deutscher Texte vergleichen.

{% include dev/widgets/widget-monoalphabetische-substitution.html %}


## Laplace-Experiment

Ein Laplace-Experiment ist ein Zufallsexperiment, bei dem alle Ergebnisse gleich wahrscheinlich sind. Dann genügt es, passende Ergebnisse zu zählen:

$$
P(A) = \frac{\text{Anzahl der Ergebnisse in } A}{\text{Anzahl aller Ergebnisse}}
$$

Beim Würfelwurf ist das Ereignis $A$: „Es wird eine Primzahl geworfen.“ Dann gilt $A=\lbrace 2,3,5\rbrace$ und damit

$$
P(A)=\frac{3}{6}=\frac{1}{2}.
$$

Wichtig ist die Voraussetzung der Gleichwahrscheinlichkeit. Ein normaler Würfel wird als Laplace-Experiment modelliert; ein gezinkter Würfel nicht. Beim europäischen Roulette gibt es $37$ mögliche Felder, nämlich $0$ bis $36$. Wenn jedes Feld gleich wahrscheinlich ist, hat das Ereignis „Die Kugel landet auf einem roten Feld“ die Wahrscheinlichkeit $\frac{18}{37}$.

{% include dev/widgets/widget-roulette.html %}


## Relative Häufigkeiten

Wenn Wahrscheinlichkeiten nicht durch gleich wahrscheinliche Ergebnisse begründet werden können, werden sie oft aus Beobachtungsdaten geschätzt. Die **relative Häufigkeit** eines Ereignisses ist der Anteil der beobachteten Fälle, in denen das Ereignis eingetreten ist:

$$
{} \text{relative Häufigkeit} = \frac{\text{absolute Häufigkeit des Ereignisses}}{\text{Gesamtanzahl der Beobachtungen}}
$$

Beispiel: Wenn in einer Klasse $2$ von $20$ Schülerinnen und Schülern während einer Klausur unerlaubte Hilfsmittel verwenden, beträgt die relative Häufigkeit $\frac{2}{20}=0{,}1$, also $10\,\%$. Als Wahrscheinlichkeitsmodell gelesen bedeutet das: Für eine zufällig ausgewählte Person aus dieser Klasse wird das Ereignis mit Wahrscheinlichkeit $0{,}1$ erwartet.

In den Aufgaben zum nächsten Check sind absolute Häufigkeiten für mehrere Teilgruppen gegeben. Entscheidend ist dann, zuerst die passende absolute Häufigkeit des gesuchten Ereignisses zu bestimmen und sie anschließend durch die Gesamtanzahl zu teilen.

{% include dev/check-anker.html nummer="3" %}

Das **Gesetz der großen Zahlen** erklärt, warum relative Häufigkeiten bei vielen Wiederholungen oft in die Nähe der zugrunde liegenden Wahrscheinlichkeit rücken. Es verbindet damit beobachtete Häufigkeiten mit Wahrscheinlichkeiten als Modell für zukünftige Zufallsexperimente.

## Exkurs: Axiome von Kolmogorov

Eine solide mathematische Fundierung der Stochastik wurde erst in den 1930er Jahren von Andrej Nikolajewitsch Kolmogorov (1903-1987) entwickelt. Kolmogorov formulierte die folgenden Grundsätze (Axiome), aus denen sich dann weitere Rechenregeln folgern lassen.
Betrachtet wird ein Zufallsexperiment mit Ergebnismenge $S$ und Ereignissen $A$ und $B$. Eine Wahrscheinlichkeitsverteilung $P$ ordnet jeder Teilmenge von $S$, also jedem Ereignis, eine reelle Zahl zu, so dass gilt:

- $P(A)\geq 0$
- $P(S)=1$
- $P(A\cup B)=P(A)+P(B)$, falls $A\cap B=\emptyset$,

für alle Teilmengen $A$ und $B$ von $S$.

### Folgerungen

1. $P(\emptyset)=0$
2. Alle Wahrscheinlichkeiten liegen immer zwischen einschließlich 0 und einschließlich 1.
3. **Satz von der Gegenwahrscheinlichkeit:** $P(\overline{A})=1-P(A)$.
4. **Zerlegung von Ereignissen:** $P(B)=P(A\cap B)+P(\overline{A}\cap B)$
5. **Satz von Sylvester:** $P(A\cup B)=P(A)+P(B)-P(A\cap B)$

### Beweise

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

{% include dev/check-anker.html nummer="4" %}


## Venn-Diagramme

Die Mengenoperationen und Axiome von Kolmogorov mit ihren Folgerungen lassen sich anschaulich anhand sogenannter Venn-Diagramme nachvollziehen: Ereignisse können als Teilflächen einer Fläche $X$ interpretiert werden. Die Wahrscheinlichkeiten der Ereignisse entsprechen dann den Inhalten dieser Teilflächen. Der Inhalt der Fläche $X$ ist nach Definition 1.

{% include dev/check-anker.html nummer="5" %}
