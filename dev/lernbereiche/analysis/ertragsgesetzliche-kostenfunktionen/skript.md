---
layout: dev-module
title: Ertragsgesetzliche Kostenfunktionen - Skript (Dev)
description: Dev-Lernbereich Ertragsgesetzliche Kostenfunktionen, Modul Skript.
page_context: Lernbereich
nav: dashboard
body_class: page-module-designs
module_key: skript
published: true
lernbereich: ertragsgesetzliche-kostenfunktionen
gebiet: analysis
permalink: /dev/lernbereiche/analysis/ertragsgesetzliche-kostenfunktionen/skript.html
---

## Einführung

Die Kosten eines Unternehmens lassen sich durch verschiedene Funktionen modellieren. Eine besondere Rolle spielen dabei **ertragsgesetzliche Kostenfunktionen**. Diese lassen sich durch ganzrationale Funktionen dritten Grades $K(x)=ax^3+bx^2+cx+d$ beschreiben und weisen folgende charakteristische Eigenschaften auf:

- Der y-Abschnitt ist positiv, denn die Fixkosten sind immer positiv.
- $K(x)$ ist monoton wachsend, denn mit zunehmender Produktionsmenge steigen auch die Gesamtkosten.
- Die Wendestelle ist positiv, denn $K(x)$ soll den charakteristischen Übergang von unterproportionalem zu überproprotionalem Kostenwachstum modellieren.

### Graphische Darstellung der Ertragsgesetzlichkeit

Die folgende graphische Darstellung zeigt verschiedene Funktionen dritten Grades und dient der Unterscheidung zwischen ertragsgesetzlichem und nicht-ertragsgesetzlichem Verlauf:

{% include dev/graph.html
   funktionen='[
    {"name":"K(x)", "term":"0.5*x^3-6*x^2+30*x+48", "beschreibung":"Kostenfunktion"},
    {"name":"f(x)", "term":"0.5*x^3-6*x^2+30*x-50", "beschreibung":"f(x)"},
    {"name":"g(x)", "term":"0.5*x^3-6*x^2+15*x+48", "beschreibung":"g(x)"},
    {"name":"h(x)", "term":"0.5*x^3+1.5*x^2+7.5*x+110.5", "beschreibung":"h(x)"}
   ]'
    punkte='[
     {"x":0,"y":-50,"text":"negativer y-Abschnitt"},
     {"x":4,"y":44,"text":"in einem Bereich streng monoton fallend"},
     {"x":-1,"y":104,"text":"negative Wendestelle"}
   ]'
   titel="Ertragsgesetzliche Kostenfunktionen"
   xachse="Menge x in ME"
   yachse="Betrag y in GE"
   xmin=-4
   xmax=10
   ymin=-60
   ymax=200
%}

Aus der Grafik ist ersichtlich, dass nur die Funktion $K(x)$ den Anforderungen an eine ertragsgesetzliche Kostenfunktion genügt. Die weiteren Funktionen scheitern jeweils an einem Kriterium:

- $f(x)$ hat einen keinen positiven $y$-Abschnitt.
- $g(x)$ ist nicht monoton wachsend.
- $h(x)$ hat keine postive Wendestelle.

Auch mit Hilfe der Graphen der Grenzkostenfunktionen können wir - bis auf den positiven y-Abschnitt - prüfen, ob ein ertragsgesetzlicher Kostenverlauf vorliegt. Das folgende Diagramm zeigt die Graphen vierer Ableitungsfunktionen.

