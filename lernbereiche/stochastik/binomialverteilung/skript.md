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
frage="Eine Basketballspielerin habe von der Freiwurflinie eine Trefferwahrscheinlichkeit von 70 % und wirft 4 Mal. Wie groß ist die Wahrscheinlichkeit, dass sie genau 3 Treffer erzielt?"
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

Im vorherigen Abschnitt interessierten wir uns für die Wahrscheinlichkeit für **genau** $k$ Treffer. In diesem Abschnitt erweitern wir die Fragestellung und fragen nach der Wahrscheinlichkeit, dass die Anzahl der Treffer in einem vorgegebenen Bereich liegt.

### Beispiel
Eine Basketballsperin habe von der Dreierlinie eine Trefferwahrscheinlichkeit von 10% und wirft 20 Mal. Die Zufallsgröße $X$, die die Anzahl der Treffer angibt, ist binomialverteilt mit $n=20$ und $p=0{,}1$.

Wie groß ist die Wahrscheinlchkeit für höchstens 2 Treffer? Höchstens 2 Treffer bedeutet, dass sie 0, 1 oder 2 Mal trifft. Die gesuchte Wahrscheinlichkeit wird mit $P(X\leq 2)$ bezeichnet und ist


$$

\begin{align*}
P(X \leq 2) &= P(X = 0) + P(X = 1) + P(X = 2) \\
&= \binom{20}{0} \cdot 0{,}1^0 \cdot 0{,}9^{20} + \binom{20}{1} \cdot 0{,}1^1 \cdot 0{,}9^{19} + \binom{20}{2} \cdot 0{,}1^2 \cdot 0{,}9^{18}\\
&=0,1216 + 0,2702 + 0,2852\\
&=0,6769.
\end{align*}

$$

Die Bernoulli-Formel muss also lediglich mehrmals nacheinander angewendet werden.

### Symbolische Formulierungen

Damit wir die Bernoulli-Formel geeignet anwenden können, müssen wir gut auf die Beschreibung des gesuchten Bereichs achten: Um welche Trefferanzahlen geht es? Dazu ist es hilfreich, textuelle Beschreibungen in symbolische umzuformen.

Beschreiben Sie die folgenden Wahrscheinlichkeiten symbolisch (weiterhin ist $n=8$).

