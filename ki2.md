---
layout: shell
title: Regression und neuronale Netze
description: Arbeitsnotizen zu Regression, Bildungsplanbezug und neuronalen Netzen.
body_class: page-legal
published: true
permalink: /ki2.html
---

# Regression

## Training durch Regression

[Dieses Widget](training_als_schrittweise_regression.html)  veranschaulicht die Grundidee des Trainings eines kleinen neuronalen Netzes durch Gradientenabstieg: Das Netz berechnet Vorhersagen, bestimmt den Fehler und passt seine Gewichte schrittweise so an, dass der mittlere quadratische Fehler kleiner wird.


## Fehlvorstellungen
- Unterschied zwischen "Steckbriefaufgaben" und Regression beachten:
    - Bei Steckbriefaufgaben liefert jeder Datenpunkt (durch Einsetzen) eine Gleichung im LGS; die Anzahl der Gleichungen entspricht also der Anzahl der Datenpunkte.
    - Bei der Regression entspricht dagegen **nicht** ein Datenpunkt einer Gleichung im LGS. Stattdessen bestimmt die Anzahl der Funktionsparameter (z. B. bei linearer, quadratischer Regression) die Anzahl der Gleichungen im sogenannten *Normalgleichungssystem* $X^TXw=X^Ty$, dies ist unabhängig von der Anzahl $n$ der Datenpunkte.
    - Konsequenz: Ist $n$ kleiner als die Anzahl der Parameter, ist $X^TX$ nicht invertierbar und das Normalgleichungssystem nicht eindeutig lösbar:
        - 1 Datenpunkt bei einer affin-linearen Regression $\mathbb{R}\to\mathbb{R}$ (2 Parameter $m,b$) führt zu 2 Gleichungen mit 2 Unbekannten, diese sind aber linear abhängig (durch einen Punkt gehen unendlich viele Geraden).
        - Ähnlich führen 2 Datenpunkte bei einer affin-linearen Regression $\mathbb{R}^2\to\mathbb{R}$ (3 Parameter $w_1,w_2,b$) zu 3 Gleichungen mit 3 Unbekannten, die wiederum linear abhängig sind (durch 2 Punkte gehen unendlich viele Ebenen).
        - Allgemein gilt: $X^TX$ ist nur invertierbar, wenn $n$ mindestens so groß wie die Anzahl der Parameter ist und die Datenpunkte "in allgemeiner Lage" sind (d. h. $X$ hat vollen Spaltenrang).


## Multiple lineare Regression
- Setting: Aus $n$ Datenpunkten die lineare Regressionsfunktion $\mathbb{R}^m\to\mathbb{R}$ finden. Z. B.: $n=4$ und $m=2$
- Gegeben: $((x_{11},x_{12}) \mid y_1)$, $((x_{21},x_{22}) \mid y_2)$, $((x_{31},x_{32}) \mid y_3)$, $((x_{41},x_{42}) \mid y_4)$
- Gesucht: "beste"/fehlerquadrat-minimierende Funktion
$$
w=(w_1,w_2,b):\mathbb{R}^2\to\mathbb{R}, \quad (x_1,x_2) \mapsto w_1x_1+w_2x_2+b
$$
- Dann ist $w=(X^TX)^{-1}X^Ty$, wobei
$$
X=\begin{pmatrix} x_{11} & x_{12} & 1 \\ x_{21} & x_{22} & 1 \\ x_{31} & x_{32} & 1 \\ x_{41} & x_{42} & 1 \end{pmatrix}, \qquad y=\begin{pmatrix} y_1\\y_2\\y_3\\y_4 \end{pmatrix}
$$

- Hinweis: keine geschlossene Formel für nicht-lineare Regression

### Spezialfall: n=2, m=1

Gegeben: $(x_1\mid y_1)$, $(x_2\mid y_2)$

$$
X=\begin{pmatrix} x_1 & 1 \\ x_2 & 1 \end{pmatrix}, \qquad y=\begin{pmatrix} y_1 \\ y_2 \end{pmatrix}
$$

$X^TX$ ist invertierbar, falls $x_1 \neq x_2$.

Dann führt $w=(X^TX)^{-1}X^Ty=(m,b)$ zu den gewöhnlichen Gleichungen der Geraden durch zwei Punkte:
$$
m=\frac{y_2-y_1}{x_2-x_1}
$$
und
$$
b=\frac{x_2y_1-x_1y_2}{x_2-x_1} \quad (=y_1-mx_1)
$$


### Spezialfall: n allgemein, m=1

D. h. gesucht ist eine lineare Regression $\mathbb{R}\to\mathbb{R}$ aus $n$ Datenpunkten $(x_1\mid y_1),\dots,(x_n\mid y_n)$.

