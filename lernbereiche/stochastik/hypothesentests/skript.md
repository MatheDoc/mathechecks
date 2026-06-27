---
layout: module
title: Hypothesentests - Skript
description: Lernbereich Hypothesentests, Modul Skript.
page_context: Lernbereich
nav: dashboard
body_class: page-module
module_key: skript
published: true
lernbereich: hypothesentests
gebiet: stochastik
permalink: /lernbereiche/stochastik/hypothesentests/skript.html
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

"Wenn mehr als 7 von 50 Schülern zu spät kommen, wird angenommen, dass der Anteil verspäteter Schüler über 10 % liegt. Andernfalls wird weiterhin davon ausgegangen, dass der Anteil 10 % beträgt."

Erst **nachdem** diese Regel festgelegt wurde, wird die Datenerhebung durchgeführt. Das Ergebnis wird anschließend nach der vorher definierten Regel interpretiert – unabhängig von persönlichen Meinungen oder Interessen.

## Grundbegriffe

Ein Hypothesentest basiert auf zwei sich ausschließenden Aussagen:

- **Nullhypothese** ($H_0$): Die Ausgangsvermutung, die überprüft werden soll. Sie beschreibt in der Regel den „Normalzustand“ oder eine Annahme, an der gezweifelt wird.
- **Gegenhypothese** ($H_1$): Die Alternative zur Nullhypothese. Sie beschreibt den vermuteten neuen Zustand oder eine Abweichung vom bisherigen Wert.

Je nachdem, welches Ergebnis die Stichprobe liefert, treffen wir eine Entscheidung: Wir behalten $H_0$ bei oder verwerfen sie zugunsten von $H_1$.

Dabei kann es zu zwei Arten von Fehlern kommen:

| | $H_0$ ist wahr. | $H_1$ ist wahr. |
| $H_0$ wird beibehalten. | ✅ Richtige Entscheidung | ⚠️ Fehler 2. Art (auch $\beta$-Fehler) |
| $H_0$ wird verworfen. | ⚠️ Fehler 1. Art (auch $\alpha$-Fehler) | ✅ Richtige Entscheidung |

Solche Fehler lassen sich prinzipiell nicht vermeiden – es sei denn, wir entscheiden uns immer für $H_0$ oder immer für $H_1$. Das ist jedoch nicht zielführend. Der Grund dafür liegt in der Natur einer Stichprobe: Wir können niemals mit absoluter Sicherheit sagen, was für die gesamte Grundgesamtheit gilt.

Stattdessen versuchen wir, zumindest die Wahrscheinlichkeiten für Fehler möglichst klein zu halten. Dabei zeigt sich jedoch ein grundlegender Zielkonflikt: Wird die Wahrscheinlichkeit für einen Fehler 1. Art (fälschliches Verwerfen von $H_0$) gesenkt, steigt in der Regel die Wahrscheinlichkeit für einen Fehler 2. Art (fälschliches Beibehalten von $H_0$) – und umgekehrt.

Der Fehler 2. Art ist oft schwieriger zu behandeln, da die tatsächliche Wahrscheinlichkeit unter der Gegenhypothese ($H_1$) meist nicht genau bekannt ist. Zudem liegt der Schwerpunkt der Analyse häufig auf dem Fehler 1. Art, da das Verwerfen einer, oft begründeten, Nullhypothese schwerwiegendere Folgen haben kann als das Ablehnen einer möglicherweise spekulativen Gegenhypothese. Aus diesem Grund konzentriert man sich in der Praxis häufig auf die Kontrolle des Fehlers 1. Art.

Um auf Basis eines Stichprobenergebnisses schließlich eine Entscheidung zu treffen, wird eine **Entscheidungsregel** benötigt. Diese teilt den Wertebereich in einen **Annahmebereich** $A$ und einen **Ablehnungsbereich** $\overline{A}$ ein.

