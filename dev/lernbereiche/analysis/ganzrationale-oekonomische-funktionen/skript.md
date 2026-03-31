---
layout: dev-module
title: Ganzrationale ökonomische Funktionen - Skript (Dev)
description: Dev-Lernbereich Ganzrationale ökonomische Funktionen, Modul Skript.
page_context: Lernbereich
nav: dashboard
body_class: page-module-designs
module_key: skript
published: true
lernbereich: ganzrationale-oekonomische-funktionen
gebiet: analysis
permalink: /dev/lernbereiche/analysis/ganzrationale-oekonomische-funktionen/skript.html
---

## Einführung

Allgemein verwenden wir die Abkürzungen **ME** für Mengeneinheit und **GE** für Geldeinheit. In Abhängigkeit von der Menge $x$ werden wir folgende Funktionen betrachten:

### Preis-Absatz-Funktion

Die Preis-Absatz-Funktion $p(x)$ gibt an, wie hoch der Preis in GE pro abgesetzter ME ist. Da es keine negativen Preise gibt, gilt stets $p(x) \geq 0$. Es treten zwei Fälle auf:

- Im **Angebotspolypol** wird der Preis durch den Markt bestimmt. Dann ist $p(x)$ konstant, z. B. $p(x) = 32$ bei einem Marktpreis bzw. Gleichgewichtspreis von 32 GE.
- Im **Angebotsmonopol** kann das Unternehmen den Preis selbst festlegen. Da mit steigendem Preis die Absatzmenge sinkt, ist $p(x)$ eine monoton fallende Funktion. Wir betrachten in diesem Abschnitt lineare Preis-Absatz-Funktionen mit negativer Steigung und positivem y-Achsenabschnitt, z. B. $p(x) = -5x + 60$.

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

Sind zwei dieser vier ökonomischen Funktionen bekannt, können wir die übrigen zwei berechnen (außer die bekannten Funktionen wären $p$ und $E$).

{% include dev/check-anker.html nummer="1" %}

{% include dev/check-anker.html nummer="2" %}




## Kennzahlen

Diese ökonomischen Funktionen werden mit Hilfe folgender Kennzahlen beschrieben und analysiert.

- **Marktpreis:** Preis im Marktgleichgewicht, auch Gleichgewichtspreis (Angebotspolypol).
- **Höchstpreis:** Maximaler Preis, den ein Konsument zu zahlen bereit ist (Angebotsmonopol).
- **Sättigungsmenge:** Absatzmenge, bei der trotz Preis null keine Nachfrage mehr besteht (Angebotsmonopol).
- **Erlösmaximale Menge:** Menge, bei der der Erlös maximal ist (Maximum der Erlösfunktion).
- **Maximaler Erlös:** Höchster möglicher Erlös, tritt bei der erlösmaximalen Menge auf.
- **Fixkosten:** Produktionsunabhängige Kosten (z. B. Miete).
- **Übergang vom degressiven zum progressiven Kostenwachstum:** Menge, bis zu der die Kosten unterproportional steigen, danach überproportional.
- **Gewinnschwelle:** Absatzmenge, ab der Gewinn erwirtschaftet wird (erste Nullstelle von $G(x)$).
- **Gewinngrenze:** Höchste Menge, bei der noch Gewinn erzielt wird (letzte Nullstelle von $G(x)$).
- **Gewinnmaximale Menge:** Menge, bei der der Gewinn maximal ist (Maximum der Gewinnfunktion).
- **Maximaler Gewinn:** Wert von $G(x)$ bei der gewinnmaximalen Menge.
- **Gewinnmaximaler Preis:** Preis bei der gewinnmaximalen Menge (Angebotsmonopol).
- **Break-even-Point:** Punkt, an dem Erlöse und Kosten gleich sind
- **Cournotscher Punkt:** Punkt auf $p(x)$ mit gewinnmaximaler Menge und gewinnmaximalem Preis


{% include dev/check-anker.html nummer="3" %}

### Hinweise

- Eventuell müssen wir Kapazitätsgrenzen berücksichtigen. Liegt zum Beispiel im Angebotspolypol eine Kapazitätsgrenze vor, so ist die erlösmaximalen Menge, die im Angebotspolypol ohne Kapazitätsgrenze beliebig groß wäre, genau diese Kapazitätsgrenze.
- Denkbar wäre auch eine Kapazitätsgrenze unterhalb der lokalen Extremstelle (Maximum) der Gewinnfunktion. Dies müsste bei der Bestimmung der gewinnmaximalen Menge berücksichtigt werden.
- Wenn $G(x)$ stets negativ ist, d.h. wenn die Kosten immer größer als die Erlöse sind, gibt es weder eine Gewinnschwelle noch eine Gewinngrenze.

## Graphische Darstellungen


### Angebotsmonopol

Das folgende Diagramm zeigt die Funktionen $E(x)$, $K(x)$, $G(x)$ und $p(x)$ für ein Angebotsmonopol mit Kapazitätsgrenze bei 13 ME.

{% include dev/graph.html
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

{% include dev/check-anker.html nummer="4" %}

### Angebotspolypol

Das folgende Diagramm zeigt die Funktionen $E(x)$, $K(x)$, $G(x)$ und $p(x)$ für ein Angebotspolypol. 

{% include dev/graph.html
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

{% include dev/check-anker.html nummer="5" %}



## Berechnungen

Um ökonomische Kennzahlen berechnen zu können, benötigen wir die unter anderem die Werkzeuge der Differentialrechnung. Um die Kennzahlen berechnen zu können, ist es nun wichtig, den richtigen mathematischen Ansatz zu wählen.

{% include dev/check-anker.html nummer="6" %}

Jetzt sind wir in der Lage, die ökonomischen Kennzahlen mit Hilfe der analytischer Methoden zu berechnen. Wir erinnern an dieser Stelle an den Ansatz zur Berechnung charakteristischer Punkte einer Funktion $f(x)$:

- y-Abschnitt: $f(0)$
- Nullstellen: $f(x)=0$
- Extremstellen: Notwendige Bedingung $f^{\prime}(x) = 0$, hinreichende Bedingung $f^{\prime\prime}(x) > 0$ (Minimum) oder $f^{\prime\prime}(x) < 0$ (Maximum)
- Wendestellen: Notwendige Bedingung $f^{\prime\prime}(x) = 0$, hinreichende Bedingung $f^{\prime\prime\prime}(x) > 0$ (minimale Steigung) oder $f^{\prime\prime\prime}(x)<0$ (maximale Steigung)

{% include dev/check-anker.html nummer="7" %}

{% include dev/check-anker.html nummer="8" %}





