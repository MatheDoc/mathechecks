---
layout: module
title: Ganzrationale ökonomische Funktionen - Skript
description: Lernbereich Ganzrationale ökonomische Funktionen, Modul Skript.
page_context: Lernbereich
nav: dashboard
body_class: page-module
module_key: skript
published: true
lernbereich: ganzrationale-oekonomische-funktionen
gebiet: analysis
permalink: /lernbereiche/analysis/ganzrationale-oekonomische-funktionen/skript.html
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
     &= -0{,}5x^3 + 6x^2 + 2x - 48
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

{% include check-anker.html nummer=1 %}

Dasselbe Prinzip gilt für das Angebotsmonopol, wo zusätzlich die Erlösfunktion $E(x)=p(x)\cdot x$ als Produkt aus Preis-Absatz-Funktion und Menge gebildet wird.

{% include check-anker.html nummer=2 %}


## Kennzahlen

Diese ökonomischen Funktionen werden mit Hilfe folgender Kennzahlen beschrieben und analysiert.

|Kennzahl| Symbol | Beschreibung| Definition|
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

Graphen geben eine schnelle Übersicht über alle Kennzahlen, bevor sie rechnerisch bestimmt werden. Entscheidend ist dabei, welche Kurve jeweils abgelesen oder geometrisch ausgewertet wird.

### Angebotspolypol

Im Angebotspolypol ist $E(x) = p \cdot x$ eine Gerade mit Steigung $p$. Da eine Gerade kein inneres Maximum besitzt, fällt die erlösmaximale Menge mit der **Kapazitätsgrenze** zusammen. Das folgende Diagramm zeigt die vier ökonomischen Funktionen für das Beispiel aus der Einführung mit Kapazitätsgrenze bei 13 ME:

{% include graph.html
   funktionen='[
    {"name":"E(x)", "term":"32*x", "beschreibung":"Erlösfunktion"},
    {"name":"K(x)", "term":"0.5*x^3-6*x^2+30*x+48", "beschreibung":"Kostenfunktion"},
    {"name":"G(x)", "term":"-0.5*x^3+6*x^2+2*x-48", "beschreibung":"Gewinnfunktion"},
    {"name":"p(x)", "term":"32", "beschreibung":"Preis-Absatz-Funktion"}
   ]'
   titel="Ökonomische Funktionen (Polypol)"
   xachse="Menge x in ME"
   yachse="Betrag y in GE"
   xmin=0
   xmax=14
   ymin=-100
   ymax=450
%}

Alle Kennzahlen aus der Tabelle lassen sich direkt am Graphen ablesen:

- **Marktpreis**: konstante Höhe von $p(x)$, gleichzeitig Steigung von $E(x)$
- **Erlösmaximale Menge und maximaler Erlös**: $x$- und $y$-Koordinate am rechten Ende von $E(x)$ an der Kapazitätsgrenze
- **Fixkosten** $K_f$: $y$-Achsenabschnitt von $K(x)$
- **Übergang degressiv/progressiv**: Wendepunkt von $K(x)$, d. h. die Stelle, an der $K(x)$ von links- nach rechtsgekrümmt übergeht
- **Gewinnschwelle und Gewinngrenze**: Nullstellen von $G(x)$
- **Gewinnmaximale Menge und maximaler Gewinn**: Hochpunkt von $G(x)$
- **Break-even-Punkte**: Schnittpunkte von $E(x)$ und $K(x)$

{% include check-anker.html nummer=3 %}

### Angebotsmonopol

Im Angebotsmonopol fällt $p(x)$, sodass $E(x) = p(x) \cdot x$ eine Parabel mit echtem inneren Maximum wird. Neben den aus dem Polypol bekannten Kennzahlen treten im Monopol weitere auf:

{% include graph.html
   funktionen='[
    {"name":"E(x)", "term":"-5*x^2+60*x", "beschreibung":"Erlösfunktion"},
    {"name":"K(x)", "term":"0.5*x^3-6*x^2+30*x+48", "beschreibung":"Kostenfunktion"},
    {"name":"G(x)", "term":"-0.5*x^3+x^2+30*x-48", "beschreibung":"Gewinnfunktion"},
    {"name":"p(x)", "term":"-5*x+60", "beschreibung":"Preis-Absatz-Funktion"}
   ]'
   titel="Ökonomische Funktionen (Monopol)"
   xachse="Menge x in ME"
   yachse="Betrag y in GE"
   xmin=0
   xmax=12.5
   ymin=-100
   ymax=250
%}

- **Höchstpreis** $p_H$: $y$-Achsenabschnitt von $p(x)$ — Preisobergrenze, ab der keine Nachfrage mehr besteht
- **Sättigungsmenge** $s_m$: Nullstelle von $p(x)$ — Menge, ab der der Marktpreis auf null fällt
- **Erlösmaximale Menge**: Hochpunkt von $E(x)$ — nun ein echtes inneres Maximum, kein Randpunkt
- **Cournotscher Punkt** $C(x_{Gmax}|p_{Gmax})$: Punkt auf $p(x)$ zur gewinnmaximalen Menge $x_{Gmax}$

{% include check-anker.html nummer=4 %}



## Berechnungen

Alle Kennzahlen lassen sich nicht nur graphisch ablesen, sondern auch rechnerisch bestimmen. Grundlage dafür sind die Werkzeuge der Differentialrechnung. Der erste Schritt ist stets, die gesuchte Kennzahl dem richtigen mathematischen Konzept zuzuordnen:

| Mathematisches Konzept | Zugehörige Kennzahlen |
|---|---|
| $y$-Achsenabschnitt: $f(0)$ | $p_H$, $K_f$ |
| Nullstelle: $f(x)=0$ lösen | $s_m$, $x_{GS}$, $x_{GG}$ |
| Extremstelle (Maximum): $f'(x)=0$, $f''(x)<0$ | $x_{Emax}$ (nur Monopol), $x_{Gmax}$ |
| Wendestelle: $f''(x)=0$, $f'''(x)\neq 0$ | $x_w$ |
| $y$-Wert an bekannter Stelle: Einsetzen | $E_{max}$, $G_{max}$, $p_{max}$ |

Im Polypol hat $E(x)$ kein inneres Maximum — die erlösmaximale Menge ist die Kapazitätsgrenze, also kein Extremstellenproblem.

{% include check-anker.html nummer=5 %}

Sind die Ansätze bekannt, können wir die Kennzahlen vollständig durchrechnen — zunächst für das Angebotspolypol, wo die lineare Erlösfunktion den Rechenweg etwas vereinfacht.

{% include check-anker.html nummer=6 %}

Im Angebotsmonopol kommen Höchstpreis, Sättigungsmenge und Cournotscher Punkt als zusätzliche Kennzahlen hinzu. Der Rechenweg folgt dabei strukturell denselben Konzepten.

{% include check-anker.html nummer=7 %}






