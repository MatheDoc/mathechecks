---
layout: skript
title: Ganzrationale ökonomische Funktionen
description: Ganzrationale ökonomische Funktionen – Skript
lernbereich: ganzrationale-oekonomische-funktionen
---

## Einführung

Allgemein verwenden wir die Abkürzungen **ME** für Mengeneinheit und **GE** für Geldeinheit.

In Abhängigkeit von der Menge $x$ betrachten wir folgende Funktionen:

### Preis-Absatz-Funktion

Die Preis-Absatz-Funktion $p(x)$ gibt an, wie hoch der Preis in GE pro abgesetzter ME ist. Da es keine negativen Preise gibt, gilt stets $p(x) \geq 0$. Es treten zwei Fälle auf:

- Im **Angebotspolypol** wird der Preis durch den Markt bestimmt. Dann ist $p(x)$ konstant, z. B. $p(x) = 32$ bei einem Marktpreis bzw. Gleichgewichtspreis von 32 GE.
- Im **Angebotsmonopol** kann das Unternehmen den Preis selbst festlegen. Da mit steigendem Preis die Absatzmenge sinkt, ist $p(x)$ eine monoton fallende Funktion. Wir betrachten in diesem abschnitt lineare Preis-Absatz-Funktionen mit negativer Steigung und positivem y-Achsenabschnitt, z. B. $p(x) = -5x + 60$.

### Erlösfunktion

Die Erlösfunktion $E(x)$ gibt den Gesamterlös in GE in Abhängigkeit von der Absatzmenge $x$ an. Da der Gesamterlös gleich Preis mal Menge ist, gilt

$$
E(x) = p(x) \cdot x
$$

- Im Beispiel zum Angebotspolypol ist

$$
\begin{align*}
E(x) &= p(x) \cdot x \\
     &= 32x
\end{align*}
$$

- Im Beispiel zum Angebotsmonopol ist

$$
\begin{align*}
E(x) &= (-5x + 60) \cdot x \\
     &= -5x^2 + 60x
\end{align*}
$$

### Kostenfunktion

Die Kostenfunktion $K(x)$ gibt die Gesamtkosten in GE in Abhängigkeit von der Absatzmenge $x$ an. Da die Kosten immer positiv und mit wachsender Menge zunehmend sind, ist $K(x)$ eine streng monoton wachsende Funktion. In diesem Abschnitt ist $K(x)$ eine ganzrationale Funktion dritten Grades, zum Beispiel

$$
K(x) = 0{,}5x^3 - 6x^2 + 30x + 48
$$

### Gewinnfunktion

Die Gewinnfunktion $G(x)$ ergibt sich aus der Differenz zwischen Erlös und Kosten:

$$
G(x) = E(x) - K(x)
$$

- Im Beispiel zum Angebotspolypol ist

$$
\begin{align*}
G(x) &= 32x - (0{,}5x^3 - 6x^2 + 30x + 48) \\
     &= 32x - 0{,}5x^3 + 6x^2 - 30x - 48 \\
     &= -0{,}5x^3 + 6x^2 - 2x - 48
\end{align*}
$$

- Im Beispiel zum Angebotsmonopol ist

$$
\begin{align*}
G(x) &= (-5x^2 + 60x) - (0{,}5x^3 - 6x^2 + 30x + 48) \\
&= -5x^2 + 60x - 0{,}5x^3 + 6x^2 - 30x - 48 \\
     &= -0{,}5x^3 + x^2 + 30x - 48
\end{align*}
$$

Sind zwei dieser vier ökonomischen Funktionen bekannt, können wir die übrigen zwei berechnen (außer die bekannten Funktionen waren $p$ und $E$).

{% include info.html
index="1"
frage="Berechnen von Gleichungen ökonomischer Funktionen mit Hilfe von $E(x)=p(x)\cdot x$ und $G(x)=E(x)-K(x)$ (Angebotspolypol)"
antwort="

- Sind $p(x)$ und $K(x)$ gegeben, können mit Hilfe der Formeln direkt $E(x)$ und $G(x)$ berechnet werden.
- Andernfalls müssen die Formeln umgestellt werden: $p(x)=\frac{E(x)}{x}$, $K(x)=E(x)-G(x)$ und $E(x)=G(x)+K(x)$.

"
%}

