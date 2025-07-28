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
frage="Mathematische Definition der Kennzahlen zum Marktgleichgewicht"
antwort="Beschreibung der Kennzahlen mit Hilfe mathematischer Fachbegriffe (y-Achsenabschnitt, Nullstelle, Schnittpunkt)"
%}

<div id="skript-aufgabe-1"></div>

## Graphische Darstellungen

Das folgende Diagramm veranschaulicht die Kennzahlen zum Marktgleichgewicht.

{% include graph.html
   funktionen='[
    {"name":"p<sub>N</sub>(x)", "term":"-2*x+42", "beschreibung":"Nachfragefunktion"},
    {"name":"p<sub>A</sub>(x)", "term":"1.5x+14", "beschreibung":"Angebotsfunktion"}
   ]'
    punkte='[
     {"x":0,"y":42,"text":"Höchstpreis"},
     {"x":0,"y":14,"text":"Mindesangebotspreis"},
     {"x":8,"y":26,"text":"Marktgleichgewicht: Gleichgewichtsmenge und Gleichgewichtspreis"},
     {"x":21,"y":0,"text":"Sättigungsmenge"}
   ]'
   titel="Marktgleichgewicht"
   xachse="Menge x in ME"
   yachse="Betrag y in GE"
   xmin=-0.2
   xmax=22
   ymin=-1
   ymax=50
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
frage="Berechnung der Kennzahlen zum Marktgleichgewicht. Den Beispielen liegen folgende Funktionen zugrunde:

$$
\begin{align*}
p_N(x)&=-2x+42\\
p_A(x)&=1{,}5x+14\\
\end{align*}
$$

"

antwort="

### Höchstpreis

Der y-Achsenabschnitt von $p_N(x) = -2x + 42$:

$$
p_N(0) = 42
$$

Der Höchstpreis beträgt 42 GE.

### Sättigungsmenge

Nullstelle von $p_N(x)$:

$$
\begin{align*}
-2x + 42 &= 0 \quad|-42\\
-2x  &= -42 \quad|:(-2)\\
x &= 21
\end{align*}
$$

Die Sättigungsmenge beträgt 21 ME.

### Mindestangebotspreis

Der y-Achsenabschnitt von $p_A(x) = 1{,}5x + 14$:

$$
p_A(0) = 14
$$

Der Mindestangebotspreis beträgt 14 GE.

### Gleichgewichtsmenge

Schnittstelle von $p_N$ und $p_A$:

$$
\begin{align*}
-2x + 42 &= 1{,}5x+14 \quad|+2x-14\\
28  &= 3{,}5x \quad|:(-3{,}5)\\
x &= 8
\end{align*}
$$

Die Gleichgewichtsmenge beträgt 8 ME.

### Gleichgewichtspreis

y-Wert des Schnittpunkts von $p_N$ und $p_A$:

$$
p_N(8)=-2\cdot 8 +42=26
$$

(Oder gleichwertig:

$$
p_A(8)=1{,}5\cdot 8 + 14=26
$$

)

Der Gleichgewichtspreis beträgt 26 GE.

### Umsatz im Marktgleichgewicht

Produkt der Gleichgewichtsmenge und des Gleichgewichtspreis:

$$
8\cdot 26 = 208
$$

Der Umsatz im Marktgleichgewicht beträgt 208 GE.

"
%}

<div id="skript-aufgabe-3"></div>

## Marktsituationen

Liegt ein vollkommener Markt mit Polypol auf der Anbieter- und Nachfragerseite vor, so stellt sich ein Marktgleichgewicht ein. Externe Einflüsse können jedoch zu einem Marktungleichgewicht führen.

### Marktgleichgewicht

Der im vorherigen Abschnitt behandelte Fall: Im Marktgleichgewicht stimmen angebotene und nachgefragte Menge überein. Der Preis und die Menge werden durch das Zusammenspiel von Angebot und Nachfrage bestimmt.

### Marktungleichgewicht: Nachfrageüberschuss

Ein äußerer Eingriff, hier die Festlegung eines **Höchstpreises**, kann ein Ungleichgewicht verursachen. Das folgende Diagramm zeigt die Situation bei einem Höchstpreis $p_H$ von 20 GE.

{% include graph.html
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

{% include graph.html
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

{% include info.html
index="4"
frage="Bestimmung des Nachfrage- und Angebotsüberschusses bei festgelegtem Preis"
antwort="

- Bestimmung der nachgefragten Menge
- Bestimmung der angebotenen Menge
- Je nachdem welche Menge größer ist: Nachfrage- und Angebotsüberschusses
"
%}

<div id="skript-aufgabe-4"></div>
