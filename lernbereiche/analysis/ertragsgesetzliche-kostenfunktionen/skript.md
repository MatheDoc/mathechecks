---
layout: skript
title: Ertragsgesetzliche Kostenfunktionen
description: Ertragsgesetzliche Kostenfunktionen - Skript
lernbereich: ertragsgesetzliche-kostenfunktionen
gebiet: analysis
---

## Einführung

Die Kosten eines Unternehmens lassen sich durch verschiedene Funktionen modellieren. Eine besondere Rolle spielen dabei **ertragsgesetzliche Kostenfunktionen**. Diese lassen sich durch ganzrationale Funktionen dritten Grades der Form $K(x)=ax^3+bx^2+cx+d$ beschreiben und weisen folgende charakteristische Eigenschaften auf:

- Der y-Abschnitt ist positiv, denn die Fixkosten sind immer positiv.
- $K(x)$ ist monoton wachsend, denn mit zunehmender Produktionsmenge steigen auch die Gesamtkosten.
- Die Wendestelle ist positiv, denn $K(x)$ soll den charakteristischen Übergang von unterproportionalem zu überproprotionalen Kostenwachstum modellieren.

Die folgende graphische Darstellung zeigt verschiedene Funktionen dritten Grades und dient der Unterscheidung zwischen ertragsgesetzlichem und nicht-ertragsgesetzlichem Verlauf:

