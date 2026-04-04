---
layout: dev-module
title: Marktgleichgewicht - Grundlagen - Skript (Dev)
description: Dev-Lernbereich Marktgleichgewicht - Grundlagen, Modul Skript.
page_context: Lernbereich
nav: dashboard
body_class: page-module-designs
module_key: skript
published: true
lernbereich: marktgleichgewicht-grundlagen
gebiet: analysis
permalink: /dev/lernbereiche/analysis/marktgleichgewicht-grundlagen/skript.html
---

## Einführung

Auf einem Markt treffen Anbieter und Nachfrager zusammen. Ihr Verhalten lässt sich mithilfe mathematischer Funktionen modellieren. In Abhängigkeit von der Menge $x$ betrachten wir folgende Preisfunktionen:

### Die Nachfragefunktion

Die Nachfragefunktion $p_N(x)$ gibt an, wie hoch der Preis in Geldeinheiten (GE) pro nachgefragter Mengeneinheit (ME) ist. Da es keine negativen Preise geben kann, gilt stets $p_N(x)\geq0$. Weil die nachgefragte Menge in der Regel nur dann steigt, wenn der Preis sinkt, ist die Nachfragefunktion monoton fallend.

### Die Angebotsfunktion

Die Angebotsfunktion $p_A(x)$ gibt an, wie hoch der Preis in Geldeinheiten (GE) pro angebotener Mengeneinheit (ME) ist. Auch hier gilt $p_A(x)\geq0$, da negative Preise nicht sinnvoll sind. Da Produzenten nur dann bereit sind, mehr anzubieten, wenn der Preis steigt, ist die Angebotsfunktion monoton steigend.

## Kennzahlen

Das Zusammenspiel von Nachfrage- und Angebotsfunktion wird mit Hilfe folgender Kennzahlen beschrieben und analysiert.

|Kennzahl| Symbol | Beschreibung| Definition|
|---|---|---|---|
|Gleichgewichtsmenge| $x_G$| Menge, bei der nachgefragter und angebotener Preis gleich sind| Schnittstelle von $p_N$ und $p_A$|
|Gleichgewichtspreis| $p_G$| Preis, bei der nachgefragte und angebotene Menge gleich sind| y-Wert des Schnittpunkts von $p_N$ und $p_A$|
|Höchstpreis| $p_H$| Maximaler Preis, den ein Konsument zu zahlen bereit ist| y-Achsenabschnitt von $p_N$|
|Sättigungsmenge| $x_S$| Absatzmenge, bei der trotz Preis null keine Nachfrage mehr besteht| Nullstelle von $p_N$|
|Mindestangebotspreis| $p_M$| Preis, ab dem Produzenten bereits, das Produkt anzubieten| y-Achsenabschnitt von $p_A$|
|Umsatz im Marktgleichgewicht| $U_G$| Gesamtumsatz, wenn auf dem Markt die Gleichgewichtsmenge zum Gleichgewichtspreis gehandelt wird| Produkt aus $x_G$ und $p_G$|



## Graphische Darstellungen

{% include dev/check-anker.html nummer="1" %}


## Berechnungen

{% include dev/check-anker.html nummer="2" %}


## Marktsituationen

Liegt ein vollkommener Markt mit Polypol auf der Anbieter- und Nachfragerseite vor, so stellt sich ein Marktgleichgewicht ein. Externe Einflüsse können jedoch zu einem Marktungleichgewicht führen.

### Marktgleichgewicht

Der im vorherigen Abschnitt behandelte Fall: Im Marktgleichgewicht stimmen angebotene und nachgefragte Menge überein. Der Preis und die Menge werden durch das Zusammenspiel von Angebot und Nachfrage bestimmt.

### Marktungleichgewicht: Nachfrageüberschuss

Ein äußerer Eingriff, hier die Festlegung eines **Höchstpreises**, kann ein Ungleichgewicht verursachen. Das folgende Diagramm zeigt die Situation bei einem Höchstpreis $p_H$ von 20 GE.

{% include dev/graph.html
   funktionen='[
    {"name":"p<sub>N</sub>(x)", "term":"-2*x+42", "beschreibung":"Nachfragefunktion"},
    {"name":"p<sub>A</sub>(x)", "term":"1.5x+14", "beschreibung":"Angebotsfunktion"},
    {"name":"p<sub>H</sub>", "term":"20", "beschreibung":"Höchstpreis"}
   ]'
    punkte='[
     {"x":4,"y":20,"text":"Angebotene Menge bei Höchstpreis"},
     {"x":11,"y":20,"text":"Nachgefragte Menge bei Höchstpreis"}
   ]'
   titel="Nachfrageüberhang"
   xachse="Menge x in ME"
   yachse="Betrag y in GE"
   xmin=-0.2
   xmax=22
   ymin=-1
   ymax=50
