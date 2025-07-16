---
layout: skript
title: Hypothesentests
description: Hypothesentests - Skript
lernbereich: hypothesentests
---

## Einführung

Häufig stehen wir vor der Aufgabe, Hypothesen (Vermutungen) über eine Grundgesamtheit zu überprüfen. Zum Beispiel:

- Eine Schule hat ein neues pädagogisches Konzept eingeführt, das gezielt die Lernmotivation und Selbstorganisation der Schülerinnen und Schüler fördern soll. Es wird vermutet, dass dadurch mehr Lernende das Klassenziel erreichen. Nun soll überprüft werden, ob sich die Erfolgsquote im Vergleich zu den Vorjahren verbessert hat.
- Es besteht die Vermutung, dass der vermehrte Einsatz von Elektrofahrzeugen zu einer besseren Luftqualität in Städten führt. Es soll geklärt werden, ob sich Luftschadstoffwerte – etwa Feinstaub- oder Stickoxidkonzentrationen – im Vergleich zu früheren Jahren verringert haben.
- Ein Unternehmen hat einen neuen Algorithmus zur Erkennung von Hassrede in sozialen Netzwerken entwickelt. Es soll geprüft werden, ob dieser Algorithmus zuverlässiger arbeitet als das bisher eingesetzte Verfahren.

In der Praxis ist es häufig aus zeitlichen, organisatorischen oder finanziellen Gründen nicht möglich, alle Elemente einer Grundgesamtheit vollständig zu untersuchen (Vollerhebung). Stattdessen wird eine Stichprobe herangezogen, um auf die Grundgesamtheit zu schließen. Dieses Vorgehen bezeichnet man als **Hypothesentest**.

Mit der zunehmenden Digitalisierung erscheinen Vollerhebungen heute zwar realistischer als früher, dennoch bleibt die Stichprobe in vielen Situationen der praktikablere Weg.

Damit die Ergebnisse eines Hypothesentests verlässlich und aussagekräftig sind, müssen bestimmte Voraussetzungen erfüllt sein:

- Die Stichprobe muss repräsentativ sein – also zufällig gezogen, unverzerrt und typisch für die Gesamtgruppe.
- Der Stichprobenumfang muss groß genug sein, damit zufällige Schwankungen möglichst gering bleiben.
- Die Fragestellung muss eindeutig entscheidbar sein, in der Regel im Sinne einer Ja/Nein-Aussage, z. B. „Stimmt die Behauptung?“ oder „Hat sich etwas verändert?“

Das grundlegende Ziel eines Hypothesentests besteht darin, zu prüfen, ob die beobachteten Daten mit einer vorher aufgestellten Behauptung über die Grundgesamtheit vereinbar sind.

### Beispiel: Verspätete Schüler

Laut langjähriger Erfahrung und nach Meinung der Schüler beträgt der Anteil der Schüler, die verspätet zum Unterricht erscheinen, 10 %. Eine Lehrerin vermutet nun, dass sich dieser Anteil erhöht hat.

Sie beobachtet eine Stichprobe von 50 Schülern und stellt fest, dass 6 davon verspätet erscheinen. Das sind mehr als 10 %, was die Vermutung der Lehrerin zu bestätigen scheint. Allerdings könnte diese Abweichung auch rein zufällig sein.

Was nun? Die Lehrerin könnte die Zahlen in ihrem Sinne interpretieren und behaupten, dass mehr als 10 % der Schüler zu spät kommen. Die Schüler wiederum könnten argumentieren, dass eine solche geringe Abweichung keine Beweiskraft habe.

### Prinzipien eines fairen Hypothesentests

Ein Hypothesentest soll standardisiert, objektiv und reproduzierbar sein. Daher gilt das Grundprinzip: **Erst das Verfahren, dann die Daten.** Vor der Datenerhebung muss genau definiert werden, bei welchem Beobachtungsergebnis welche Entscheidung getroffen wird.

Im Beispiel könnten sich Lehrerin und Schüler **vorab** auf folgende Regel einigen:

> Wenn mehr als 7 von 50 Schülern zu spät kommen, wird angenommen, dass der Anteil verspäteter Schüler über 10 % liegt. Andernfalls wird weiterhin davon ausgegangen, dass der Anteil 10 % beträgt.