{% include dev/graph.html
   funktionen='[
    {"name":"K\u2032(x)", "term":"1.5*x^2-12*x+30", "beschreibung":"Kostenfunktion"},
    {"name":"f\u2032(x)", "term":"-1.5*x^2+8*x+35", "beschreibung":"f(x)"},
    {"name":"g\u2032(x)", "term":"1.5*x^2-12*x+15", "beschreibung":"g(x)"},
    {"name":"h\u2032(x)", "term":"1.5*x^2+2*x+7.5", "beschreibung":"h(x)"}
   ]'
    punkte='[
     {"x":4,"y":-9,"text":"g\u2032 in einem Bereich negative Werte, d.h. g streng monoton fallend"},
     {"x":-0.67,"y":6.83,"text":"negative Extremstelle h\u2032, d.h. negative Wendestelle von h"}
   ]'
   titel="Ertragsgesetzliche Kostenfunktionen"
   xachse="Menge x in ME"
   yachse="Betrag y in GE"
   xmin=-2
   xmax=10
   ymin=-10
   ymax=50
%}

Aus der Grafik ist ersichtlich, dass nur die Funktion $K(x)$ den Anforderungen an eine ertragsgesetzliche Kostenfunktion genügt. Die weiteren Funktionen scheitern jeweils mindestens an einem Kriterium:

- $f'(x)$ ist eine nach unten geöffnete Parabel. Dann kann $f(x)$ grundsätzlich nicht ertragsgesetzlich sein, weil $f(x)$ z.B. einen negativen Leitkoeffizienten hat und somit für große $x$ streng monoton fallend ist.
- $g'(x)$ nimmt in einem Bereich negative Werte an. Damit ist $g(x)$ in diesem Bereich streng monoton fallend.
- $h'(x)$ hat eine negative Extremstelle. Diese entspricht der Wendestelle von $h(x)$. Die Wendestelle von $h(x)$ ist also negativ.

## Rechnerischer Nachweis der Ertragsgesetzlichkeit

Um rechnerisch zu prüfen, ob eine Kostenfunktion $K(x)$ einen ertragsgesetzlichen Verlauf aufweist, müssen wir folgendes prüfen:

- Form: Die Funktion ist ganzrational dritten Grades, d.h. $K(x)=ax^3+bx^2+cx+d$.
- Fixkosten: Der y-Achsenabschnitt ist positiv, d. h. $K(0)>0$.
- Monotonie: Die Funktion ist monoton wachsend, d.h.$K'(x)\geq 0$.
- Wendepunkt: Die Wendestelle $x_w$ ist positiv, d.h. $x_w>0$.

{% include dev/check-anker.html nummer="1" %}

### Nachweis für parametrisierte Funktionen

Betrachten wir parametrisierte Funktionen, z.B.

$$
K_a(x)=x^3-9x^2+ax+60,
$$

so könnte nur für einen bestimmen Paramterbereich ein ertragsgesetzlicher Verlauf vorliegen. Dazu betrachten wir die Graphen zu den Parametern $a=40$, $a=30$, $a=20$ und $a=10$.

{% include dev/graph.html
   funktionen='[
    {"name":"K<sub>40</sub>(x)", "term":"x^3-9*x^2+40*x+60", "beschreibung":"K<sub>40</sub>(x)"},
    {"name":"K<sub>30</sub>", "term":"x^3-9*x^2+30*x+60", "beschreibung":"K<sub>30</sub>(x)"},
    {"name":"K<sub>20</sub>", "term":"x^3-9*x^2+20*x+60", "beschreibung":"K<sub>20</sub>(x)"},
    {"name":"K<sub>10</sub>", "term":"x^3-9*x^2+10*x+60", "beschreibung":"K<sub>10</sub>(x)"}
   ]'
   titel="Ertragsgesetzliche Kostenfunktionen"
   xachse="Menge x in ME"
   yachse="Betrag y in GE"
   xmin=0
   xmax=11
   ymin=0
   ymax=300
%}

Wir erkennen, dass nur $K_{40}$ und $K_{30}$ ertragsgesetzlich sind, $K_{20}$ und $K_{10}$ sind nicht monoton wachsend. Um feststellen zu können, für welche Paramter $a$ ein ertragsgesetzlicher Verlauf vorliegt, müssen wir die Kriterien in Abhängigkeit des Paramters $a$ prüfen.