Dann führt $w=(X^TX)^{-1}X^Ty=(m,b)$ zu den gewöhnlichen Formeln der eindimensionalen linearen Regression:

$$
m=\frac{\sum_{i=1}^n (x_i-\bar x)(y_i-\bar y)}{\sum_{i=1}^n (x_i-\bar x)^2}
$$

und

$$
b=\bar y - m\bar x
$$

mit $\bar x=\frac1n\sum_{i=1}^n x_i$ und $\bar y=\frac1n\sum_{i=1}^n y_i$.


<!--# Vorläufiger Bildungsplan
Sie nutzen das arithmetische Mittel zum Clustern von Daten mit einer Veränderlichen und verwenden dabei auch den k-Means Algorithmus (Z 5). Bei Daten mit zwei Veränderlichen visualisieren sie Cluster in Streudiagrammen (Z 6). Sie identifizieren die Bedeutung von Cluster-Algorithmen in privaten und beruflichen Kontexten (Z 7).

Zur Erstellung von Regressionsfunktionen aus funktionalen Zusammenhängen mit einer oder zwei veränderlichen verwenden sie die Methode der kleinsten Fehlerquadrate, Ableitungen nach Parametern und lineare Gleichungssysteme(Z 4). Sie ordnen die lineare Regression in den Bereich maschinellen Lernens als Teilbereich Künstlicher Intelligenz ein und treffen auf der Basis der Regressionsfunktionen Prognosen (Z 5).

Im Rahmen betrieblicher Abläufe nutzen sie die Grundlagen neuronaler Netze für Klassifizierungsprobleme und beurteilen die gesellschaftliche Bedeutung automatisierter Prozesse.

Sie nutzen neuronale Netze mit höchstens einer verborgenen Schicht für Klassifizierungen (Z 5). Sie verwenden Gewichtsmatrizen und Aktivierungsfunktionen (z. B. Identitäts-Funktion, Heaviside-Funktion, Sigmoid-Funktion) zur Berechnung von Outputvektoren aus vorgegebenen Inputvektoren mit Bias (Z 6). Sie beurteilen die Eignung von gegebenen Gewichtsmatrizen mit Hilfe der Fehlerfunktion (Summe der Fehlerquadrate) (Z 7).-->


# Mögliche Unterrichtsthemen

Die folgenden Punkte konkretisieren die Bildungsplan-Vorgaben zu neuronalen Netzen für den Unterricht (ohne Clustering).

## Input-Output-Beziehung

### Allgemeines
- Analogie zu mehrstufigen Produktionsprozessen (z. B. verborgene Schicht = Zwischenprodukte) betonen.
- Aktivierungsfunktion diskutieren: Sollte man überhaupt nichtlineare Aktivierungsfunktionen betrachten? Schüler kennen aktuell weder tanh noch Sigmoid o. Ä. aus dem Unterricht.
- Input und Output stets als Spaltenvektor notieren (anschlussfähig an bestehende Vektor-/Matrizenschreibweise aus der linearen Algebra).


### Mögliche Aufgabentypen
- Output-Vektor aus gegebenem Input-Vektor, Gewichtsmatrix und Bias berechnen (ohne Aktivierungsfunktion).
- Wert nach Anwendung der Aktivierungsfunktion berechnen und anwendungsbezogen interpretieren/klassifizieren (z. B. rot/blau/gelb je nach Schwellenwert).
- Heaviside- und Sigmoid-Aktivierung am selben Beispiel vergleichen (harter Schwellenwert vs. weicher Übergang).
- Aus einem Netzdiagramm die zugehörige Gewichtsmatrix aufstellen (und umgekehrt).
- Umkehrproblem bei Identitätsaktivierung: Gegebener Output-Vektor und (quadratische, invertierbare) Gewichtsmatrix, gesuchten Input-Vektor durch Lösen des LGS bestimmen. Kontrastiert "Netz vorwärts anwenden" mit "Netz invertieren" (in der Praxis meist nicht möglich, da Gewichtsmatrizen i. Allg. nicht quadratisch/invertierbar sind).
- Entscheidungsgrenze bei einem Neuron mit zwei Inputs und Heaviside-Aktivierung: Aus $w_1x_1+w_2x_2+b=0$ die Geradengleichung in der $x_1$-$x_2$-Ebene bestimmen und ins Streudiagramm einzeichnen (Anschluss an Geradengleichungen/Halbebenen aus der analytischen Geometrie).


## Training

### Allgemeines
- Allgemein gesucht ist eine hochgradig nichtlineare, multidimensionale Regressionsfunktion.
- Aber bereits die lineare Regression skaliert schlecht wegen der Berechnung von $(X^TX)^{-1}$.
- Training erfolgt in der Praxis über Gradient Descent u. Ä.
- Der Bildungsplan verlangt kein eigenständiges Training (Z 7: "beurteilen die Eignung von gegebenen Gewichtsmatrizen mit Hilfe der Fehlerfunktion"), sondern nur die Bewertung bereits vorgegebener Gewichtsmatrizen. Das entschärft die unten genannte Schwierigkeit fehlender partieller Ableitungen.

