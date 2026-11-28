---
layout: module
title: "Mehrstufige Zufallsexperimente erklärt – Baumdiagramme und Pfadregeln"
description: "Mehrstufige Zufallsexperimente erklärt: Baumdiagramme aufstellen, vervollständigen und interpretieren – mit Beispielen und Pfadregeln."
page_context: Lernbereich
nav: dashboard
body_class: page-module
module_key: skript
published: true
lernbereich: mehrstufige-zufallsexperimente
gebiet: stochastik
permalink: /lernbereiche/stochastik/mehrstufige-zufallsexperimente/skript.html
---

# Mehrstufige Zufallsexperimente: Baumdiagramme und Pfadregeln

## Einführung

Wenn mehrere Zufallsexperimente nacheinander durchgeführt werden, sprechen wir von einem mehrstufigen Zufallsexperiment. Zur übersichtlichen Darstellung nutzen wir häufig Baumdiagramme. Für jede Stufe des Zufallsexperiments werden die Ergebnisse des einzelnen Zufallsexperiments als Knotenpunkte dargestellt. Die Stufen werden dann durch Pfade miteinander verbunden. Ein Ergebnis des mehrstufigen Zufallsexperiments entspricht dann einem vollständigen Pfad im Baumdiagramm. An den einzelnen Pfaden stehen die entsprechenden Wahrscheinlichkeiten. Es gibt zwei wichtige Regeln:

- **Pfadmultiplikationsregel:** Die Wahrscheinlichkeit eines Ergebnisses ist das Produkt der Wahrscheinlichkeiten entlang des entsprechenden Pfades.
- **Pfadadditionsregel:** Die Wahrscheinlichkeit eines Ereignisses ist die Summe der Wahrscheinlichkeiten der Ergebnisse, die zu diesem Ereignis führen.

Da generell die Summe aller Wahrscheinlichkeiten eines Zufallsexperiments immer gleich 1 ist, ist auch die Summe der Wahrscheinlichkeiten aller Pfade, die von einem Knotenpunkt starten, gleich 1. Ebenso ist auch die Summe der Endwahrscheinlichkeiten gleich 1.

### Beispiel: Zweimaliger Münzwurf

Kopf ($K$) und Zahl ($Z$) treten bei einem einmaligen Wurf beide mit einer Wahrscheinlichkeit von 50&nbsp;% auf. Daraus ergibt sich folgendes Baumdiagramm:

{% include baumdiagramm.html
    pa="0.5"
    pba="0.5"
    pbna="0.5"
    titel="Zweimaliger Münzwurf"
    label_a="K"
    label_abar="Z"
    label_b="K"
    label_bbar="Z"
%}

Nach der Pfadmultiplikationsregel haben wir jede Endwahrscheinlichkeit mit $0{,}5\cdot 0{,}5=0{,}25$ berechnet.

Betrachten wir z.B. das Ereignis $E$: "Es wird zweimal das Gleiche geworfen.", so ist $E=\\{KK, ZZ\\}$, und nach der Pfadadditionsregel folgt nun

$$
\begin{align*}
P(E)&=P(\{KK\})+P(\{ZZ\})\\
&=0{,}25+0{,}25\\
&=0{,}5.
\end{align*}
$$

## Baumdiagramme vervollständigen

Häufig stehen wir vor der Aufgabe, ein unvollständiges Baumdiagramm zu vervollständigen. Dazu verwenden wir, dass die Summe der Wahrscheinlichkeiten der Pfade, die von einem Knotenpunkt starten, gleich 1 ist. Außerdem wenden wir die Pfadregeln geschickt an.

### Direktes Anwenden der Pfadmultiplikationsregel

{% include check-anker.html nummer=1 %}

### Umformen der Pfadmultiplikationsregel

{% include check-anker.html nummer=2 %}

### Anwenden aller Pfadregeln

{% include check-anker.html nummer=3 %}


## Baumdiagramme interpretieren

Häufig liegt eine Situation vor, in der zwei Ereignisse $A$ und $B$ und deren Gegenereignisse auftreten. Bei der Interpretation eines Baumdiagramms müssen wir genau darauf achten, welche Wahrscheinlichkeiten gesucht sind. 

{% include check-anker.html nummer=4 %}

## Komplexe Baumdiagramme

An einer Schule wurden 1.200 Schülerinnen und Schüler gefragt, ob und wie sie Lern-Apps nutzen. Sie nutzen eine kostenlose Version (G), eine Bezahlversion (B) oder keine Lern-App (K). Wer eine App nutzt, wurde zusätzlich gefragt, ob er sie vor allem zur Unterhaltung (U) oder zur Prüfungsvorbereitung (V) nutzt. Die Auswertung liefert:

- 240 der 1.200 Befragten nutzen keine Lern-App.
- 70&nbsp;% der Nutzer der kostenlosen Version nutzen sie vor allem zur Prüfungsvorbereitung.
- 12&nbsp;% aller Befragten nutzen die Bezahlversion vor allem zur Unterhaltung.
- Insgesamt nutzen 27&nbsp;% aller Befragten eine Lern-App vor allem zur Unterhaltung.