<div id="skript-aufgabe-1"></div>

{% include info.html
index="2"
frage="Berechnen von Gleichungen ökonomischer Funktionen mit Hilfe von $E(x)=p(x)\cdot x$ und $G(x)=E(x)-K(x)$ (Angebotsmonopol)"
antwort="siehe Info 1"
%}

<div id="skript-aufgabe-2"></div>

## Kennzahlen

Diese ökonomischen Funktionen werden mit Hilfe folgender Kennzahlen beschrieben und analysiert.

- **Marktpreis:** Preis im Marktgleichgewicht, auch Gleichgewichtspreis (Angebotspolypol).
- **Höchstpreis:** Maximaler Preis, den ein Konsument zu zahlen bereit ist (Angebotsmonopol).
- **Sättigungsmenge:** Absatzmenge, bei der trotz Preis null keine Nachfrage mehr besteht (Angebotsmonopol).
- **Erlösmaximale Menge:** Menge, bei der der Erlös maximal ist (Maximum der Erlösfunktion).
- **Maximaler Erlös:** Höchster möglicher Erlös, tritt bei der erlösmaximalen Menge auf.
- **Fixkosten:** Produktionsunabhängige Kosten (z. B. Miete).
- **Übergang vom degressiven zum progressiven Kostenwachstum:** Bis hierhin steigen die Kosten unterproportional, danach überproportional.
- **Gewinnschwelle:** Absatzmenge, ab der Gewinn erwirtschaftet wird (erste Nullstelle von $G(x)$).
- **Gewinngrenze:** Höchste Menge, bei der noch Gewinn erzielt wird (letzte Nullstelle von $G(x)$).
- **Gewinnmaximale Menge:** Menge, bei der der Gewinn maximal ist (Maximum der Gewinnfunktion).
- **Maximaler Gewinn:** Wert von $G(x)$ bei der gewinnmaximalen Menge.
- **Gewinnmaximaler Preis:** Preis bei der gewinnmaximalen Menge (Angebotsmonopol).
- **Break-even-Point:** Punkt, an dem Erlöse und Kosten gleich sind
- **Cournotscher Punkt:** Punkt auf $p(x)$ mit gewinnmaximaler Menge und gewinnmaximalem Preis

{% include info.html
index="3"
frage="Mathematische Definition ökonomischer Kennzahlen"
antwort="Beschreibung der Kennzahlen mit Hilfe mathematischer Fachbegriffe (y-Achsenabschnitt, Nullstelle, Extremstelle, Wendestelle)"
%}

<div id="skript-aufgabe-3"></div>

### Hinweise

- Eventuell müssen wir Kapazitätsgrenzen berücksichtigen. Liegt zum Beispiel im Angebotspolypol eine Kapazitätsgrenze vor, so ist die erlösmaximalen Menge, die im Angebotspolypol ohne Kapazitätsgrenze beliebig groß wäre, genau diese Kapazitätsgrenze.
- Denkbar wäre auch eine Kapazitätsgrenze unterhalb der lokalen Extremstelle (Maximum) der Gewinnfunktion. Dies müsste bei der Bestimmung der gewinnmaximalen Menge berücksichtigt werden.
- Wenn $G(x)$ stets negativ ist, d.h. wenn die Kosten immer größer als die Erlöse sind, gibt es weder eine Gewinnschwelle noch eine Gewinngrenze.

## Graphische Darstellung

Die beiden folgenden Diagramme veranschaulichen die ökonomischen Kennzahlen graphisch.

### Angebotsmonopol (mit Kapazitätsgrenze x=13)