{% include dev/check-anker.html nummer="2" %}

### Allgemeiner Nachweis

Um zu prüfen, ob eine Kostenfunktion $K(x)$ einen ertragsgesetzlichen Verlauf aufweist, sind folgende Bedingungen zu analysieren:

1. $K(0)>0$.
2. $x_w>0$.
3. $K'(x)\geq 0$

Wir prüfen diese Bedingungen nun für die allgemeine Funktionen $K(x)=ax^3+bx^2+cx+d$:

1. $K(0)>0$: Dies ist genau erfüllt, falls $d>0$.
2. $K'(x)\geq 0$: Zunächst muss $a>0$ sein, da sonst $K(x)$ für große $a$ monoton fallend wäre. Wir berechnen die Nullstellen der ersten Ableitung $K'(x)=3ax^2+2bx+c$.

   $$
   \begin{align*}
   3ax^2+2bx+c&=0\quad| :(3a)\\
   x^2+\frac{2b}{3a}x+\frac{c}{3a}&=0\quad| \text{ pq-Formel}\\
   x_{1,2}&=-\frac{-b}{3a}\pm \sqrt{\left(\frac{-b}{3a}\right)^2-\frac{c}{3a}}
   \end{align*}
   $$

   Nun gilt $K'(x)\geq 0$, falls der Term unter der Wurzel nicht-negativ ist: $\left(\frac{-b}{3a}\right)^2-\frac{c}{3a}\geq 0$, d.h. $b^2\leq 3ac$.

3. $x_w>0$: Wir berechnen allgemein die Wendestelle. Die Wendestelle ist die Nullstelle von $K^{\prime\prime\prime}(x)=6ax+2b$

   $$
   \begin{align*}
   6ax+2b&=0\\
   x&=-\frac{b}{3a}
   \end{align*}
   $$

   Das heißt, $x_w>0$ falls $-\frac{b}{3a}>0$. Da generell $a>0$ ist, folgt $b<0$.

Wir fassen zusammen. Eine Funktion $K(x)=ax^3+bx^2+cx+d$ ist genau ertragsgesetzlich falls die folgenden Bedingungen erfüllt sind:

- $d>0$
- $a>0$
- $b^2\leq 3ac$
- $b<0$

## Kennzahlen

Neben der gewöhnlichen Kostenfunktion $K(x)$, die die Gesamtkosten in Abhängigkeit der Menge $x$ angibt, betrachten wir hier noch:

- die Grenzkostenfunktion $K'(x)$ (Ableitung von $K(x)$)
- die Stückkostenfunktion $k(x)=\frac{K(x)}{x}$
- variable Stückkostenfunktion $k_v(x)=\frac{K_v(x)}{x}$, wobei $K_v(x)$ die variablen Gesamtkosten sind

Für die Kostenfunktion $K(x)=0{,}5x^3 - 6x^2 + 30x + 48$ erhalten wir für die

- Grenzkosten: $K'(x) = 1{,}5x^2-12x+30$
- Stückkosten: $k(x)=0{,}5x^2 - 6x + 30 + \frac{48}{x}$
- variablen Stückkosten: $k_v(x)=0{,}5x^2 - 6x + 30 $

Diese Kostenfunktionen werden mit Hilfe folgender Kennzahlen beschrieben und analysiert.

|Kennzahl| Symbol | Beschreibung|Mathematische Definition|
|---|---|---|---|
|Übergang degressives/progressives Kostenwachstum| $x_w$|Menge, bis zu der die Kosten unterproportional steigen, danach überproportional|  Extremstelle (Minimum) von $K'$|
|Betriebsminimum| $x_{BM}$ | Menge, bei der die geringsten variablen Stückkosten auftreten| Extremstelle (Minimum) von $k_v$|
|Kurzfristige Preisuntergrenze| $KPU$ | Stückkosten, wenn im Betriebsminimum produziert wird - entspricht dem kleinsten Preis, bei dem die variablen Stückkosten gedeckt sind| $k_v(x_{BM})$ |
|Betriebsoptimum| $x_{BO}$ | Menge, bei der die geringsten Stückkosten auftreten| Extremstelle (Minimum) von $k$|
|Langfristige Preisuntergrenze| $LPU$ | Stückkosten, wenn im Betriebsoptimum produziert wird - entspricht bei dem kleinsten Preis, bei dem die Stückkosten gedeckt sind| $k(x_{BO})$ |


