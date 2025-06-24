---
layout: skript
title: Binomialverteilung
description: Binomialverteilung - Skript
lernbereich: binomialverteilung
---

## Einführung

Ein **Bernoulli-Experiment** ist ein Zufallsexperiment mit nur zwei möglichen Ergebnissen: Treffer oder Niete. Die Wahrscheinlichkeit für einen Treffer wird in der Regel mit $p$ bezeichnet, für eine Niete mit $q=1-p$. Wird ein Bernoulli-Experiment $n$-mal hintereinander bei gleichbleibender Trefferwahrscheinlichkeit durchgeführt, so sprechen wir von einer **Bernoulli-Kette** der Länge $n$.
Eine Zufallsgröße, die bei einer Bernoulli-Kette die Anzahl der Treffer angibt, heißt **binomialverteilt**.

Mit anderen Worten: Beim zugrundeliegenden Zufallsexperiment einer binomialverteilten Zufallsgröße

- gibt es feste Anzahl an Versuchen (Stufen),
- gibt es in jedem Versuch genau zwei mögliche Ausgänge,
- bleibt die Wahrscheinlichkeit für Treffer und Niete in jedem Versuch gleich.

Aufgrund dieser klaren Struktur werden sich viele systematische Rechenverfahren ergeben. Zunächst ist es aber wichtig festzustellen, ob eine Zufallsgröße binomialverteilt ist oder nicht.

<div id="skript-aufgabe-1"></div>

## Die Bernoulli-Formel

Wir betrachten eine Bernoulli-Kette der Länge $n$ mit Trefferwahrscheinlichkeit $p$ und fragen nach der Wahrscheinlichkeit für genau $k$ Treffer. Das zugehörige Baumdiagramm hat folgende Gestalt:

{% include baumdiagramm-binomial.html %}

Um die Wahrscheinlichkeit für genau $k$ Treffer zu berechnen, benötigen wir die erstens Anzahl der Pfade mit genau $k$ Treffern und zweitens die Endwahrscheinlichkeit eines solchen Pfades.

- **Pfadanzahl:** Der sogenannte Binomialkoeffizient (lies: n über k)

  $$
    \begin{align}
    \binom{n}{k} & =\frac{n!}{k!\cdot (n-k)!}\\
    & =\frac{1\cdot 2 \cdot \ldots n}{(1\cdot 2 \cdot \ldots k)\cdot (1\cdot 2 \cdot \ldots (n-k))}
    \end{align}
  $$

  gibt diese Anzahl an Pfaden an. Er kann mit den meisten Taschenrechnern direkt bestimmt werden.

- **Pfadendwahrscheinlichkeit:** Jeder dieser Pfade hat nach der Pfadmultipliaktionsregel dieselbe Pfadwahrscheinlichkeit
  $$
  p^k \cdot (1−p)^{n−k},
  $$
  denn auf jedem dieser Pfade treten genau $k$ Treffer und $n−k$ Nieten auf.

Damit ergibt sich mit der Pfadadditionsregel die **Bernoulli-Formel** für genau $k$ Treffer:

$$
P(X=k)=\binom{n}{k}\cdot p^k\cdot (1-p)^{n-k}
$$

Diese Formel bildet die Grundlage für viele Wahrscheinlichkeitsberechnungen. Sie ist in einigen Taschenrechnern als Funktion integriert und in Tafelwerken dokumentiert.

### Berechnungen

{% include flip-card.html
frage="Eine Basketballspielerin habe eine Trefferwahrscheinlichkeit von 70 % und wirft 4 Mal. Wie groß ist die Wahrscheinlichkeit, dass sie genau 3 Treffer erzielt?"
antwort="

$$
\begin{align*}
P(X=4)&=\binom{4}{3}\cdot 0{,}7^3\cdot (1-0{,}7)^{4-3}\\
&=0{,}4116
\end{align*}
$$ "
%}

{% include flip-card.html
frage="Ein Virentest erkennt eine Infektion mit 92 % Wahrscheinlichkeit. Bei 12 getesteten infizierten Personen: Wie groß ist die Wahrscheinlichkeit, dass genau 11 positive Tests erfolgen?"
antwort="


$$

\begin{align*}
P(X=11)&=\binom{12}{11}\cdot 0{,}92^{11}\cdot 0{,}08^{12-11}\\
&=0{,}2855
\end{align*}

$$
" %}

{% include flip-card.html
frage="Die Wahrscheinlichkeit, dass ein Paket zu spät geliefert wird, beträgt 10 %. Bei 8 Sendungen: Wie wahrscheinlich ist es, dass genau 2 zu spät ankommen?"
antwort="


$$

\begin{align*}
P(X=2)&=\binom{8}{2}\cdot 0{,}1^2\cdot 0{,}9^{8-2}\\
&=0{,}1488
\end{align*}

$$
" %}

### Interpretationen

Durch den häufigen Einsatz von Taschenrechnern oder Tafelwerken gerät die Bedeutung der Bernoulli-Formel in den Hintergrund. Dabei ist gerade diese Formel die Grundlage dafür, dass solche Hilfsmittel Wahrscheinlichkeiten so zuverlässig angeben können. Es ist daher wichtig, die Formel auch inhaltlich interpretieren zu können.

<div id="skript-aufgabe-2"></div>

## Intervallwahrscheinlichkeiten



## Erwartungswert und Standardabweichung
$$