{% include flip-card.html
frage="Wahrscheinlichkeit für genau 6 Treffer"
antwort="
$$

P(X=6)

$$
" %}

{% include flip-card.html
frage="Wahrscheinlichkeit für höchstens 4 Treffer"
antwort="
$$

P(X\leq 4)=P(X=0)+P(X=1)+\ldots+P(X= 4)

$$
" %}

{% include flip-card.html
frage="Wahrscheinlichkeit für mindestens 12 Treffer"
antwort="
$$

P(X\geq 12)=P(X=12)+P(X=13)+\ldots+P(X= 20)

$$
" %}

{% include flip-card.html
frage="Wahrscheinlichkeit für weniger als 10 Treffer"
antwort="
$$

P(X< 10)=P(X=0)+P(X=1)+\ldots+P(X=9)

$$
" %}

{% include flip-card.html
frage="Wahrscheinlichkeit für mehr als 7 Treffer"
antwort="
$$

P(X> 7)=P(X=8)+P(X=9)+\ldots+P(X= 20)

$$
" %}

{% include flip-card.html
frage="Wahrscheinlichkeit für mehr als 11 und höchstens 18 Treffer"
antwort="
$$

P(11< X\leq 18)=P(X=12)+P(X=13)+\ldots+P(X= 18)

$$
" %}

{% include flip-card.html
frage="Wahrscheinlichkeit zwischen einschließlich 2 und ausschließlich 9 Treffer"
antwort="
$$

P(2\leq X<9)=P(X=2)+P(X=3)+\ldots+P(X= 8)

$$
" %}

Wir beobachten die folgenden Regeln:


$$

P(X<k)=P(X\leq k-1)

$$


$$

P(X>k)=P(X\geq k+1)

$$


$$

P(a\leq X\leq b)=P(X\leq b) - P(X\leq a-1)

$$

Das Gegenereignis zu "mindestens $k$ Treffer" ist "höchstens $k-1$ Treffer". Der Satz von der Gegenwahrscheinlichkeit lautet hier also


$$

P(X\geq k)=1-P(X\leq k-1).

$$

### Berechnungen

Für Bereichswahrscheinlichkeiten werden die Bernoulli-Formeln mehrfach nacheinander angewendet. Dies kann bei vielen Summanden aufwendig und fehleranfällig sein. Typischerweise gehen wir daher wie folgt vor:

-  Wir verwenden Tafelwerke, in denen Wahrscheinlichkeiten der Form $P(X\leq k)$ angegeben sind. Andere Wahrscheinlichkeiten müssen dann über geeignete Umformungen bestimmt werden, z.B.:


$$

P(X=k)=P(X\leq k)-P(X\leq k-1)

$$


$$

P(X\geq k)=1-P(X\leq k-1).

$$


$$

P(a<X<b)=P(X\leq b-1)-P(X\leq a).

$$

Die Wahrscheinlichkeiten der Art $P(X\leq k)$ treten im Übrigen häufiger auf und heißen **kumulierte** Wahrscheinlichkeiten.


- Alternativ nutzen wir Taschenrechner, die die gewünschten Wahrscheinlichkeiten direkt berechnen können, z.B.:


$$

P(a\leq X\leq b)=Bcd(a;b;n;p)

$$

<div id="skript-aufgabe-3"></div>

<div id="skript-aufgabe-4"></div>

### Weitere Hinweise
Bevor wir nun Bereichswahrscheinlichkeiten bestimmen können, müssen wir die folgenden Fragen beantworten:

* Liegt überhaupt eine binomialverteilte Zufallsgröße vor?
* Wie lauten die Bernoulli-Parameter $n$ und $p$?
* Was ist im Sachzusammenhang ein Treffer, was ist eine Niete?
* Müssen die Intervallgrenzen des angegebenen Bereichs eventuell noch berechnet werden?
* Möglicherweise entstehen Ausdrücke mit nicht-ganzzahligen Intervallgrenzen. Hier müssen wir richtig runden: Ist z.B. $X\leq 3{,}8$ so darf $X$ auf keinen Fall größer als $3{,}8$ sein, es gilt also $P(X\leq 3{,}8)=P(X\leq 3)$. Ist z.B. $X> 5{,}1$, so darf $X$ auf keinen Fall kleiner oder gleich als $5{,}1$ sein, es gilt also $P(X> 5{,}1)=P(X\geq 6)$.

### Beispiele

Bestimmen Sie die Wahrscheinlichkeiten der angegebnen Ereingisse

1. mit Hilfe kumulierter Wahrscheinlichkeiten,
2. mit Hilfe des Taschenrechners.

Die Basketballspielerin erzielt (weiterhin ist $n=20$ und $p=0{,}1$)


{% include flip-card.html
frage="genau 6 Treffer."
antwort="
$$

\begin{align*}
P(X=6) &= P(X\leq 6) - P(X\leq 5) = 0{,}9976 - 0{,}9887 = 0{,}0089 \\
P(X=6) &= Bcd(6;6;20;0{,}1) = 0{,}0089
\end{align*}

$$
" %}

{% include flip-card.html
frage="höchstens 4 Treffer."
antwort="
$$

\begin{align*}
P(X\leq 4) &= 0{,}9568 \\
P(X\leq 4) &= Bcd(0;4;20;0{,}1) = 0{,}9568
\end{align*}

$$
" %}

{% include flip-card.html
frage="mindestens 6 Treffer."
antwort="
$$

\begin{align*}
P(X\geq 6) &= 1 - P(X\leq 5)=1-0{,}9887= 0{,}0113 \\
P(X\geq 6) &= Bcd(6;20;20;0{,}1) = 0{,}0113
\end{align*}

$$
" %}

{% include flip-card.html
frage="weniger als 3 Treffer."
antwort="
$$

\begin{align*}
P(X<3) &= P(X\leq 2)=0{,}6769 \\
P(X<3) &= Bcd(0;2;20;0{,}1) = 0{,}6769
\end{align*}

$$
" %}

{% include flip-card.html
frage="mehr als 3 Treffer."
antwort="
$$

\begin{align*}
P(X>3) &= 1 - P(X\leq 3)=1-0{,}8670=0{,}1330 \\
P(X>3) &= Bcd(4;20;20;0{,}1) = 0{,}1330
\end{align*}

$$
" %}

{% include flip-card.html
frage="mehr als 1 und höchstens 5 Treffer."
antwort="
$$

\begin{align*}
P(1 < X \leq 5) &= P(X\leq 5) - P(X\leq 1)=0{,}9887-0{,}3917=0{,}5970 \\
P(1 < X \leq 5) &= Bcd(2;5;20;0{,}1) = 0{,}5970
\end{align*}

$$
" %}

{% include flip-card.html
frage="einschließlich 3 und ausschließlich 9 Treffer."
antwort="
$$

\begin{align*}
P(3 \leq X < 9) &= P(X\leq 8) - P(X\leq 2)=0{,}9999-0{,}6769 = 0{,}3230 \\
P(3 \leq X < 9) &= Bcd(3;8;20;0{,}1) = 0{,}3230
\end{align*}

$$
" %}

{% include flip-card.html
frage="weniger als 4 oder mehr als 7 Treffer."
antwort="Das gegebene Ereignis setzt sich aus den beiden Ereignisse $X<4$ und $X>7$ zusammen:
$$

\begin{align*}
P(X<4 \text{ oder } X>7) &= P(X\leq 3) + (1 - P(X\leq 7))=0{,}8670 + 0{,}0004=0{,}8674 \\
P(X<4 \text{ oder } X>7) &= Bcd(0;3;20;0{,}1) + Bcd(8;20;20;0{,}1) =0{,}8670 + 0{,}0004=0{,}8674
\end{align*}

$$
" %}

{% include flip-card.html
frage="in höchstens 13% der Würfe Treffer."
antwort="Hier berechnen wir zunächst die Intervallgrenzen: $0,13\cdot 20=2,6$. Dann haben wir:
$$

\begin{align*}
P(X \leq 2{,}6) &= P(X \leq 2) = 0{,}6769\\
P(X \leq 2{,}6) &= Bcd(0;2;20;0{,}1) = 0{,}6769
\end{align*}

$$
" %}

{% include flip-card.html
frage="in mehr als einem Drittel der Würfe Treffer."
antwort="Hier berechnen wir zunächst die Intervallgrenzen: $\frac{20}{3} \approx 6{,}7$. Dann haben wir:
$$

\begin{align*}
P(X > 6{,}7) &= P(X > 7) = 1 - P(X \leq 6) = 1 - 0{,}9986 = 0{,}0024 \\
P(X > 6{,}7) &= P(X > 7)= Bcd(7;20;20;0{,}1) = 0{,}0024
\end{align*}

$$
" %}


{% include flip-card.html
frage="höchstens 15 Fehlwürfe."
antwort="Hier geht es um die Fehlwürfe und nicht um die Treffer. Daher ist hier $p=0{,}9$.
$$

\begin{align*}
P(X \leq 15)&=0{,}0432\\
P(X \leq 15)&=Bcd(0;15;20;0{,}9)=0{,}0432
\end{align*}

$$
" %}

{% include flip-card.html
frage="nur im ersten und letzten Wurf ein Treffer."
antwort="Es liegt keine binomialverteilte Zufallsgröße vor, da es nicht um die Anzahl der Treffer von 20 Würfen geht, sondern um eine konkrete Wurffolge: 1. Treffer, 2. Fehlwurf, 2. Fehlwurf,..., 19. Fehlwurf, 20. Treffer. Das Ereignis entpricht also genau einem Pfad im Baumdiagramm.
$$

P(\text{1. und 20. Treffer, Rest Fehlwurf})=0{,}1^2 \cdot 0{,}9^{18}=0{,}0015

$$
" %}

{% include flip-card.html
frage="im 3. und 14. Wurf einen Treffer."
antwort="Hier geht es nur um den 3. und 14. Wurf, alles andere ist irrelevant. Daher ist
$$

P(\text{ 3. und 14. Treffer})=0{,}1\cdot 0{,}1=0{,}01

$$
" %}

<div id="skript-aufgabe-5"></div>

## Histogramme

Wie jede Zufallsgröße können binomialverteilte Zufallsgrößen in Histogrammen dargestellt werden. Es gibt zwei Varianten:

- Einzelwahrscheinlichkeiten: Hier wird jeder Trefferanzahl $k$ die Wahrscheinlichkeit $P(X=k)$ zugeordnet.
- Kumulierte Wahrscheinlichkeiten: Hier wird jeder Trefferanzahl $k$ die kumulierte Wahrscheinlichkeit $P(X\leq k)$ zugeordnet.

Ein wichtiger Zusammenhang zwischen beiden Histogrammen ist der folgende: Da


$$

P(X=k)=P(X\leq k)- P(X\leq k-1)

$$

können die Einzelwahrscheinlichkeiten $P(X=k)$ als Stufenhöhen im Histogramm der kumulierten Wahrscheinlichkeiten aufgefasst werden

{%include histogramm-binomial.html %}

<div id="skript-aufgabe-6"></div>

<div id="skript-aufgabe-7"></div>

## Bestimmung von n, p und k

Mit Hilfe der Bernoulli-Formel $P(X=k)=\binom{n}{k}p^k(1-p)^{n-k}$ lassen sich Intervallwahrscheinlichkeiten binomialverteilter Zufallsgrößen betimmen:


$$

\begin{align*}
P(X\leq k)&=P(X=0) + P(X=1) + \ldots P(X=k)\\
&=\binom{n}{0}p^0(1-p)^{n} + \binom{n}{1}p^{1}(1-p)^{n-1} + \ldots + \binom{n}{k}p^k(1-p)^{n-k}\\
=&\sum\_{i=0}^k \binom{n}{i}p^i(1-p)^{n-i}
\end{align*}

$$

Wie wir gesehen haben, lässt sich dieser komplizierte Ausdruck mit Hilfe von Tafelwerken oder Taschenrechnern bestimmen. Das bedeutet: Wenn $n$, $p$ und $k$ gegeben sind, können wir die Wahrscheinlickeit $P(X\leq k)$ bestimmen.

Wir ändern nun die Perspektive: Angenommen $P(X\leq k)$ und z.b. $p$ und $k$ seien gegeben. Was ist dann $n$?

Dazu müsste die oben erwähnte Formel nach $n$ aufgelöst werden. Dies ist jedoch nicht elementar möglich. Stattdessen probieren wir systemisch aus, indem wir Wertetabellen erstellen.

### Beispiel 1
Gegegen: $P(X\leq 3)\approx 0{,}71$ und $p=0,4$

Gesucht: $n$

Mit Hilfe eines Tafelswerks und Taschenrechners stellen  wir folgende Tabelle auf:

| $n$ | $P(X\leq 3)$ |
| --- | ----------- |
| 1      | 1,0000           |
| 2      | 1,0000           |
| 3      | 1,0000           |
| 4      | 0,9744           |
| 5      | 0,9130           |
| 6      | 0,8208           |
| 7      | 0,7102           |
| 8      | 0,5941           |
| 9      | 0,4826           |
| 10     | 0,3823           |

Wir entnehmen der Tabelle, dass $P(X\leq 3)=0{,}7102\approx 0{,}71$ für $n=3$ ist.

### Beispiel 2

Gegegen: $P(X\geq 14)\approx 0{,}15$ und $n=20$

Gesucht: $p$

Mit Hilfe eines Tafelswerks und Taschenrechners stellen  wir folgende Tabelle auf:

| $p$ | $P(X\geq 14)$ |
| --- | ----------- |
| 0,51  | 0,0688 |
| 0,52  | 0,0814 |
| 0,53  | 0,0958 |
| 0,54  | 0,1119 |
| 0,55  | 0,1299 |
| 0,56  | 0,1499 |
| 0,57  | 0,1719 |
| 0,58  | 0,1959 |
| 0,59  | 0,2220 |
| 0,60  | 0,2500 |

Wir entnehmen der Tabelle, dass $P(X\geq 14)=0{,}1499\approx 0{,}15$ für $p=0{,}56$ ist.

### Beispiel 3

Gegegen: $P(X\leq k)\approx 0{,}10$ und $n=200$ und $p=0{,}9$

Gesucht: $k$

Mit Hilfe eines Tafelswerks und Taschenrechners stellen  wir folgende Tabelle auf:

| $k$ | $P(X\leq k)$ |
| --- | ----------- |
| 171   | 0,0271 |
| 172   | 0,0434 |
| 173   | 0,0672 |
| 174   | 0,1005 |
| 175   | 0,1449 |
| 176   | 0,2017 |
| 177   | 0,2710 |
| 178   | 0,3516 |
| 179   | 0,4408 |
| 180   | 0,5345 |

Wir entnehmen der Tabelle, dass $P(X\leq 174)=0{,}1005\approx 0{,}10$. Es ist also $k=174$.

Häufig  stegen wir auch vor der Frage, dass ein minimales oder maximales $n$, $p$ oder $k$ gesucht ist, so dass eine vorgegebene Wahrscheinlichkeit unter- oder überschritten wird.

{% include flip-card.html
frage="
Der Besitzer eines Restaurants untersucht, wie viele Gäste vegetarische Gerichte bestellen. Allgemeine Statistiken zeigen, dass 61% aller Gäste vegetarische Gerichte bestellen.

Bestimmen Sie die Anzahl der Gerichte, die mindestens untersucht werden müssen, damit die Wahrscheinlichkeit für mindestens 144 vegetarische Gerichte mindestens 29% beträgt."
antwort="
Gegeben ist $p=0{,}61$ und $k=144$. Gesucht ist das kleinste $n$, so dass $P(X\geq 144)\geq 0{,}29$ ist. Wir bestimmen:

$$

\begin{align*}
\text{für }n=228 \text{ gilt: } P(X\geq 144)=0{,}2753<0{,}29\\
\text{für }n=229 \text{ gilt: } P(X\geq 144)=0{,}3042\geq 0{,}29
\end{align*}

$$

Das kleinste $n$, für das $P(X\geq 144)\geq 0{,}29$ gilt, ist also $n=229$.

" %}

<div id="skript-aufgabe-8"></div>

{% include flip-card.html
frage="
Ein Unternehmen untersucht, wie zufrieden seine Mitarbeiter sind. Dazu werden 274 Mitarbeiter befragt.

Bestimmen Sie wie hoch der Anteil der zufriedenen Mitarbeiter mindestens sein muss, damit die Wahrscheinlichkeit für höchstens 142 zufriedene Mitarbeiter höchstens 31% beträgt (auf 2 NKS gerundet)."
antwort="
Gegeben ist $n=274$ und $k=142$. Gesucht ist das kleinste $p$, so dass $P(X\leq 142)\leq 0{,}31$ ist. Wir bestimmen:

$$

\begin{align*}
\text{für }p=0{,}53 \text{ gilt: } P(X\leq 142)=0{,}3706>0{,}31\\
\text{für }p=0{,}54 \text{ gilt: } P(X\leq 142)=0{,}2538\leq 0{,}31
\end{align*}

$$

Das kleinste $p$, für das $P(X\leq 142)\leq 0{,}31$ gilt, ist also $p=0{,}54$.

" %}

<div id="skript-aufgabe-9"></div>

{% include flip-card.html
frage="
Ein potentieller Werbepartner studiert den Bekanntheitsgrad einer Influencerin. An einer Umfrage zum Bekanntheitsgrad der Influencerin nehmen 158 User teil. Man weiß, dass jeder 2. User der Influencerin folgt.

Bestimmen Sie die Anzahl der Follower der Influencerin, die höchstens in der Stichprobe vorhanden sein dürfen, damit die Wahrscheinlichkeit für mindestens diese Anzahl der Follower der Influencerin mindestens 87% beträgt."
antwort="
Gegeben ist $n=158$ und $p=0{,}5$. Gesucht ist das größte $k$, so dass $P(X\geq k)\geq 0{,}87$ ist. Wir bestimmen:

$$

\begin{align*}
\text{Es gilt: } P(X\geq 72)=0{,}8837\geq 0{,}87\\
\text{Es gilt: } P(X\geq 73)=0{,}8495< 0{,}87
\end{align*}

$$

Das größte $k$, für das $P(X\geq k)\geq 0{,}87$ gilt, ist also $k=72$.

" %}

<div id="skript-aufgabe-10"></div>

## Erwartungswert und Standardabweichung


$$