{% include graph.html
   funktionen='[
    {"name":"E(x)", "term":"32x", "beschreibung":"Erlösfunktion"},
    {"name":"K(x)", "term":"0.5*x^3-6*x^2+30*x+48", "beschreibung":"Kostenfunktion"},
    {"name":"G(x)", "term":"-0.5*x^3+6x^2+2*x-48", "beschreibung":"Gewinnfunktion"},
    {"name":"p(x)", "term":"32", "beschreibung":"Preisfunktion"}
   ]'
   punkte='[
     {"x":0,"y":32,"text":"Marktpreis"},
     {"x":13,"y":0,"text":"Kapazitätsgrenze"},
     {"x":13,"y":416,"text":"erlösmaximale Menge und maximaler Erlös"},
     {"x":0,"y":48,"text":"Fixkosten"},
     {"x":4,"y":104,"text":"Übergang vom degressiven zum progressiven Kostenwachstum"},
     {"x":3.06,"y":0,"text":"Gewinnschwelle"},
     {"x":11.63,"y":0,"text":"Gewinngrenze"},
     {"x":8.16,"y":96.16,"text":"gewinnmaximale Menge und maximaler Gewinn"},
     {"x":3.06,"y":97.92,"text":"Break-even Point"},
     {"x":11.63,"y":372.16,"text":"Break-even Point"}
   ]'
   titel="Ökonomische Funktionen"
   xachse="Menge x in ME"
   yachse="Betrag y in GE"
   xmin=0
   xmax=14
   ymin=-100
   ymax=450
%}

### Angebotspolypol

{% include graph.html
   funktionen='[
    {"name":"E(x)", "term":"-5x^2+60x", "beschreibung":"Erlösfunktion"},
    {"name":"K(x)", "term":"0.5*x^3-6*x^2+30*x+48", "beschreibung":"Kostenfunktion"},
    {"name":"G(x)", "term":"-0.5*x^3+x^2+30*x-48", "beschreibung":"Gewinnfunktion"},
    {"name":"p(x)", "term":"-5x+60", "beschreibung":"Preisfunktion"}
   ]'
   punkte='[
     {"x":0,"y":60,"text":"Höchstpreis"},
     {"x":12,"y":0,"text":"Sättigungsmenge"},
     {"x":6,"y":180,"text":"erlösmaximale Menge und maximaler Erlös"},
     {"x":0,"y":48,"text":"Fixkosten"},
     {"x":4,"y":104,"text":"Übergang vom degressiven zum progressiven Kostenwachstum"},
     {"x":1.58,"y":0,"text":"Gewinnschwelle"},
     {"x":8,"y":0,"text":"Gewinngrenze"},
     {"x":5.19,"y":64.74,"text":"gewinnmaximale Menge und maximaler Gewinn"},
     {"x":5.19,"y":34.05,"text":"Cournotscher Punkt: gewinnmaximale Menge und gewinnmaximaler Preis"},
     {"x":1.58,"y":82.32,"text":"Break-even Point"},
     {"x":8,"y":160,"text":"Break-even Point"}
   ]'
   titel="Ökonomische Funktionen"
   xachse="Menge x in ME"
   yachse="Betrag y in GE"
   xmin=0
   xmax=12.5
   ymin=-100
   ymax=250
%}

{% include info.html
index="4"
frage="Graphische Bestimmung (Angebotspolypol)"
antwort="Graphische Interpretation mathematischer Fachbegriffe (y-Achsenabschnitt, Nullstellen, Extremstellen, Wendestellen)"

%}

<div id="skript-aufgabe-4"></div>

{% include info.html
index="5"
frage="Graphische Bestimmung (Angebotsmonopol)"
antwort="siehe Info 4"
%}

<div id="skript-aufgabe-5"></div>

## Berechnung

Um ökonomische Kennzahlen berechnen zu können, benötigen wir die unter anderem die Werkzeuge der Differentialrechnung. Um die Kennzahlen berechnen zu können, ist es nun wichtig, den richtigen mathematischen Ansatz zu wählen.

{% include info.html
index="6"
frage="Ansatz zur Berechnung charakteristischer Punkte einer Funktion $f(x)$."
antwort="

- y-Abschnitt: $f(0)$
- Nullstellen: $f(x)=0$
- Extremstellen: Notwendige Bedingung $f'(x) = 0$, hinreichende Bedingung $f'\'(x) > 0$ (Minimum) oder $f'\'(x) < 0$ (Maximum)
- Wendestellen: Notwendige Bedingung $f'\'(x) = 0$, hinreichende Bedingung $f''\'(x) > 0$ (minimale Steigung) oder $f''\'(x)<0$ (maximale Steigung)
  "
  %}

<div id="skript-aufgabe-6"></div>

{% include info.html
index="7"
frage="Berechnung ökonomischer Kennzahlen (Angebotspolypol)."
antwort="

### Marktpreis

Es seien $p(x)=32$ und so $E(x)=32x$. Der Markpreis beträgt hier 32 GE.

Für weitere Kennzahlen siehe Info 8.
"
%}

