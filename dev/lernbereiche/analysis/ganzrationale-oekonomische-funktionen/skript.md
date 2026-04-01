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

|Kennzahl| Symbol | Beschreibung|Mathematische Definition|
|---|---|---|---|
|Marktpreis| $p$|Preis im Marktgleichgewicht, auch Gleichgewichtspreis (Angebotspolypol)| konstante Wert $p$|
|Höchstpreis| $p_H$ | Maximaler Preis, den ein Konsument zu zahlen bereit ist (Angebotsmonopol)| $y$-Abschnitt von $p(x)$|
|Sättigungsmenge| $s_m$ | Absatzmenge, bei der trotz Preis null keine Nachfrage mehr besteht (Angebotsmonopol)| Nullstelle von $p(x)$|
|Erlösmaximale Menge| $x_{Emax}$ | Menge, bei der der Erlös maximal ist| Extremstelle (Maximum) von $E(x)$|
|Maximaler Erlös| $E_{max}$ | Höchster möglicher Erlös, tritt bei der erlösmaximalen Menge auf| $E(x_{Emax})$ |
|Fixkosten| $K_f$ | Produktionsunabhängige Kosten (z. B. Miete)| $y$-Abschnitt von $K(x)$|
|Übergang degressives/progressives Kostenwachstum| $x_w$|Menge, bis zu der die Kosten unterproportional steigen, danach überproportional|  Wendestelle von $K(x)$|
|Gewinnschwelle| $x_{GS}$|Absatzmenge, ab der Gewinn erwirtschaftet wird| erste Nullstelle von $G(x)$|
|Gewinngrenze| $x_{GG}$|Höchste Menge, bei der noch Gewinn erzielt wird| letzte Nullstelle von $G(x)$|
|Gewinnmaximale Menge| $x_{Gmax}$|Menge, bei der der Gewinn maximal ist| Extremstelle (Maximum) $G(x)$|
|Maximaler Gewinn| $G_{max}$|Wert von $G(x)$ bei der gewinnmaximalen Menge| $G(x_{Gmax})$|
|Gewinnmaximaler Preis| $p_{max}$|Preis, bei dem die Gewinne maximiert werden (Angebotsmonopol)|  $p(x_{Gmax})$|
|Break-even-Point| $BEP$ | Punkt, an dem Erlöse und Kosten gleich sind| Schnittpunkt von $E(x)$ und $K(x)$|
|Cournotscher Punkt| $C$ | Punkt auf $p(x)$ mit gewinnmaximaler Menge und gewinnmaximalem Preis| $C(x_{Gmax};p_{Gmax})$|


### Hinweise

- Eventuell müssen wir Kapazitätsgrenzen berücksichtigen. Liegt zum Beispiel im Angebotspolypol eine Kapazitätsgrenze vor, so ist die erlösmaximalen Menge, die im Angebotspolypol ohne Kapazitätsgrenze beliebig groß wäre, genau diese Kapazitätsgrenze.
- Denkbar wäre auch eine Kapazitätsgrenze unterhalb der lokalen Extremstelle (Maximum) der Gewinnfunktion. Dies müsste bei der Bestimmung der gewinnmaximalen Menge berücksichtigt werden.
- Wenn $G(x)$ stets negativ ist, d.h. wenn die Kosten immer größer als die Erlöse sind, gibt es weder eine Gewinnschwelle noch eine Gewinngrenze.

## Graphische Darstellungen


### Angebotsmonopol

{% include dev/check-anker.html nummer="3" %}

### Angebotspolypol


{% include dev/check-anker.html nummer="4" %}



## Berechnungen

Um ökonomische Kennzahlen berechnen zu können, benötigen wir die unter anderem die Werkzeuge der Differentialrechnung. Um die Kennzahlen berechnen zu können, ist es nun wichtig, den richtigen mathematischen Ansatz zu wählen.

{% include dev/check-anker.html nummer="5" %}

Jetzt sind wir in der Lage, die ökonomischen Kennzahlen mit Hilfe der analytischer Methoden zu berechnen.

{% include dev/check-anker.html nummer="6" %}

{% include dev/check-anker.html nummer="7" %}





