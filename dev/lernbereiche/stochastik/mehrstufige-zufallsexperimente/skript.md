---
layout: dev-module
title: Mehrstufige Zufallsexperimente - Skript (Dev)
description: Dev-Lernbereich Mehrstufige Zufallsexperimente, Modul Skript.
page_context: Lernbereich
nav: dashboard
body_class: page-module-designs
module_key: skript
published: true
lernbereich: mehrstufige-zufallsexperimente
gebiet: stochastik
permalink: /dev/lernbereiche/stochastik/mehrstufige-zufallsexperimente/skript.html
---

## Einführung

Wenn mehrere Zufallsexperimente nacheinander durchgeführt werden, sprechen wir von einem mehrstufigen Zufallsexperiment. Zur übersichtlichen Darstellung nutzen wir häufig Baumdiagramme. Für jede Stufe des Zufallsexperiments werden die Ergebnisse des einzelnen Zufallsexperiments als Knotenpunkte dargestellt. Die Stufen werden dann durch Pfade miteinander verbunden. Ein Ergebnis des mehrstufigen Zufallsexperiments entspricht dann einem vollständigen Pfad im Baumdiagramm. An den einzelnen Pfaden stehen die entsprechenden Wahrscheinlichkeiten. Es gibt zwei wichtige Regeln:

- **Pfadmultiplikationsregel:** Die Wahrscheinlichkeit eines Ergebnisses ist das Produkt der Wahrscheinlichkeiten entlang des entsprechenden Pfades.
- **Pfadadditionsregel:** Die Wahrscheinlichkeit eines Ereignisses ist die Summe der Wahrscheinlichkeiten der Ergebnisse, die zu diesem Ereignis führen.

Da generell die Summe aller Wahrscheinlichkeiten eines Zufallsexperiments immer gleich 1 ist, ist auch die Summe der Wahrscheinlichkeiten aller Pfade, die von einem Knotenpunkt starten, gleich 1. Ebenso ist auch die Summe der Endwahrscheinlichkeiten gleich 1.

### Beispiel: Zweimaliger Münzwurf

Kopf ($K$) und Zahl ($Z$) treten bei einem einmaligen Wurf beide mit einer Wahrscheinlichkeit von 50&nbsp;% auf. Daraus ergibt sich folgendes Baumdiagramm:

{% include dev/baumdiagramm.html
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

{% include dev/check-anker.html nummer=1 %}

### Umformen der Pfadmultiplikationsregel

{% include dev/check-anker.html nummer=2 %}

### Anwenden der aller Pfadregeln

{% include dev/check-anker.html nummer=3 %}


## Baumdiagramme interpretieren

Häufig liegt eine Situation vor, in der zwei Ereignisse $A$ und $B$ und deren Gegenereignisse auftreten. Bei der Interpretation eines Baumdiagramms müssen wir genau darauf achten, welche Wahrscheinlichkeiten gesucht sind. 

{% include dev/check-anker.html nummer=4 %}

## Weitere Baumdigramme

Baumdiagramme eignen sich auch dazu, komplexere Zufallsexperimente zu veranschaulichen. Wichtig ist, den Text gründlich zu lesen, um die Struktur des Zufallsexperiments zu verstehen. Dann können wir das Baumdiagramm zeichnen, die im Text gegebenen Wahrscheinlichkeiten notieren und schließlich die Pfadregeln anwenden.

{% include dev/check-anker.html nummer=5 %}

{% include dev/check-anker.html nummer=6 %}

<!--### Urnenmodelle
Ein wichtiges Beipsiel für mehrstufige Zufallsexperimente sind das Ziehen von Kugeln aus einer Urne. Hier müssen wir unterscheiden, ob Kugeln zurückgegelgt werden oder nicht.

#### Beispiel: Ziehen mit Zurücklegen
In einer Urne

und dann ein alltägliches zufallsexpeirment, das als urnenmodell interpretiert werden kann

-->