{% include info.html
index="8"
frage="Berechnung ökonomischer Kennzahlen (Angebotsmonopol). Den Beispielen liegen folgende Funktionen zugrunde:

$$
\begin{align*}
p(x)&=-5x+60\\
E(x)&=-5x^2+60x\\
K(x)&=0{,}5x^3-6x^2+30x+48\\
G(x)&=-0{,}5x^3+x^2+30x-48
\end{align*}
$$

"

antwort="

### Höchstpreis

Der y-Achsenabschnitt von $p(x) = -5x + 60$:

$$
p(0) = 60
$$

Der Höchstpreis beträgt 60 GE.

### Sättigungsmenge

Nullstelle von $p(x)$:

$$
\begin{align*}
-5x + 60 &= 0 \\
x &= 12
\end{align*}
$$

Die Sättigungsmenge beträgt 12 ME.

### Erlösmaximale Menge

Extremstelle von $E(x) = -5x^2 + 60x$:

Bestimme $E'(x)=-10x+60$ und $E'\'(x)=-10$.

$$
\begin{align*}
-10x + 60 &= 0 \Rightarrow x = 6\\
E'\'(6)&=-10 < 0 (Maximum)
\end{align*}
$$

Die erlösmaximale Menge beträgt 6 ME.

### Maximaler Erlös

Einsetzen der erlösmaximale Menge in $E(x)$:

$$
E(6) = -5 \cdot 6^2 + 60 \cdot 6 = -180 + 360 = 180
$$

Der maximale Erlös beträgt 180 GE.

### Fixkosten

y-Achsenabschnitt der Kostenfunktion $K(x)=0{,}5x^3-6x^2+30x+48$:

$$
K(0) = 48
$$

Die Fixkosten betragen 48 GE.

### Übergang vom degressiven zum progressiven Kostenwachstum

Wendestelle von $K(x)=0{,}5x^3-6x^2+30x+48$:

Bestimme $K'\'(x)=3x-12$ und $K''\'(x)=3$

$$
\begin{align*}
3x - 12 =  0 \Rightarrow x = 4\\
K''\'(4)=3 > 0 \text{ (minimale Steigung)}
\end{align*}
$$

Der Übergang vom degressiven zum progressiven Kostenwachstum findet bei 4 ME statt.

### Gewinnschwelle und Gewinngrenze

Erste und letzte positive Nullstelle von $G(x)=-0{,}5x^3+x^2+30x-48$:

$$
\begin{align*}
-0{,}5x^3 + x^2 + 30x - 48 &=0 \Rightarrow x_1=-7{,}58,\ x_2=1{,}58,\ x_3=8\\
(x_1&=-7{,}58 \text{ liegt nicht im ökonomischen Definitionsbereich})
\end{align*}
$$

Die Gewinnschwelle beträgt 1,53 ME und die Gewinngrenze bei 8 ME .

### Gewinnmaximale Menge

Extremstelle von $G(x)=-0{,}5x^3+x^2+30x-48$:

Bestimme $G'(x)= -1{,}5x^2 + 2x + 30 $ und $G'\'(x)=-3x+2$

$$
\begin{align*}
-1{,}5x^2 + 2x + 30 & = 0 \Rightarrow x_1=-3{,}86,\ x_2=5{,}19\\
G'\'(5{,}19)&=-3\cdot 5{,}19+2=-13{,}57<0 \text{ (Maximum)}\\
(x_1&=-3{,}86\text{ liegt nicht im ökonomischen Definitionsbereich})
\end{align*}
$$

Die gewinnmaximale Menge beträgt 5,19 GE.

### Maximaler Gewinn

Einsetzen der gewinnmaximalen Menge in $G(x)$:

$$
G(5{,}19) = 64{,}74
$$

Der maximale Gewinn beträgt 64,74 GE.

### Gewinnmaximaler Preis

Einsetzen der gewinnmaximalen Menge in $p(x)$:

$$
p(5{,}19) = 34{,}05
$$

Der gewinnmaximale Preis beträgt 34,05 GE.

"
%}

<div id="skript-aufgabe-7"></div>

<div id="skript-aufgabe-8"></div>