{% include graph.html
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

- $f(x)$ hat einen keinen positiven $y$-Abschnitt
- $g(x)$ ist nicht monoton wachsend
- $h(x)$ hat keine postive Wendestelle

## Nachweis der Ertragsgesetzlichkeit

Um rechnerisch zu prüfen, ob eine Kostenfunktion $K(x)$ einen ertragsgesetzlichen Verlauf aufweist, müssen wir folgendes prüfen:

- Form: Die Funktion ist ganzrational dritten Grades, d.h. $K(x)=ax^3+bx^2+cx+d$.
- Fixkosten: Der y-Achsenabschnitt ist positiv, d. h. $K(0)>0$.
- Monotonie: Die Funktion ist monoton wachsend, d.h.$K'(x)\geq 0$.
- Wendepunkt: Die Wendestelle $x_w$ ist positiv, d.h. $x_w>0$.

{% include info.html
index="1"
frage="Welche Funktionen haben einen ertragsgesetzlichen Verkauf?

$$
\begin{align*}
K_1(x)&=3x^2+4x+2\\
K_2(x)&=0{,}5x^3-6x^2+30x-50\\
K_3(x)&=0{,}5x^3-6x^2+15x+48\\
K_4(x)&=0{,}5x^3+1{,}5x^2+7{,}5x+110{,}5\\
K_5(x)&=0{,}5x^3-6x^2+30x+48\\
\end{align*}
$$

"
antwort="

### $K_1(x)$

$K_1(x)=3x^2+4x+2$ ist keine Funktion dritten Grades. 👉 nicht-ertragsgesetzlich ❌

### $K_2(x)$

$K_20{,}5x^3-6x^2+30x-50$ besitzt einen negativen y-Abschnitt. 👉 nicht-ertragsgesetzlich ❌

### $K_3(x)$

Um zu prüfen, ob $K_3(x)0{,}5x^3-6x^2+15x+48$ monoton wachsend ist, können wir versuchen Extremstellen zu bestimmen. **Wenn es Extremstellen gibt, dann ist die Funktion nicht monoton wachsend.** Wir berechnen $K_3'(x)=1{,}5x^2-12x^2+15$. Die notwendige Bedignung für Extrema lautet:

$$
\begin{align*}
1{,}5x^2-12x^2+15&=0\quad |:(1{,}5)\\
5x^2-8x^2+10&=0\quad |\text{ pq-Formel}\\
x_{1,2}=-\frac{-8}{2}\pm\sqrt{\left(\frac{-8}{2}\right)^2-10}\\
x_{1,2}=4\pm\sqrt{6}
\end{align*}
$$

Da der Term unter Wurzel positiv ist, existieren die einfachen Nullstellen $x_1$ und $x_2$. Es liegen also Extrema vor. 👉 nicht-ertragsgesetzlich ❌

(Wären beide Extremstellen negativ, so könnte durchaus im ökonomischen Definitionsbereich ein monotones Wachstum vorliegen. Da aber die Wendestelle positiv sein muss, können wir annehmen, dass zumindest die größere Extremstelle positiv ist.)

### $K_4(x)$

Wir bestimmen die Wendestelle von $K_4(x)=0{,}5x^3+1{,}5x^2+7{,}5x+110{,}5$. Wir haben $K^{\prime\prime}(x)=3x+3$ und $K^{\prime\prime\prime}(x)=3$. Die notwendige Bedingung lautet:

$$
\begin{align*}
3x+3=0\\
x&=-1
\end{align*}
$$

Die hinreichende Bedingung:

$$
K'''(-1)=3>0\text{ (minimale Steigung)}
$$

Die Wendestelle ist also negativ. 👉 nicht-ertragsgesetzlich ❌

### $K_5(x)$

Für $K_5(x)=0{,}5x^3-6x^2+30x+48$ gilt:

- Die Funktion ist ganzrational dritten Grades. ✔️
- Der y-Achsenabschnitt ist positiv. ✔️
- Wir versuchen die Extremstellen zu berechnen: Es ist $K_5'(x)=1{,}5x^2-12x+30$. Die notwendige Bedingung lautet

  $$
  \begin{align*}
  1{,}5x^2-12x^2+30&=0\quad |:(1{,}5)\\
  x^2-8x^2+20&=0\quad |\text{ pq-Formel}\\
  x_{1,2}=-\frac{-8}{2}\pm\sqrt{\left(\frac{-8}{2}\right)^2-20}\\
  x_{1,2}=4\pm\sqrt{-4}
  \end{align*}
  $$

  Da der Term unter Wurzel negativ ist, existieren keine Extremstellen. Die Funktion $K_5(x)$ ist also monoton, und zwar monoton wachsend, weil z.B. der Leitkoeffizient $0{,}5>0$ ist. ✔️

- Wir berechnen die Wendestelle: Es ist $K_5^{\prime\prime}(x)=3x-12$. Die notwendige Bedingung lautet:

  $$
  \begin{align*}
  3x-12=0\\
  x&=4
  \end{align*}
  $$

  Die hinreichende Bedingung:

  $$
  K'''(4)=3>0\text{ (minimale Steigung)}
  $$

  Die Wendestelle $x_w$ ist also positiv. ✔️

Damit sind alle Kriterien erfüllt. 👉 ertragsgesetzlich ✅

"
%}

<div id="skript-aufgabe-1"></div>

### Nachweis für parametrisierte Funktionen

Betrachten wir parametrisierte Funktionen, z.B.

$$
K_a(x)=x^3-9x^2+ax+60,
$$

so könnte nur für einen bestimmen Paramterbereich ein ertragsgesetzlicher Verlauf vorliegen. Dazu betrachten wir die Graphen zu den Parametern $a=40$, $a=30$, $a=20$ und $a=10$.

{% include graph.html
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

{% include info.html
index="2"
frage="Für welche Parameter ist $K_a(x)=x^3-9x^2+ax+60$ ertragsgesetzlich?"
antwort="

- Da $K_a(0)=60$ für alle $a$ liegt immer ein positiver y-Abschnitt vor.
- Da $K_a^{\prime\prime}(x)=6x-18$ und $6x-18=0$ falls $x=3$ ist die Wendestelle immer positiv.
- Zur Monotonie: Wir berechnen die Nullstellen von $K_a'(x)=3x^2-18x+a$.

$$
\begin{align*}
3x^2-18x+a&=0\quad |:(3)\\
x^2-6x+\frac{a}{3}&=0\quad |\text{ pq-Formel}\\
x_{1,2}&=-\frac{-6}{2}\pm\sqrt{\left(\frac{-6}{2}\right)^2-\frac{a}{3}}\\
x_{1,2}&=3\pm\sqrt{9-\frac{a}{3}}
\end{align*}
$$

Nun ist $K'_a(x)\geq 0$ genau dann, wenn keine einfachen Nullstellen existieren. Dies ist genau dann der Fall, falls der Term unter der Wurzel nicht positiv ist, d.h. falls

$$
\begin{align*}
9-\frac{a}{3}&\leq 0\quad |+\frac{a}{3}\\
9&\leq \frac{a}{3}\quad |\cdot 3\\
27&\leq a
\end{align*}
$$

Also ist $K'_a(x)\geq 0$, falls $a\geq 27$.
"

%}

<div id="skript-aufgabe-2"></div>

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

Neben der gewöhnlichen Kostenfunktion $K(x)$, die die Gesamtkosten in Abhängigkeit der MEnge $x§ angeibt, betrachten wir hier noch:

- die Grenzkostenfunktion $K'(x)$ (Ableitung von $K(x)$)
- die Stückkostenfunktion $k(x)=\frac{K(x)}{x}$
- variable Stückkostenfunktion $k_v(x)=\frac{K_v(x)}{x}$, wobei $K_v(x)$ die variablen Gesamtkosten sind

Für die Kostenfunktion $K(x)=0{,}5x^3 - 6x^2 + 30x + 48$ erhalten wir für die

- Grenzekosten: $K'(x) = 1{,}5x^2-12x+30$
- Stückosten: $k(x)=0{,}5x^2 - 6x + 30 + \frac{48}{x}$
- variablen Stückkosten: $k_v(x)=0{,}5x^2 - 6x + 30 $

Diese Kostenfunktionen werden mit Hilfe folgender Kennzahlen beschrieben und analysiert.

- **Übergang vom degressiven zum progressiven Kostenwachstum:** Menge, bis zu der die Kosten unterproportional steigen, danach überproportional.
- **Betriebsminimum:** Menge, bei die geringsten variablen Stückkosten auftreten.
- **Kurzfristige Preisuntergrenze:** Stückkosten, wenn im Betriebsminimum produziert wird - entspricht bei dem Preis, bei dem die variablen Stückkosten gedeckt sind.
- **Betriebsoptimum:** Menge, bei die geringsten Stückkosten auftreten.
- **Langfristige Preisuntergrenze:** Stückkosten, wenn im Betriebsoptimum produziert wird - entspricht bei dem Preis, bei dem die Stückkosten gedeckt sind.

{% include info.html
index="3"
frage="Mathematische Definition Kostenkennzahlen"
antwort="Beschreibung der Kennzahlen mit Hilfe mathematischer Fachbegriffe"
%}

<div id="skript-aufgabe-3"></div>

## Graphische Darstellung

{% include graph.html
   funktionen='[
    {"name":"K\u2032(x)", "term":"1.5*x^2-12*x+30", "beschreibung":"Kostenfunktion"},
    {"name":"k(x)", "term":"0.5*x^2-6*x+30+48/x", "beschreibung":"Stückkostenfunktion"},
    {"name":"k<sub>v</sub>(x)", "term":"0.5*x^2-6*x+30", "beschreibung":"variable Stückkostenfunktion"}
   ]'
   titel="Kostenfunktionen"
   xachse="Menge x in ME"
   yachse="Betrag y in GE"
   xmin=0
   xmax=12.5
   ymin=0
   ymax=80
%}

{% include info.html
index="4"
frage="Graphische Bestimmung"
antwort="Interpretation charakteristischer Punkte"
%}

<div id="skript-aufgabe-4"></div>

## Berechnung

Um Kostenkennzahlen berechnen zu können, benötigen wir die unter anderem die Werkzeuge der Differentialrechnung. Um die Kennzahlen berechnen zu können, ist es nun wichtig, den richtigen mathematischen Ansatz zu wählen.

{% include info.html
index="5"
frage="Ableitung einfacher gebrochenrationaler Funktionen."
antwort="

- Ableitung von $f(x)=\frac{1}{x}$: $f'(x)=-\frac{1}{x^2}$
- Ableitung von $f(x)=\frac{1}{x^2}$: $f'(x)=-\frac{1}{x^3}$

  "
  %}

<div id="skript-aufgabe-5"></div>

### Exkurs: Alternative Bestimmung des Betriebsminimums und -optimums

## Steckbriefaufgaben