Erst **nachdem** diese Regel festgelegt wurde, wird die Datenerhebung durchgeführt. Das Ergebnis wird anschließend nach der vorher definierten Regel interpretiert – unabhängig von persönlichen Meinungen oder Interessen.

## Grundbegriffe

Ein Hypothesentest basiert auf zwei sich ausschließenden Aussagen:

- **Nullhypothese** ($H_0$): Die Ausgangsvermutung, die überprüft werden soll. Sie beschreibt in der Regel den „Normalzustand“ oder eine Annahme, an der gezweifelt wird.
- **Gegenhypothese** ($H_1$): Die Alternative zur Nullhypothese. Sie beschreibt den vermuteten neuen Zustand oder eine Abweichung vom bisherigen Wert.

Je nachdem, welches Ergebnis die Stichprobe liefert, treffen wir eine Entscheidung: Wir behalten $H_0$ bei oder verwerfen sie zugunsten von $H_1$.

Dabei kann es zu zwei Arten von Fehlern kommen:

| | $H_0$ ist wahr. | $H_1$ ist wahr. |
| $H_0$ wird beibehalten. | ✅ Richtige Entscheidung | ⚠️ Fehler 2. Art (auch $\beta$-Fehler) |
| $H_0$ wird verwerfen. | ⚠️ Fehler 1. Art (auch $\alpha$-Fehler) | ✅ Richtige Entscheidung |

Solche Fehler lassen sich prinzipiell nicht vermeiden – es sei denn, wir entscheiden uns immer für $H_0$ oder immer für $H_1$. Das ist jedoch nicht zielführend. Der Grund dafür liegt in der Natur einer Stichprobe: Wir können niemals mit absoluter Sicherheit sagen, was für die gesamte Grundgesamtheit gilt.

Stattdessen versuchen wir, zumindest die Wahrscheinlichkeiten für Fehler möglichst klein zu halten. Dabei zeigt sich jedoch ein grundlegender Zielkonflikt: Wird die Wahrscheinlichkeit für einen Fehler 1. Art (fälschliches Verwerfen von $H_0$) gesenkt, steigt in der Regel die Wahrscheinlichkeit für einen Fehler 2. Art (fälschliches Beibehalten von $H_0$) – und umgekehrt.

Der Fehler 2. Art ist oft schwieriger zu behandeln, da die tatsächliche Wahrscheinlichkeit unter der Gegenhypothese ($H_1$) meist nicht genau bekannt ist. Zudem liegt der Schwerpunkt der Analyse häufig auf dem Fehler 1. Art, da das Verwerfen einer, oft begründeten, Nullhypothese schwerwiegendere Folgen haben kann als das Ablehnen einer möglicherweise spekulativen Gegenhypothese.

Aus diesem Grund konzentriert man sich in der Praxis häufig auf die Kontrolle des Fehlers 1. Art. Dessen maximale Wahrscheinlichkeit bezeichnen wir als **Signifikanzniveau**.

Um auf Basis eines Stichprobenergebnisses schließlich eine Entscheidung zu treffen, wird eine **Entscheidungsregel** benötigt. Diese teilt den Wertebereich in einen **Annahmebereich** $A$ und einen **Ablehnungsbereich** $\overline{A}$ ein.

Im Übrigen sprechen wir von einem **linksseitigen** Test, falls die Gegenhypothese kleinere Wahrscheinlichkeiten als die Nullhypothese vermutet (z.B. $H_1: p<0{,2}$). Dagegen liegt ein **rechtsseitiger** Test vor, wenn die Gegenhypothese größere Wahrscheinlichkeiten als die Nullhypothese vermutet (z.B. $H_1: p>0{,2}$).

### Grundbegriffe im Beispiel

**Was ist das grundlegende Setting?**

- Testgröße: Anzahl der verspäteten Schüler
- Stichprobenumfang: $n=50$
- Nullhypothese $H_0$: $p=0{,}1$
- Gegenhypothese $H_1$: $p>0{,}1$
- Rechtsseitiger Test

**Wie lautet die Entscheidungsregel?**