## Graphische Darstellungen

{% include dev/check-anker.html nummer="3" %}




## Berechnungen

Um Kostenkennzahlen berechnen zu können, benötigen wir die unter anderem die Werkzeuge der Differentialrechnung. Um die Kennzahlen berechnen zu können, ist es nun wichtig, den richtigen mathematischen Ansatz zu wählen.

{% include dev/check-anker.html nummer="4" %}

Jetzt sind wir in der Lage, die Kostenkennzahlen mit Hilfe der Differentialrechnung zu berechnen.

{% include dev/check-anker.html nummer="5" %}




### Exkurs: Alternative Bestimmung des Betriebsminimums und -optimums

Das Betriebsoptimum und Betriebsminimum lassen sich auch wie folgt bestimmen.

### Satz

**1.** Das Betriebsoptimum ist die Schnittstelle der Grenzkosten- und Stückkostenfunktion:

$$
x_{BO} = \text{Schnittstelle von } K' \text{ und } k.
$$

**2.** Das Betriebsminimum ist die Schnittstelle der Grenzkosten- und variablen Stückkostenfunktion:

$$
x_{BM} = \text{Schnittstelle von } K' \text{ und } k_v.
$$

### Beweis

**1.**

Eine allgemeine Kostenfunktion ist von der Gestalt

$$
K(x) = ax^3 + bx^2 + cx + d.
$$

Es folgt:

$$
\begin{align*}
K'(x) &= 3ax^2 + 2bx + c \\
k(x) &= ax^2 + bx + c + \frac{d}{x} \\
k'(x) &= 2ax + b - \frac{d}{x^2}
\end{align*}
$$

Das Betriebsoptimum $x_{BO}$ ist die Nullstelle der 1. Ableitung von $k'$, d.h.:

$$
\begin{align*}
k'(x_{BO}) &= 0 \\
2a x_{BO} + b - \frac{d}{x_{BO}^2} &= 0 \quad \big| \cdot x_{BO}^2 \\
2a x_{BO}^3 + b x_{BO}^2 - d &= 0
\end{align*}
$$

Für die Schnittstelle der Grenzkosten- und Stückkostenfunktion $x_s$ gilt:

$$
\begin{align*}
K'(x_s) &= k(x_s) \\
3a x_s^2 + 2b x_s + c &= a x_s^2 + b x_s + c + \frac{d}{x_s} \\
2a x_s^2 + b x_s - \frac{d}{x_s} &= 0 \quad \big| \cdot x_s \\
2a x_s^3 + b x_s^2 - d &= 0
\end{align*}
$$

Es folgt die Behauptung, da die jeweils letzten Gleichungen identisch sind.

**2.**

Aus der Gestalt der allgemeinen Kostenfunktion folgt:

$$
\begin{align*}
k_v(x) &= ax^2 + bx + c \\
k_v'(x) &= 2a x + b
\end{align*}
$$

Das Betriebsminimum $x_{BM}$ ist die Nullstelle der Ableitung von $k_v$, also:

$$
\begin{align*}
k_v'(x_{BM}) &= 0 \\
2a x_{BM} + b &= 0
\end{align*}
$$

Für die Schnittstelle der Grenzkosten- und variablen Stückkostenfunktion $x_s$ gilt:

