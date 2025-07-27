---
layout: skript
title: Marktgleichgewicht - Grundlagen
description: Marktgleichgewicht - Grundlagen - Skript
lernbereich: marktgleichgewicht-grundlagen
gebiet: analysis
---

## Einführung

Auf einem Markt treffen Anbieter und Nachfrager zusammen. Ihr Verhalten lässt sich mithilfe mathematischer Funktionen modellieren. In Abhängigkeit von der Menge $x$ betrachten wir folgende Preisfunktionen:

### Die Nachfragefunktion

Die Nachfragefunktion $p_N(x)$ gibt an, wie hoch der Preis in Geldeinheiten (GE) pro nachgefragter Mengeneinheit (ME) ist. Da es keine negativen Preise geben kann, gilt stets $p_N(x)\geq0$. Weil die nachgefragte Menge in der Regel nur dann steigt, wenn der Preis sinkt, ist die Nachfragefunktion monoton fallend.

### Die Angebotsfunktion

Die Angebotsfunktion $p_A(x)$ gibt an, wie hoch der Preis in Geldeinheiten (GE) pro angebotener Mengeneinheit (ME) ist. Auch hier gilt $p_A(x)\geq0$, da negative Preise nicht sinnvoll sind. Da Produzenten nur dann bereit sind, mehr anzubieten, wenn der Preis steigt, ist die Angebotsfunktion monoton steigend.

## Kennzahlen

- **Gleichgewichtsmenge:** Menge, bei der nachgefragter und angebotener Preis gleich sind.
- **Gleichgewichtspreis:** Preis, bei der nachgefragte und angebotene Menge gleich sind.
- **Höchstpreis:** Maximaler Preis, den ein Konsument zu zahlen bereit ist.
- **Sättigungsmenge:** Absatzmenge, bei der trotz Preis null keine Nachfrage mehr besteht.
- **Mindestangebotspreis:** Preis, ab dem Produzenten bereits, das Produkt anzubieten.
- **Umsatz im Marktgleichgewicht:** Gesamtumsatz, wenn auf dem Markt die Gleichgewichtsmenge zum Gleichgewichtspreis gehandelt wird.

{% include info.html
index="1"
frage="Mathematische Definition Kennzahlen zum Marktgleichgewicht"
antwort="Beschreibung der Kennzahlen mit Hilfe mathematischer Fachbegriffe (y-Achsenabschnitt, Nullstelle, Schnittpunkt)"
%}

<div id="skript-aufgabe-1"></div>

## Graphische Darstellungen

Die beiden folgenden Diagramme veranschaulicht die Kennzahlen zum Marktgleichgewicht.

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

{% include info.html
index="2"
frage="Graphische Bestimmung der Kennzahlen zum Marktgleichgewicht"
antwort="Graphische Interpretation mathematischer Fachbegriffe (y-Achsenabschnitt, Nullstellen, Schnittpunkte)"
%}

<div id="skript-aufgabe-2"></div>

## Berechnungen

{% include info.html
index="3"
frage="Berechnung der Kennzahlen zum Marktgleichgewicht."
antwort="

- y-Abschnitt: $f(0)$
- Nullstellen: $f(x)=0$
- Extremstellen: Notwendige Bedingung $f'(x) = 0$, hinreichende Bedingung $f'\'(x) > 0$ (Minimum) oder $f'\'(x) < 0$ (Maximum)
- Wendestellen: Notwendige Bedingung $f'\'(x) = 0$, hinreichende Bedingung $f''\'(x) > 0$ (minimale Steigung) oder $f''\'(x)<0$ (maximale Steigung)
  "
  %}

<div id="skript-aufgabe-3"></div>

## Weitere Marktsituationen