Ein Baumdiagramm ist hier nicht vorgegeben, wir müssen es aus dem Text selbst aufstellen. Es hat auch nicht die Standardform mit zwei Ereignissen $A$ und $B$ und ihren Gegenereignissen. Die Pfadregeln gelten aber genauso.

### Die Struktur des Baums

Zuerst klären wir, wonach unterschieden wird. Auf der ersten Stufe steht die Art der Nutzung mit drei Ausgängen G, B und K. Auf der zweiten Stufe steht der Zweck mit U und V, allerdings nur nach G und B. Wer keine Lern-App nutzt, wurde nicht nach dem Zweck gefragt. Der Pfad K endet deshalb schon nach der ersten Stufe:

{% include baumdiagramm-allgemein.html baum="G(U V) B(U V) K" breite=420 %}

„Auch nach K müssen die Äste U und V folgen, damit der Baum vollständig ist.“ Stimmt das? Nein. Ein Baumdiagramm bildet nur ab, was im Sachverhalt tatsächlich passiert oder erfasst wird. Für K gibt es keine zweite Stufe.

Andere Sachverhalte führen zu anderen Formen. Nach verschiedenen Ästen kann es mit unterschiedlichen Ausgängen weitergehen, zum Beispiel bei Flugreisen mit „pünktlich“, „verspätet“ und „ausgefallen“, bei Bahnreisen nur mit „pünktlich“ und „verspätet“. Bei Abläufen endet ein Pfad, sobald der Vorgang abgeschlossen ist. Hat eine Fahrprüfung höchstens drei Versuche, tritt nach dem Bestehen (B) niemand mehr an, nur nach dem Nichtbestehen (N) geht es weiter:

{% include baumdiagramm-allgemein.html baum="B N(B N(B N))" breite=420 %}

Bei solchen Abläufen gibt die Zeit die Reihenfolge der Stufen vor. Bei Umfragen wie der zu den Lern-Apps wählen wir die Reihenfolge, in der der Text die Anteile angibt.

### Angaben einordnen

Der häufigste Fehler beim Aufstellen ist, eine Angabe an die falsche Stelle zu schreiben. Entscheidend ist, worauf sich ein Anteil bezieht:

- **Anteil einer Gruppe** steht am Ast, der aus dieser Gruppe herausführt. „70&nbsp;% der Nutzer der kostenlosen Version …“ bezieht sich nur auf G und gehört an den Ast von G nach V.
- **Anteil aller mit zwei Merkmalen** ist ein Pfadende. „12&nbsp;% aller Befragten nutzen die Bezahlversion vor allem zur Unterhaltung“ ist das Pfadende von B → U.
- **Gesamtanteil über mehrere Gruppen** ist eine Summe von Pfadenden. „Insgesamt 27&nbsp;% … zur Unterhaltung“ steht an keiner einzelnen Stelle, sondern ist die Summe der Pfadenden von G → U und B → U.
- **Absolute Häufigkeiten** teilen wir durch die Gesamtzahl: $\frac{240}{1200}=0{,}2$. Der Wert steht am Ast zu K und ist zugleich das Pfadende, weil der Pfad dort endet.

{% include baumdiagramm-allgemein.html baum="G(U V[0,7]) B(U[|0,12] V) K[0,2|0,2]" breite=480 %}

„‚12&nbsp;% aller Befragten nutzen die Bezahlversion vor allem zur Unterhaltung‘ gehört an den Ast von B nach U.“ Stimmt das? Nein. Die 12&nbsp;% beziehen sich auf alle Befragten, nicht nur auf die Nutzer der Bezahlversion. Am Ast von B nach U steht ein anderer Wert, nämlich der Anteil innerhalb der Gruppe B.

### Fehlende Werte bestimmen

Sind alle Angaben eingetragen, vervollständigen wir den Baum mit den bekannten Regeln. Bei komplexen Bäumen müssen wir dabei fast immer auch rückwärts rechnen:

- Ist ein Pfadende bekannt und ein Ast auf diesem Pfad, erhalten wir den fehlenden Ast durch Division.
- Ist eine Summe von Pfadenden bekannt, erhalten wir ein fehlendes Pfadende durch Subtraktion.
- An jedem Knoten summieren sich die Äste zu 1.

Zur Kontrolle müssen sich am Ende alle Pfadenden zu 1 summieren. Das folgende Beispiel zeigt den vollständigen Weg vom Text bis zum ausgefüllten Baum.

{% include check-anker.html nummer=5 %}

<!--### Urnenmodelle
Ein wichtiges Beipsiel für mehrstufige Zufallsexperimente sind das Ziehen von Kugeln aus einer Urne. Hier müssen wir unterscheiden, ob Kugeln zurückgegelgt werden oder nicht.

#### Beispiel: Ziehen mit Zurücklegen
In einer Urne

und dann ein alltägliches zufallsexpeirment, das als urnenmodell interpretiert werden kann

-->