- Annahmebereich $A=\\{0{,}1{,}2{,}...{,}7\\}$
- Ablehnungsbereich $\overline{A}=\\{8{,}9{,}10{,}...{,}50\\}$

**Wie wird entschieden?**

In der Stichprobe kamen 6 Schüler verspätet. Da $6$ im Annahmebereich liegt, wird die Nullhypothese beibehalten.

**Was bedeutet die Fehler 1. und 2. Art im Sachzusammenhang?**

- Fehler 1. Art: Man entscheidet sich dafür, dass mehr als 10 % der Schüler zu spät, obwohl in Wirklichkeit der Anteil genau 10 % beträgt.

- Fehler 2. Art: Man entscheidet sich dafür, dass genau 10 % der Schüler zu spät kommen, obwohl in Wirklichkeit der Anteil höher ist.

**Wie hoch ist die maximale Wahrscheinlichkeit für den Fehler 1. Art bzw. das erzielte Signifikanznevau im Sachzusammenhang?**

Ein Fehler 1. Art tritt ein, wenn die Nullhypothese wahr ist (also $p = 0{,}1$ gilt), wir jedoch aufgrund des Testergebnisses $H_0$ verwerfen. Dies geschieht, wenn die beobachtete Anzahl verspäteter Schüler im Ablehnungsbereich $\overline{A} = \{8{,}9{,}10{,}\dotsc{,}50\}$ liegt. Die maximale Wahrscheinlichkeit dafür – das Signifikanzniveau – beträgt:

$$
P(X\geq 8)=Bcd(8;50;200;0{,}1)=0{,}1221
$$

**Wie hoch ist die Wahrscheinlichkeit für den Fehler 2. Art?**

Ein Fehler 2. Art tritt ein, wenn die Gegenhypothese wahr ist (d. h. $p > 0{,}1$), wir jedoch die Nullhypothese beibehalten. Ohne zusätzliche Informationen über den tatsächlichen Wert von $p$ unter der Gegenhypothese kann diese Wahrscheinlichkeit nicht bestimmt werden.

{%include info.html
index="1"
frage="Linksseitiger Hypothesentest: Anwendung der Entscheidungsregel und Bestimmung des Signifikanzniveaus"
antwort="
Beispiel: Gegeben ist ein Hypothesentest mit:

- $n=200$
- $H_0$: $p=0{,}4$
- $H_1$: $p<0{,}4$
- $A=\\{71,72,...,200\\}$ und $\overline{A}=\\{0,1,...,70\\}$
- Stichprobenergebnis: $k=69$

Anwendung der Entscheidungsregel: Da $69\in\overline{A}$ wird die Nullhypothese abgelehnt und die Gegenhypothese angenommen.

Bestimmung des Signifikanzniveaus: $P(X\leq 70) = Bcd(0;70;200;0{,}4) = 0{,}0844$

"
%}

<div id="skript-aufgabe-1"></div>

{%include info.html
index="2"
frage="Rechtsseitiger Hypothesentest: Anwendung der Entscheidungsregel und Bestimmung des Signifikanzniveaus"
antwort="
Beispiel: Gegeben ist ein Hypothesentest mit:

- $n=200$
- $H_0$: $p=0{,}4$
- $H_1$: $p>0{,}4$
- $A=\\{0,1,2,...,90\\}$ und $\overline{A}=\\{91,92,...,200\\}$
- Stichprobenergebnis: $k=88$

Anwendung der Entscheidungsregel: Da $88\in A$ wird die Nullhypothese angenommen und die Gegenhypothese abgelehnt.

Bestimmung des Signifikanzniveaus: $P(X\geq 91) = Bcd(91;200;200;0{,}4) = 0{,}0655$

"
%}

<div id="skript-aufgabe-2"></div>

<!-- ## Exkurs: p-Hacking-->

## Herleitung der Entscheidungsregel

Wie gelangen wir zur Entscheidungsregel? Oder anders formuliert: Wie lassen sich Annahme- und Ablehnungsbereich der Nullhypothese festlegen?

Das zentrale Prinzip lautet: Wir legen eine maximal tolerierte Wahrscheinlichkeit für einen Fehler 1. Art fest – also die Wahrscheinlichkeit, dass die Nullhypothese fälschlich verworfen wird, obwohl sie zutrifft. Diese Vorgabe wird als Signifikanzniveau bezeichnet und mit dem Symbol $\alpha$ dargestellt. In der Praxis wählt man häufig einen Wert $\alpha=5\%$.