Im Übrigen sprechen wir von einem **linksseitigen** Test, falls die Gegenhypothese kleinere Wahrscheinlichkeiten als die Nullhypothese vermutet (z.B. $H_1: p<0{,}1$). Dagegen liegt ein **rechtsseitiger** Test vor, wenn die Gegenhypothese größere Wahrscheinlichkeiten als die Nullhypothese vermutet (z.B. $H_1: p>0{,}1$).

### Grundbegriffe im Beispiel

**Was ist das grundlegende Setting?**

- Testgröße: Anzahl der verspäteten Schüler
- Stichprobenumfang: $n=50$
- Nullhypothese $H_0$: $p=0{,}1$
- Gegenhypothese $H_1$: $p>0{,}1$
- Rechtsseitiger Test

**Wie lautet die Entscheidungsregel?**

- Annahmebereich $A=\\{0,1,2,\ldots,7\\}$
- Ablehnungsbereich $\overline{A}=\\{8,9,10,\ldots,50\\}$

**Wie wird entschieden?**

In der Stichprobe kamen 6 Schüler verspätet. Da $6$ im Annahmebereich liegt, wird die Nullhypothese beibehalten.

**Was bedeuten die Fehler 1. und 2. Art im Sachzusammenhang?**

- Fehler 1. Art: Man entscheidet sich dafür, dass mehr als 10 % der Schüler zu spät kommen, obwohl in Wirklichkeit der Anteil genau 10 % beträgt.

- Fehler 2. Art: Man entscheidet sich dafür, dass genau 10 % der Schüler zu spät kommen, obwohl in Wirklichkeit der Anteil höher ist.

**Wie hoch ist die maximale Wahrscheinlichkeit für den Fehler 1. Art im Sachzusammenhang?**

Ein Fehler 1. Art tritt ein, wenn die Nullhypothese wahr ist (also $p = 0{,}1$ gilt), wir jedoch aufgrund des Testergebnisses $H_0$ verwerfen. Dies geschieht dann, wenn die beobachtete Anzahl verspäteter Schüler im Ablehnungsbereich $\overline{A} = \\{8,9,10,\ldots,50\\}$ liegt. Die maximale Wahrscheinlichkeit dafür beträgt:

$$
\begin{align*}
P(X\geq 8)&=Bcd(8;50;50;0{,}1)\\
            &=0{,}1221
\end{align*}
$$

**Wie hoch ist die Wahrscheinlichkeit für den Fehler 2. Art?**


Zu Beginn eines Hypothesentests ist die Wahrscheinlichkeit für den Fehler 2. Art typischerweise
nicht bekannt – denn dazu müsste man wissen, welcher konkrete Wert des Parameters unter der
Gegenhypothese tatsächlich vorliegt. Die Gegenhypothese legt meist nur eine Richtung fest
(z. B. $p > p_0$), nicht einen bestimmten Wert. Ist dieser Wert jedoch aus anderen Gründen bekannt oder plausibel annehmbar, lässt sich der
Fehler 2. Art nachträglich berechnen – nachdem Annahme- und Ablehnungsbereich bereits
festgelegt wurden.


Angenommen wir wüssten also, dass der tatsächliche Anteil verspäteter Schüler bei $p = 0{,}2$ liegt, lässt sich die Wahrscheinlichkeit für den Fehler 2. Art berechnen.

Ein Fehler 2. Art tritt ein, wenn trotz $p = 0{,}2$ die Testgröße im Annahmebereich
$A = \{0,1,\ldots,7\}$ landet:

$$
\begin{align*}
P(X \leq 7 \mid p = 0{,}2) &= Bcd(7;50;50;0{,}2) \\
                             &= 0{,}2732
\end{align*}
$$

Das heißt: Liegt der wahre Anteil verspäteter Schüler bei 20 %, wird der Test dies in etwa 27 % der Fälle nicht erkennen.


{% include check-anker.html nummer=1 %}

{% include check-anker.html nummer=2 %}


<!-- ## Exkurs: p-Hacking-->

## Herleitung der Entscheidungsregel

Wie gelangen wir zur Entscheidungsregel? Oder anders formuliert: Wie lassen sich Annahme- und Ablehnungsbereich der Nullhypothese festlegen?