%}

Am Diagramm können wir erkennen, dass bei einem Höchstpreis von 20 GE die angebotene Menge bei 4 ME liegt und die nachgefragte Menge bei 11 ME. Es entsteht somit ein Nachfrageüberschuss von $11 - 4 = 7$ ME.

Dieser Überschuss ist leicht nachvollziehbar: Der künstlich gesenkte Preis führt dazu, dass weniger Produzenten bereit sind, das Produkt anzubieten, während mehr Konsumenten bereit sind, es zu kaufen.

Die entsprechende Rechnung sieht wie folgt aus. Im Diagramm abgebildet sind die Nachfragefunktion $p_N(x) = -2x + 42$ und die Angebotsfunktion $p_A(x) = 1{,}5x + 14$. Wir berechnen nun die nachgefragte Menge:

$$
\begin{align*}
-2x + 42 &= 20 \quad | -42\\
-2x &= -22 \quad | :(-2)\\
x &= 11
\end{align*}
$$

und die angebotene Menge:

$$
\begin{align*}
1{,}5x + 14 &= 20 \quad | -14\\
1{,}5x &= 6 \quad | :1{,}5\\
x &= 4.
\end{align*}
$$

Bei einem Preis von 20 GE werden also 11 ME nachgefragt und 4 ME angeboten. Es ergibt sich ein Nachfrageüberschuss von 7 ME.

Da auf dem Markt zu einem Preis von 20 GE nur 4 ME angeboten werden, beträgt der realisierte Umsatz

$$
4 \cdot 20 = 80 \text{ GE}.
$$

### Marktungleichgewicht: Angebotsüberschuss

Ein äußerer Eingriff, hier die Festlegung eines **Mindestpreises**, kann ein Ungleichgewicht verursachen. Das folgende Diagramm zeigt die Situation bei einem Mindestpreis $p_M$ von 35 GE.

{% include dev/graph.html
   funktionen='[
    {"name":"p<sub>N</sub>(x)", "term":"-2*x+42", "beschreibung":"Nachfragefunktion"},
    {"name":"p<sub>A</sub>(x)", "term":"1.5x+14", "beschreibung":"Angebotsfunktion"},
    {"name":"p<sub>M</sub>", "term":"35", "beschreibung":"Mindestpreis"}
   ]'
    punkte='[
     {"x":14,"y":35,"text":"Angebotene Menge bei Mindestpreis"},
     {"x":3.5,"y":35,"text":"Nachgefragte Menge bei Mindestpreis"}
   ]'
   titel="Nachfrageüberhang"
   xachse="Menge x in ME"
   yachse="Betrag y in GE"
   xmin=-0.2
   xmax=22
   ymin=-1
   ymax=50
%}

Am Diagramm können wir erkennen, dass bei einem Mindestpreis von 35 GE die angebotene Menge bei 14 ME liegt und die nachgefragte Menge bei 3,5 ME. Es entsteht somit ein Angebotsüberschuss von $14 - 3{,}5 = 10{,}5$ ME.

Dieser Überschuss ist leicht nachvollziehbar: Der künstlich erhöte Preis führt dazu, dass mehr Produzenten bereit sind, das Produkt anzubieten, während weniger Konsumenten bereit sind, es zu kaufen.

Die entsprechende Rechnung sieht wie folgt aus. Im Diagramm abgebildet sind die Nachfragefunktion $p_N(x) = -2x + 42$ und die Angebotsfunktion $p_A(x) = 1{,}5x + 14$. Wir berechnen nun die nachgefragte Menge:

$$
\begin{align*}
-2x + 42 &= 35 \quad | -42\\
-2x &= -7 \quad | :(-2)\\
x &= 3{,}5
\end{align*}
$$

und die angebotene Menge:

$$
\begin{align*}
1{,}5x + 14 &= 35 \quad | -14\\
1{,}5x &= 21 \quad | :1{,}5\\
x &= 14.
\end{align*}
$$

Bei einem Preis von 35 GE werden also 3,5 ME nachgefragt und 14 ME angeboten. Es ergibt sich ein Angebotsüberschuss von 10,5 ME.

Da auf dem Markt zu einem Preis von 35 GE nur 3,5 ME nachgefragt werden, beträgt der realisierte Umsatz

$$
3{,}5 \cdot 35 = 122{,}5 \text{ GE}.
$$

{% include dev/check-anker.html nummer="3" %}