### Mögliche Aufgabentypen
- Den konkreten Trainingsvorgang rechnerisch zu bearbeiten ist schwierig – selbst einfaches Gradient Descent ist kaum möglich, da den Schülern keine partiellen Ableitungen zur Verfügung stehen.
- Stattdessen: Zwei neuronale Netze mit bekannter Aktivierungs- und Fehlerfunktion sowie bekannten Ist- und Soll-Werten vorlegen; Schüler bestimmen, welches Netz besser trainiert ist.
- Einfacher: Fehler (Summe der Fehlerquadrate) für ein einzelnes Netz berechnen.
- Multiple lineare Regression mit dem Taschenrechner durchführen (Formel siehe oben).
- Zu einem gegebenen Netz mit einer verborgenen Schicht und einem Datensatz prüfen lassen, ob eine kleine, vorgeschlagene Änderung einzelner Gewichte den Gesamtfehler verringert oder vergrößert – als Annäherung an die Grundidee von Gradient Descent ohne Ableitungen.
- Exaktes Minimum bei Identitätsaktivierung: Fehler als Funktion eines einzelnen Gewichts $w_1$ auffassen (alle übrigen Gewichte/Inputs fest einsetzen). Es ergibt sich eine gewöhnliche Parabel $E(w_1)=(y-(w_1x_1+w_2x_2+b))^2$. Scheitelpunkt bestimmen bzw. Ableitung null setzen liefert das exakt optimale Gewicht ohne iteratives Verfahren.
- Koordinatenweises Training über mehrere Schritte: abwechselnd $w_1$, dann $w_2$, dann $b$ optimieren (jeweils die anderen fest). Hierbei genügt reine eindimensionale Kettenregel. Ausführliches Beispiel siehe unten.

#### Ausführliches Beispiel: Koordinatenweises Training

**Netzarchitektur:** möglichst einfach gehalten, damit gewöhnliche (eindimensionale) Kettenregel genügt: ein Input, eine verborgene Schicht mit einem Neuron, ein Output-Neuron, also je Schicht nur ein Neuron und damit Zahlen statt Vektoren/Matrizen als Gewichte:

- Input: $x$
- verborgene Schicht: $h=\sigma(w_1x+b_1)$
- Output: $\hat y=\sigma(w_2h+b_2)$

mit Sigmoid-Aktivierung $\sigma(z)=\frac{1}{1+e^{-z}}$ in **beiden** Schichten (nötig, damit überhaupt abgeleitet werden kann, Heaviside scheidet hier z.B. aus). Vier Parameter: $w_1,b_1,w_2,b_2$. Fehlerfunktion für einen Datenpunkt $(x\mid y)$: $E=(y-\hat y)^2$.

**Koordinatenweises Vorgehen:** Statt gleichzeitig nach allen vier Parametern abzuleiten (Gradient/partielle Ableitungen), wird nacheinander jeweils *ein* Parameter als Variable betrachtet, alle anderen als aktuell feste Zahlen eingesetzt. Für jeden Parameter wird $E$ so zu einer gewöhnlichen reellen Funktion einer Variablen, auf die die gewöhnliche Kettenregel angewendet wird. Nach jedem Schritt wird der neue Wert übernommen, bevor der nächste Parameter behandelt wird.

**Konkrete Daten:** Datenpunkt $x=1$, Soll-Wert $y=1$, Lernrate $\eta=1$. Startgewichte: $w_1=0{,}5,\ b_1=0,\ w_2=0{,}5,\ b_2=0$.

*Startfehler:* $h=\sigma(0{,}5)\approx0{,}6225$, $\hat y=\sigma(0{,}3113)\approx0{,}5772$, $E\approx(1-0{,}5772)^2\approx0{,}1788$.

**Schritt 1 – Update von $w_2$** (nur $w_2$ variabel; $h=0{,}6225$, $b_2=0$ fest):
$$E(w_2)=(1-\sigma(w_2h+b_2))^2,\qquad \frac{dE}{dw_2}=-2(1-\hat y)\,\sigma'(z_2)\,h$$
$\frac{dE}{dw_2}\approx-2\cdot0{,}4228\cdot0{,}2441\cdot0{,}6225\approx-0{,}1285$
Update: $w_2^{neu}=0{,}5-1\cdot(-0{,}1285)\approx0{,}6285$

