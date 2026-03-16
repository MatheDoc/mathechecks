---
layout: dev-module
title: Differentialrechnung ganzrationaler Funktionen - Skript (Dev)
description: Dev-Lernbereich Differentialrechnung ganzrationaler Funktionen, Modul Skript.
page_context: Lernbereich
nav: dashboard
body_class: page-module-designs
module_key: skript
published: true
lernbereich: differentialrechnung-ganzrationaler-funktionen
gebiet: analysis
permalink: /dev/lernbereiche/analysis/differentialrechnung-ganzrationaler-funktionen/skript.html
---

## Einführung

Ganzrationale Funktionen (Polynomfunktionen) haben die Form

$$
f(x) = a_n x^n + a_{n-1} x^{n-1} + \dots + a_1 x + a_0,\quad a_i\in\mathbb{R}.
$$

Der Grad ist die höchste auftretende Potenz $n$ mit $a_n\neq 0$. Beispiele:

- linear: $f(x)=2x-3$
- quadratisch: $f(x)=x^2-4x+5$
- kubisch: $f(x)=x^3-3x$

Die Differentialrechnung untersucht Steigungen, Extremstellen und Krümmungen mithilfe von Ableitungen.

{% include info.html
index="1"
frage="Begriffe: Polynom, Grad"
antwort="
- Polynom: Summe von Potenzen von x mit reellen Koeffizienten.
- Grad: größte Potenz mit von 0 verschiedenem Koeffizienten.
"
%}


## Ableitungsregeln für Polynome

Für Polynome genügen zwei Grundregeln:

- Lineare Regel (Linearität): $(c\cdot g(x))' = c\cdot g'(x)$ und $(g(x)+h(x))' = g'(x)+h'(x)$
- Potenzregel: $\dfrac{d}{dx}\, x^n = n\,x^{n-1}$ für $n\in\mathbb{N}$

Damit lässt sich jede Ableitung eines Polynoms berechnen. Beispiel:

$$
f(x)=3x^4-2x^2+7x-5 \Rightarrow f'(x)=12x^3-4x+7.
$$

{% include info.html
index="2"
frage="Potenzregel und Linearität"
antwort="
Potenzregel: $\frac{d}{dx}x^n = n\,x^{n-1}$; Linearität: Ableitung verteilt sich über Summe und Faktoren.
"
%}


## Bedeutung der Ableitung

Die Ableitung $f'(x)$ gibt die Steigung der Tangente an den Graphen von $f$ im Punkt $x$ an.

- $f'(x)>0$: $f$ steigt lokal
- $f'(x)<0$: $f$ fällt lokal
- $f'(x)=0$: Kandidat für Extremstelle (genauer: Vorzeichenwechsel prüfen)

### Beispiel mit Graph

Wir betrachten $f(x)=x^3-3x$ und seine Ableitung $f'(x)=3x^2-3$. Beide Funktionen sind unten überlagert dargestellt.

{% include graph.html
funktionen='[{"term":"x^3-3x","name":"f(x)"},{"term":"3x^2-3","name":"f\'(x)"}]'
titel="f und f'"
xachse="x"
yachse="y"
xmin="-4"
xmax="4"
ymin="-10"
ymax="10"
%}


## Höhere Ableitungen, Krümmung und Wendepunkte

Die zweite Ableitung $f''(x)$ beschreibt die Krümmung:

- $f''(x)>0$: Graph ist „linksgekrümmt“ (konvex), Steigung nimmt zu
- $f''(x)<0$: Graph ist „rechtsgekrümmt“ (konkav), Steigung nimmt ab
- Wendepunkt: $f''(x)=0$ und Krümmungswechsel (Vorzeichenwechsel von $f''$)

Beispiel: Für $f(x)=x^3-3x$ ist $f''(x)=6x$. Bei $x=0$ gilt $f''(0)=0$ und $f''$ wechselt das Vorzeichen → Wendepunkt.

{% include info.html
index="4"
frage="Zusammenhang f, f' und f''"
antwort="
- Monotonie über Vorzeichen von $f'$
- Extremstellen: $f'(x)=0$ und Vorzeichenwechsel von $f'$
- Krümmung über Vorzeichen von $f''$, Wendepunkt bei Vorzeichenwechsel
"
%}


## Kurvendiskussion bei Polynomen (Schema)

1. Definitionsbereich (bei Polynomen: ganz $\mathbb{R}$)
2. Symmetrie prüfen (gerade/ungerade Funktion)
3. Nullstellen: $f(x)=0$
4. Verhalten im Unendlichen: Leitkoeffizient und Grad
5. Erste Ableitung: $f'(x)$, Monotonie und Extremstellen (Vorzeichenwechsel von $f'$)
6. Zweite Ableitung: $f''(x)$, Krümmung und Wendepunkte (Vorzeichenwechsel von $f''$)
7. Skizze/Plot und Zusammenfassung


## Beispiel einer vollständigen Kurvendiskussion

Gegeben sei $f(x)=x^4-2x^2$.

- $f'(x)=4x^3-4x=4x(x^2-1)$ → Kandidaten: $x\in\{-1,0,1\}$; Vorzeichenwechsel analysieren
- $f''(x)=12x^2-4$ → Krümmung und Wendepunkte: $f''(x)=0 \Rightarrow x=\pm \tfrac{2}{\sqrt{12}}=\pm \tfrac{1}{\sqrt{3}}$
- Nullstellen: $f(x)=x^2(x^2-2)$ → $x=0$ (doppelte NS) und $x=\pm\sqrt{2}$

{% include graph.html
funktionen='[{"term":"x^4-2x^2","name":"f(x)"},{"term":"4x^3-4x","name":"f\'(x)"}]'
titel="Kurvendiskussion: f und f'"
xachse="x"
yachse="y"
xmin="-3"
xmax="3"
ymin="-5"
ymax="10"
%}


## Ausblick

Für ganzrationale Funktionen genügen die Regeln der Polynomableitung. Für allgemeinere Funktionen (Produkte, Quotienten, Verkettungen) werden Produkt-, Quotienten- und Kettenregel benötigt.