Das zentrale Prinzip lautet: Wir legen eine Schranke für die maximal tolerierte Wahrscheinlichkeit für einen Fehler 1. Art fest: das **Signifikanzniveau** $\alpha$. In der Praxis wählt man häufig einen Wert $\alpha=5\%$.

Der Ablehnungsbereich wird anschließend so gewählt, dass die Wahrscheinlichkeit für einen Fehler 1. Art höchstens $\alpha$ beträgt. Zugleich soll der Ablehnungsbereich im Rahmen des vorgegebenen Signifikanzniveaus möglichst groß sein, damit die Wahrscheinlichkeit für einen Fehler 2. Art (fälschliches Beibehalten von $H_0$, obwohl $H_1$ zutrifft) möglichst gering wird.

Wir betrachten zunächst die Herleitung der Entscheidungsregel für einen linksseitigen Test, bevor wir uns dem rechtsseitigen Test zuwenden. In beiden Fällen werden wir die Entscheidungsregel zunächst mit Strukturhilfe herleiten, bevor wir sie ohne Strukturhilfe formulieren.

{% include check-anker.html nummer=3 %}

Analog gilt das Vorgehen für den rechtsseitigen Test: Hier wird der Ablehnungsbereich am oberen Ende gesucht, und die Bedingung lautet $P(X\geq k) < \alpha$.

{% include check-anker.html nummer=4 %}

Sind die Struktur und das Verfahren einmal klar, können beide Testrichtungen auch ohne zusätzliche Struktur durchgeführt werden.

{% include check-anker.html nummer=5 %}

{% include check-anker.html nummer=6 %}



## Multiples-Testen-Problem

Ich glaube keiner Statistik, die ich nicht selbst gefälscht habe. – Winston Churchill. Es gibt viele
Möglichkeiten, Statistiken zu manipulieren: Die Stichprobe kann gezielt so gewählt werden, dass ein
gewünschtes Ergebnis herauskommt; unbequeme Daten werden weggelassen; oder die Hypothese wird so
formuliert, dass ein bestimmtes Ergebnis begünstigt wird.

Eine besonders tückische Methode ist das multiple Testen. Dabei werden mehrere Hypothesentests
durchgeführt, ohne die Ergebnisse der einzelnen Tests in Beziehung zueinander zu setzen. Jeder
einzelne Test kann dabei durchaus strikten Vorgaben genügen. Da der Fehler 1. Art jedoch prinzipiell
nicht ausgeschlossen werden kann, steigt die Wahrscheinlichkeit, dass mindestens ein Test ein
signifikantes Ergebnis liefert, mit der Anzahl der durchgeführten Tests.

### Beispiel

Angenommen, der Anteil der Bürger, die die Meinungsfreiheit als gefährdet ansehen, liegt bei 25 %.
Nun möchte ein politisches Institut untersuchen – oder besser: mutwillig konstatieren –, dass sich
dieser Anteil erhöht hat. Dazu werden $n$ Hypothesentests durchgeführt, jeweils mit einem
Signifikanzniveau von $\alpha = 5\,\%$. Da die Tests unabhängig voneinander sind und die
Nullhypothese in jedem Test zutrifft, beträgt die Wahrscheinlichkeit, dass mindestens ein Test
fälschlicherweise die Nullhypothese verwirft:

$$P(X \geq 1) = Bcd(1;n;n;0,05)$$

Die Tabelle zeigt diese Wahrscheinlichkeiten für verschiedene Werte von $n$:

| Anzahl $n$       |    1 |      5 |     10 |     20 |     50 |    100 |
| $P(X \geq 1)$    | 0,05 | 0,2262 | 0,4013 | 0,6415 | 0,9231 | 0,9941 |

Bereits nach 20 Tests liegt die Wahrscheinlichkeit, mindestens einmal fälschlicherweise die
Nullhypothese zu verwerfen, bei über 64 %. Genau diesen Test könnte das Institut als Beleg für die
Gefährdung der Meinungsfreiheit anführen – obwohl der wahre Anteil unverändert bei 25 % liegt und
kein echter Effekt nachgewiesen wurde.