**Schritt 2 – Update von $b_2$** (jetzt $w_2=0{,}6285$ fest, $h=0{,}6225$ fest):
$$\frac{dE}{db_2}=-2(1-\hat y)\,\sigma'(z_2)\approx-2\cdot0{,}4034\cdot0{,}2407\approx-0{,}1942$$
Update: $b_2^{neu}=0-1\cdot(-0{,}1942)\approx0{,}1942$

**Schritt 3 – Update von $w_1$** (jetzt $b_1=0,\ w_2=0{,}6285,\ b_2=0{,}1942$ fest; Kettenregel über *zwei* Sigmoid-Stufen, aber weiterhin nur eindimensional, da nur $w_1$ variiert):
$$\frac{dE}{dw_1}=-2(1-\hat y)\,\sigma'(z_2)\,w_2\,\sigma'(z_1)\,x\approx-2\cdot0{,}3577\cdot0{,}2298\cdot0{,}6285\cdot0{,}2350\cdot1\approx-0{,}0243$$
Update: $w_1^{neu}=0{,}5-1\cdot(-0{,}0243)\approx0{,}5243$

**Schritt 4 – Update von $b_1$** (analog, jetzt mit $w_1=0{,}5243$ fest):
$$\frac{dE}{db_1}=-2(1-\hat y)\,\sigma'(z_2)\,w_2\,\sigma'(z_1)\approx-0{,}0241$$
Update: $b_1^{neu}=0-1\cdot(-0{,}0241)\approx0{,}0241$

**Ergebnis nach einer vollständigen Runde:** neues Netz $w_1\approx0{,}5243,\ b_1\approx0{,}0241,\ w_2\approx0{,}6285,\ b_2\approx0{,}1942$.

*Fehlervergleich (Kernaufgabe für die Schüler):* Beide Netze (Start- und neue Gewichte) mit demselben Input $x=1$ durchrechnen, jeweils den Fehler $(y-\hat y)^2$ berechnen und vergleichen:

- altes Netz: $E_{alt}\approx0{,}1788$
- neues Netz: $E_{neu}\approx0{,}1268$

Da $E_{neu}<E_{alt}$, ist das neue Netz besser trainiert. (Zwischenwerte gerundet; Rechnung mit GTR/Software empfohlen.)

**Didaktischer Zusatz:** Man kann den Fehler auch nach jedem einzelnen der vier Schritte (nicht erst am Ende) berechnen lassen und beobachten, dass er nach jedem Schritt kleiner wird. Das macht den "Abstieg" im Koordinatenabstieg sichtbar. Zusätzlich lässt sich diskutieren, warum echtes Gradient Descent (gleichzeitige Anpassung aller Gewichte über den Gradientenvektor) eigentlich die bessere/schnellere Variante wäre.



# Sonstiges:
- Saubere Definition von "Neuronales Netz" finden/festlegen.
- Will man den Bias im neuronalen Netz überhaupt gesondert behandeln, oder ihn nur als Teil der Gewichtsmatrix auffassen (erweiterter Input-Vektor mit zusätzlicher 1)?
- Nötig/sinnvoll/hilfreich ist ein allgemeiner Funktionsbegriff $\mathbb{R}^n\to\mathbb{R}^m$ als Grundlage.
- Beschränkt man sich auf Aufgaben, die die Schüler prinzipiell per Hand lösen könnten, oder akzeptiert man vermehrt Black-Boxen? (Wie z. B. schon aktuell bei der rechnerischen Bestimmung der Regressionsfunktion mit dem Taschenrechner.)
- Vieles sind letztlich Skalierungsprobleme (kleine, von Hand rechenbare Beispielnetze vs. reale Netze mit Millionen von Parametern).
- Diskutiert man Skalierungsfragen im Unterricht, und wenn ja, mit welchen Mitteln (Landau-Symbole o. Ä.)?
- Bewusst sein: Der entscheidende theoretische Fortschritt der letzten Jahre (neben Skalierungsfragen, Rechnerleistung, Big Data) ist die Transformer-Architektur ("Attention Is All You Need", 2017). Diese Thematik lässt sich in der Schulmathematik wohl nicht darstellen.
- Will man überhaupt mehrere Input-Vektoren zu einer Input-Matrix zusammenfassen (Batch-Verarbeitung), oder bleibt es bei einzelnen Input-Vektoren?
- Allgemein: Um welches Verständnis geht es überhaupt? Die Schüler lernen die Grundidee eines neuronalen Netzes kennen, aber keine grundsätzlich neuen mathematischen Konzepte – höchstens neue, zunächst kontextlose Begriffe wie tanh, Sigmoid etc.
- Bezug zu bereits vorhandenen Sek-II-Themen herstellen (Matrizen/LGS aus der analytischen Geometrie, Ableitungen aus der Analysis): Wie viel ist Wiederholung/Transfer, wie viel ist wirklich neuer Stoff?
