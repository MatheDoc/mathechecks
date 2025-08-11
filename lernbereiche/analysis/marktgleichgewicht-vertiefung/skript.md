---
layout: skript
title: Marktgleichgewicht - Vertiefung
description: Marktgleichgewicht - Vertiefung - Skript
lernbereich: marktgleichgewicht-vertiefung
gebiet: analysis
---

## Wiederholung

Die **Nachfragefunktion** $p_N(x)$ gibt an, wie hoch der Preis in Geldeinheiten (GE) pro nachgefragter Mengeneinheit (ME) ist. Da es keine negativen Preise geben kann, gilt stets $p_N(x)\geq0$. Weil die nachgefragte Menge in der Regel nur dann steigt, wenn der Preis sinkt, ist die Nachfragefunktion monoton fallend.

Die **Angebotsfunktion** $p_A(x)$ gibt an, wie hoch der Preis in Geldeinheiten (GE) pro angebotener Mengeneinheit (ME) ist. Auch hier gilt $p_A(x)\geq0$, da negative Preise nicht sinnvoll sind. Da Produzenten nur dann bereit sind, mehr anzubieten, wenn der Preis steigt, ist die Angebotsfunktion monoton steigend.

Wir verwenden folgende Kennzahlen zur Beschreibung von Nachfrage und Angebot:

- **Gleichgewichtsmenge:** Menge, bei der nachgefragter und angebotener Preis gleich sind.
- **Gleichgewichtspreis:** Preis, bei der nachgefragte und angebotene Menge gleich sind.
- **Höchstpreis:** Maximaler Preis, den ein Konsument zu zahlen bereit ist.
- **Sättigungsmenge:** Absatzmenge, bei der trotz Preis null keine Nachfrage mehr besteht.
- **Mindestangebotspreis:** Preis, ab dem Produzenten bereits, das Produkt anzubieten.
- **Umsatz im Marktgleichgewicht:** Gesamtumsatz, wenn auf dem Markt die Gleichgewichtsmenge zum Gleichgewichtspreis gehandelt wird.

### Graphische Bestimmungen

{% include info.html
index="1"
frage="Graphische Bestimmung der Kennzahlen zum Marktgleichgewicht"
antwort="Graphische Interpretation mathematischer Fachbegriffe (y-Achsenabschnitt, Nullstellen, Schnittpunkte)"
%}

<div id="skript-aufgabe-1"></div>

### Berechnungen

{% include info.html
index="2"
frage="Berechnung der Kennzahlen zum Marktgleichgewicht. Den Beispielen liegen folgende Funktionen zugrunde:

$$
\begin{align*}
p_N(x)&=45{,}75\\cdot e^{-0{,}044x}-6{,}75\\
p_A(x)&=0{,}016x^2+0{,}022x+6\\
\end{align*}
$$

"

antwort="

### Höchstpreis

Der y-Achsenabschnitt von $p_N(x)$:

$$
45{,}75\\cdot e^{-0{,}044\cdot 0}-6{,}75 = 39
$$

Der Höchstpreis beträgt 39 GE.

### Sättigungsmenge

Nullstelle von $p_N(x)$:

$$
\begin{align*}
45{,}75\\cdot e^{-0{,}044x}-6{,}75 &= 0 \quad|\text{ TR}\\
x &= 43{,}4921
\end{align*}
$$

Die Sättigungsmenge beträgt 43,49 ME.

### Mindestangebotspreis

Der y-Achsenabschnitt von $p_A(x)$:

$$
0{,}016\cdot 0^2+0{,}022\cdot 0+6 = 6
$$

Der Mindestangebotspreis beträgt 6 GE.

### Gleichgewichtsmenge

Schnittstelle von $p_N$ und $p_A$:

$$
\begin{align*}
45{,}75\\cdot e^{-0{,}044x}-6{,}75 &= 0{,}016x^2+0{,}022x+6 \quad|\text{ TR}\\
x &= 19{,}5903
\end{align*}
$$

Die Gleichgewichtsmenge beträgt 19,59 ME.

### Gleichgewichtspreis

y-Wert des Schnittpunkts von $p_N$ und $p_A$:

$$
p_N(19{,}5903)=12{,}5715
$$

(Oder gleichwertig:

$$
p_A(19{,}5903)=12{,}5715
$$

)

Der Gleichgewichtspreis beträgt 12,57 GE.

### Umsatz im Marktgleichgewicht

Produkt der Gleichgewichtsmenge und des Gleichgewichtspreis:

$$
19{,}5903\cdot 12{,}5715 = 246{,}2795
$$

Der Umsatz im Marktgleichgewicht beträgt 246,28 GE.

"
%}

<div id="skript-aufgabe-2"></div>

## Konsumenten- und Produzentenrente

## Abschöpfung der Konsumentenrente

{
"einleitung":"Gegeben sind die Angebotsfunktion <br/></p>\\( p_A(x)=0,016x^2+0,022x+6 \\)<br/></p> und die Nachfragefunktion <br/></p>\\( p_N(x)=45,75\\cdot e^{-0,044x}-6,75 \\).</p> <p>Bestimmen Sie (auf 2 NKS gerundet)",
"fragen":[
"den Mindestangebotspreis.",
"den Höchstpreis.",
"die Sättigungsmenge.",
"die Gleichgewichtsmenge.",
"den Gleichgewichtspreis."
],
"antworten":[
"{1:NUMERICAL:=6:0,1}",
"{1:NUMERICAL:=39:0,1}",
"{1:NUMERICAL:=43,4921:0,1}",
"{1:NUMERICAL:=19,5904:0,1}",
"{1:NUMERICAL:=12,5715:0,1}"
]
}