$$
\begin{align*}
K'(x_s) &= k_v(x_s) \\
3a x_s^2 + 2b x_s + c &= a x_s^2 + b x_s + c \\
2a x_s^2 + b x_s &= 0 \quad \big| :x_s,\ \text{da } x_s \ne 0 \\
2a x_s + b &= 0
\end{align*}
$$

Es folgt die Behauptung, da die jeweils letzten Gleichungen identisch sind.

## Steckbriefaufgaben

Ist die Gleichung einer ertragsgesetzlichen Kostenfunktion nicht bekannt, liegen jedoch Informationen über einzelne Kostenkennzahlen vor, so können wir unter Umständen die Funktionsgleichung $K(x)=ax^3+bx^2+cx+d$ rekonstruieren, das heißt die Koeffizienten bestimmen.

### Beispiel

Gegeben: Für eine ertragsgesetzliche Kostenfunktion $K(x)$ sei bekannt:

| Menge $x$ in ME | 1 | 2 | 3 | 5 |
| Kosten $K(x)$ in GE | 25 | 33 | 35 | 45 |

Gesucht: $K(x)=ax^3+bx^2+cx+d$.

Graphisch lässt sich die Situation so darstellen: Wir suchen den eine Funktion $K(x)$, deren Graph durch die angegebenen Punkte verläuft.

{% include dev/graph.html
   funktionen='[
    {"name":"K(x)", "term":"x^3-9*x^2+28*x+5", "beschreibung":"Kostenfunktion"}
   ]'
    punkte='[
     {"x":1,"y":25,"text":""},
     {"x":2,"y":33,"text":""},
     {"x":3,"y":35,"text":""},
     {"x":5,"y":45,"text":""}
   ]'
   titel="Gesucht: Graph durch geg. Punkte"
   xachse="Menge x in ME"
   yachse="Betrag y in GE"
   xmin=0
   xmax=8
   ymin=0
   ymax=70
%}

Zur Berechnung der Koeffizienten von $K(x)$ setzen wir die gegebenen Informationen in die Kostenfunktion ein:

$$
\begin{alignat*}{5}
K(1)=25 \;&\Rightarrow\;&\; a\cdot 1^3 + b\cdot 1^2 + c\cdot 1 + d &= 25 \;&\Rightarrow\;&\; 1a + 1b + 1c + 1d = 25 \\
K(2)=33 \;&\Rightarrow\;&\; a\cdot 2^3 + b\cdot 2^2 + c\cdot 2 + d &= 33 \;&\Rightarrow\;&\; 8a + 4b + 2c + 1d = 33 \\
K(3)=35 \;&\Rightarrow\;&\; a\cdot 3^3 + b\cdot 3^2 + c\cdot 3 + d &= 35 \;&\Rightarrow\;&\; 27a + 9b + 3c + 1d = 35 \\
K(5)=45 \;&\Rightarrow\;&\; a\cdot 5^3 + b\cdot 5^2 + c\cdot 5 + d &= 45 \;&\Rightarrow\;&\; 125a + 25b + 5c + 1d = 45
\end{alignat*}
$$

Die jeweils letzten Gleichungen bilden ein lineares Gleichungssystem mit vier Gleichungen und vier Unbekannten. Dieses kann mit Hilfe des Gauß-Algorithmus oder dem Taschenrechner eindeutig gelöst werden. Wir erhalten:

$$
a=1,\quad b=-9,\quad c=28,\quad d=5
$$

Damit ist $K(x)=x^3-9x^2+28x+5$.

Wir können den Plan zum Aufstellen von Funktionsgleichungen wie folgt zusammenfassen:

1. Aufstellen der allgemeinen Funktion: $K(x)=ax^3+bx^2+cx+d$, ggf. weitere, z.B. $k_v(x)=ax^2+bx+c$.
2. Gegebene Informationen durch Gleichungen ausdrücken.
3. Aufstellen eines linearen Gleichungssystems.
4. Lösen des Gleichungssystems und Angabe der gesuchten Funktion.

{% include dev/check-anker.html nummer="6" %}