Der Ablehnungsbereich wird anschließend so gewählt, dass die Wahrscheinlichkeit für einen Fehler 1. Art höchstens $\alpha$ beträgt.
Gleichzeitig soll dieser Bereich möglichst groß sein, damit die Wahrscheinlichkeit für einen Fehler 2. Art (fälschliches Beibehalten von $H_0$, obwohl $H_1$ zutrifft) möglichst gering wird – im Rahmen des vorgegebenen Signifikanzniveaus.

{%include info.html
index="3"
frage="Linksseitiger Hypothesentest: Herleitung der Entscheidungsregel"
antwort="
Beispiel: Gegeben sei ein Hypothesentest mit Stichprobenumfang $n=200$ und Signifikanzniveau $\alpha=0{,}05$. Außerdem gelte

|Nullhypothese | Gegenhypothese |
| $H_0: 0{,}4$ | $H_1: p<0{,}4$ |
| $A=\\{k+1,k+2,...,200\\}$ | $\overline{A}=\\{0,1,2,...,k\\}$ |

Der Annahme- und Ablehnungsbereich ist von der abgebildeten Gestalt, da wir uns wegen $H_1: p<0{,}4$ bei kleinen Stichprobenergebnissen für $H_1$ entscheiden, und bei großen für $H_0$. Außerdem haben wir eine Unbekannte $k$ eingefügt, um die Bereiche prägnant beschreiben zu können. Gesucht ist nun das größte $k$, so dass $P(X\leq k)<0{,}05$. Mit dem Taschenrechner oder Tafelwerk ermitteln wir:

- $P(X\leq 68)=Bcd(0;68;200;0{,}4)=0{,}0475<0{,}05$
- $P(X\leq 69)=Bcd(0;69;200;0{,}4)=0{,}0639>0{,}05$

Damit folgt $k=68$, und somit $A=\\{69,70,...,200\\}$ und $\overline{A}=\\{0,1,2,...,68\\}$.
"
%}

<div id="skript-aufgabe-3"></div>

{%include info.html
index="4"
frage="Rechtssseitiger Hypothesentest: Herleitung der Entscheidungsregel"
antwort="
Beispiel: Gegeben sei ein Hypothesentest mit Stichprobenumfang $n=200$ und Signifikanzniveau $\alpha=0{,}02$. Außerdem gelte

|Nullhypothese | Gegenhypothese |
| $H_0: 0{,}4$ | $H_1: p>0{,}4$ |
| $A=\\{0,1,2,...,k-1\\}$ | $\overline{A}=\\{k,k+1,...,200\\}$ |

Der Annahme- und Ablehnungsbereich ist von der abgebildeten Gestalt, da wir uns wegen $H_1: p>0{,}4$ bei großen Stichprobenergebnissen für $H_1$ entscheiden, und bei kleinen für $H_0$. Außerdem haben wir eine Unbekannte $k$ eingefügt, um die Bereiche prägnant beschreiben zu können. Gesucht ist nun das kleinste $k$, so dass $P(X\geq k)<0{,}02$. Mit dem Taschenrechner oder Tafelwerk ermitteln wir:

- $P(X\geq 94)=Bcd(94;200;200;0{,}4)=0{,}0263>0{,}02$
- $P(X\geq 95)=Bcd(95;200;200;0{,}4)=0{,}0188<0{,}02$

Damit folgt $k=95$, und somit $A=\\{0,1,2,...,94\\}$ und $\overline{A}=\\{95,96,...,200\\}$.
"
%}

<div id="skript-aufgabe-4"></div>

{%include info.html
index="5"
frage="Linksseitiger Hypothesentest: Herleitung der Entscheidungsregel (ohne Strukturhilfe)"
antwort="siehe oben"%}

<div id="skript-aufgabe-5"></div>

{%include info.html
index="6"
frage="Rechtsseitiger Hypothesentest: Herleitung der Entscheidungsregel (ohne Strukturhilfe)"
antwort="siehe oben"%}

<div id="skript-aufgabe-6"></div>
