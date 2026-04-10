---
layout: dev-module
title: Mehrstufige Produktionsprozesse - Skript (Dev)
description: Dev-Lernbereich Mehrstufige Produktionsprozesse, Modul Skript.
page_context: Lernbereich
nav: dashboard
body_class: page-module-designs
module_key: skript
published: true
lernbereich: mehrstufige-produktionsprozesse
gebiet: lineare-algebra
permalink: /dev/lernbereiche/lineare-algebra/mehrstufige-produktionsprozesse/skript.html
---

## Einführung

Ein Smartphone besteht aus vielen Einzelteilen. Rohstoffe wie Silizium, Lithium und Glas werden zunächst zu Bauteilen (Display, Akku, Chip) verarbeitet. In einem zweiten Schritt werden diese Bauteile zu den fertigen Smartphone-Modellen zusammengesetzt. Solche Produktionsprozesse mit mehreren Stufen heißen **mehrstufige Produktionsprozesse**.



## Darstellung mehrstufiger Produktionsprozesse

### Grundstruktur

Bei einem zweistufigen Produktionsprozess gibt es drei Arten von Gütern:

- **Rohstoffe** (R1, R2, …): Ausgangsmaterialien
- **Zwischenprodukte** (Z1, Z2, …): In der 1. Stufe aus Rohstoffen hergestellte Güter
- **Endprodukte** (E1, E2, …): In der 2. Stufe aus Zwischenprodukten hergestellte Güter

### Beispiel: Smartphone-Fertigung

Eine Firma stellt aus den Rohstoffen Silizium (R1), Lithium (R2) und Glas (R3) die Bauteile Chip (Z1), Akku (Z2) und Display (Z3) her. Aus diesen Bauteilen werden die Smartphone-Modelle Alpha (E1) und Beta (E2) zusammengesetzt.

**1. Produktionsstufe:** Für einen Chip werden 5 ME Silizium und 1 ME Glas benötigt. Für einen Akku werden 2 ME Silizium und 4 ME Lithium benötigt. Für ein Display werden 1 ME Silizium und 6 ME Glas benötigt.

**2. Produktionsstufe:** Für ein Alpha werden 2 Chips, 1 Akku und 1 Display verbaut. Für ein Beta werden 3 Chips, 2 Akkus und 2 Displays verbaut.

### Verflechtungsdiagramm

Die Struktur eines mehrstufigen Produktionsprozesses lässt sich als **Verflechtungsdiagramm** (auch Gozintograph, von engl. „the part that *goes into*") darstellen. Dabei werden die Güter als Knoten und die Bedarfsbeziehungen als Pfeile mit den jeweiligen Mengenangaben dargestellt:

<!-- TODO: Plotly-Verflechtungsdiagramm für das Smartphone-Beispiel einfügen -->

Die Pfeile zeigen stets vom Input zum Output. Die Zahl auf einem Pfeil gibt an, wie viele ME des Inputs für eine ME des Outputs benötigt werden.

### Produktionsmatrizen

Die Beziehungen zwischen den Produktionsstufen lassen sich in **Produktionsmatrizen** zusammenfassen. In einer Produktionsmatrix gilt stets:

- **Zeile = Input** (was verbraucht wird)
- **Spalte = Output** (was hergestellt wird)

Die **Rohstoff-Zwischenprodukt-Matrix** $RZ$ gibt an, wie viele ME jedes Rohstoffs für eine ME jedes Zwischenprodukts benötigt werden:

$$
RZ = \begin{pmatrix} 5 & 2 & 1 \\ 0 & 4 & 0 \\ 1 & 0 & 6 \end{pmatrix}
$$

Die Zeilen stehen für R1 (Silizium), R2 (Lithium), R3 (Glas); die Spalten für Z1 (Chip), Z2 (Akku), Z3 (Display).

Die **Zwischenprodukt-Endprodukt-Matrix** $ZE$ gibt an, wie viele ME jedes Zwischenprodukts für eine ME jedes Endprodukts benötigt werden:

$$
ZE = \begin{pmatrix} 2 & 3 \\ 1 & 2 \\ 1 & 2 \end{pmatrix}
$$

Die Zeilen stehen für Z1, Z2, Z3; die Spalten für E1 (Alpha), E2 (Beta).

### Interpretation der Einträge

Ein Eintrag in der $i$-ten Zeile und $j$-ten Spalte einer Produktionsmatrix bedeutet:

> Für **1 ME** des Outputs $j$ werden so viele ME des Inputs $i$ benötigt.

Zum Beispiel steht die $4$ in der 2. Zeile und 2. Spalte von $RZ$: Für 1 ME Akku (Z2) werden 4 ME Lithium (R2) benötigt. Die $0$ in der 2. Zeile und 1. Spalte bedeutet: Für die Chip-Herstellung wird kein Lithium benötigt.

Da die Einträge Mengen darstellen, dürfen sie **nicht negativ** sein.

### Zusammenhang: Verflechtungsdiagramm und Produktionsmatrizen

Jeder Pfeil im Verflechtungsdiagramm entspricht genau einem Eintrag in einer Produktionsmatrix: Ein Pfeil von Input $i$ zu Output $j$ mit dem Wert $v$ bedeutet, dass in der zugehörigen Produktionsmatrix der Eintrag in der $i$-ten Zeile und $j$-ten Spalte gleich $v$ ist. Umgekehrt lässt sich jeder Matrixeintrag als Pfeil im Diagramm ablesen.

Ist kein Pfeil zwischen zwei Gütern vorhanden, so ist der entsprechende Matrixeintrag $0$.

{% include dev/check-anker.html nummer=1 %}

{% include dev/check-anker.html nummer=2 %}


## Berechnung von Produktionsmatrizen

### Die Bedarfsmatrix

Neben den stufenweisen Produktionsmatrizen $RZ$ und $ZE$ ist häufig die direkte Beziehung zwischen Rohstoffen und Endprodukten von Interesse. Die **Rohstoff-Endprodukt-Matrix** (Bedarfsmatrix) $RE$ gibt an, wie viele ME jedes Rohstoffs für eine ME jedes Endprodukts insgesamt benötigt werden.

Sie berechnet sich als Produkt der beiden Stufenmatrizen:

$$
RE = RZ \cdot ZE
$$

In unserem Beispiel:

$$
RE = \begin{pmatrix} 5 & 2 & 1 \\ 0 & 4 & 0 \\ 1 & 0 & 6 \end{pmatrix} \cdot \begin{pmatrix} 2 & 3 \\ 1 & 2 \\ 1 & 2 \end{pmatrix} = \begin{pmatrix} 13 & 21 \\ 4 & 8 \\ 8 & 15 \end{pmatrix}
$$

Die $13$ in der 1. Zeile und 1. Spalte bedeutet: Für 1 ME Alpha werden insgesamt 13 ME Silizium benötigt.

### Umstellung nach einzelnen Stufenmatrizen

Ist die Bedarfsmatrix $RE$ bekannt, so können unter bestimmten Bedingungen die einzelnen Stufenmatrizen berechnet werden. Falls die jeweiligen Inversen existieren, gilt:

$$
RZ = RE \cdot ZE^{-1} \qquad\text{und}\qquad ZE = RZ^{-1} \cdot RE
$$

Man beachte: Die Inverse einer Matrix existiert nur, wenn sie quadratisch und invertierbar ist. Die Inverse einer Produktionsmatrix kann durchaus **negative Einträge** besitzen.

{% include dev/check-anker.html nummer=3 %}


## Mengenberechnungen: Vom Output zum Input

### Mengenvektoren

Die Mengen der einzelnen Güter werden als Spaltenvektoren zusammengefasst:

- $\vec{m}$: Produktionsvektor (Mengen der Endprodukte)
- $\vec{z}$: Zwischenproduktvektor
- $\vec{r}$: Rohstoffbedarfsvektor

### Berechnung

Ist der Output gegeben, so lässt sich der benötigte Input direkt berechnen, indem die entsprechende Produktionsmatrix mit dem Outputvektor multipliziert wird:

$$
\vec{r} = RE \cdot \vec{m} \qquad \vec{z} = ZE \cdot \vec{m} \qquad \vec{r} = RZ \cdot \vec{z}
$$

### Beispiel

Es sollen 100 ME Alpha und 200 ME Beta produziert werden, also $\vec{m} = \begin{pmatrix} 100 \\ 200 \end{pmatrix}$.

Benötigte Zwischenprodukte:

$$
\vec{z} = ZE \cdot \vec{m} = \begin{pmatrix} 2 & 3 \\ 1 & 2 \\ 1 & 2 \end{pmatrix} \cdot \begin{pmatrix} 100 \\ 200 \end{pmatrix} = \begin{pmatrix} 800 \\ 500 \\ 500 \end{pmatrix}
$$

Es werden also 800 Chips, 500 Akkus und 500 Displays benötigt.

Benötigte Rohstoffe:

$$
\vec{r} = RE \cdot \vec{m} = \begin{pmatrix} 13 & 21 \\ 4 & 8 \\ 8 & 15 \end{pmatrix} \cdot \begin{pmatrix} 100 \\ 200 \end{pmatrix} = \begin{pmatrix} 5500 \\ 2000 \\ 3800 \end{pmatrix}
$$

Es werden 5500 ME Silizium, 2000 ME Lithium und 3800 ME Glas benötigt.

{% include dev/check-anker.html nummer=4 %}


## Mengenberechnungen: Vom Input zum Output

### Problemstellung

Ist umgekehrt der Input gegeben (z. B. die vorhandenen Rohstoffe) und der Output gesucht, so muss die Gleichung $\vec{r} = RE \cdot \vec{m}$ nach $\vec{m}$ aufgelöst werden. Falls $RE$ invertierbar ist, gelingt dies durch:

$$
\vec{m} = RE^{-1} \cdot \vec{r}
$$

Analog gilt $\vec{m} = ZE^{-1} \cdot \vec{z}$ und $\vec{z} = RZ^{-1} \cdot \vec{r}$, sofern die jeweiligen Inversen existieren.

### Beispiel

Es stehen $\vec{z} = \begin{pmatrix} 800 \\ 500 \\ 500 \end{pmatrix}$ Bauteile zur Verfügung. Wie viele Endprodukte können produziert werden, wenn alle Bauteile aufgebraucht werden sollen?

Die Gleichung $\vec{z} = ZE \cdot \vec{m}$ führt auf das lineare Gleichungssystem:

$$
\begin{pmatrix} 2 & 3 \\ 1 & 2 \\ 1 & 2 \end{pmatrix} \cdot \vec{m} = \begin{pmatrix} 800 \\ 500 \\ 500 \end{pmatrix}
$$

Wir lösen dieses LGS (hier: eindeutige Lösung) und erhalten $\vec{m} = \begin{pmatrix} 100 \\ 200 \end{pmatrix}$.

Es können also 100 ME Alpha und 200 ME Beta produziert werden.

### Hinweis

Nicht immer ist eine vollständige Räumung des Lagers möglich. Es kann vorkommen, dass das LGS keine Lösung besitzt – die vorhandenen Mengen lassen sich dann nicht passend kombinieren. Es kann auch vorkommen, dass das LGS mehrdeutig lösbar ist – dann gibt es mehrere mögliche Produktionsprogramme. Dieser Fall wird in einem späteren Abschnitt behandelt.

{% include dev/check-anker.html nummer=5 %}


## Kosten, Erlöse und Gewinn

Auch für mehrstufige Produktionsprozesse können betriebswirtschaftliche Kennzahlen berechnet werden. Dazu werden neben den Produktionsmatrizen und Mengenvektoren zusätzliche Geldvektoren (Zeilenvektoren) benötigt.

### Kosten

Die variablen Kosten setzen sich aus drei Kostenarten zusammen:

**Rohstoffkosten:** Der Zeilenvektor $\vec{k}_R$ enthält die Kosten für eine ME jedes Rohstoffs.

$$
\text{Rohstoffkosten} = \vec{k}_R \cdot \vec{r} = \vec{k}_R \cdot RE \cdot \vec{m}
$$

**Fertigungskosten der 1. Produktionsstufe:** Der Zeilenvektor $\vec{k}_Z$ enthält die Fertigungskosten für eine ME jedes Zwischenprodukts.

$$
\text{Fertigungskosten 1. Stufe} = \vec{k}_Z \cdot \vec{z} = \vec{k}_Z \cdot ZE \cdot \vec{m}
$$

**Fertigungskosten der 2. Produktionsstufe:** Der Zeilenvektor $\vec{k}_E$ enthält die Fertigungskosten für eine ME jedes Endprodukts.

$$
\text{Fertigungskosten 2. Stufe} = \vec{k}_E \cdot \vec{m}
$$

**Variable Stückkosten:** Der Zeilenvektor der variablen Kosten je Endprodukt lautet:

$$
\vec{k}_v = \vec{k}_R \cdot RE + \vec{k}_Z \cdot ZE + \vec{k}_E
$$

**Variable Kosten:**

$$
K_v = \vec{k}_v \cdot \vec{m}
$$

**Gesamtkosten:** Zu den variablen Kosten kommen die **Fixkosten** $K_f$ hinzu:

$$
K = K_v + K_f
$$

### Erlöse

Der Zeilenvektor $\vec{p}$ enthält die Verkaufspreise je Endprodukt. Die Erlöse sind:

$$
E = \vec{p} \cdot \vec{m}
$$

### Deckungsbeitrag

Der **Stückdeckungsbeitrag** ist die Differenz aus Preis und variablen Stückkosten:

$$
\vec{db} = \vec{p} - \vec{k}_v
$$

Der **Deckungsbeitrag** ist:

$$
DB = \vec{db} \cdot \vec{m} = E - K_v
$$

### Gewinn

$$
G = E - K = DB - K_f
$$

### Beispiel

Es werden 100 ME Alpha und 200 ME Beta produziert und verkauft, also $\vec{m} = \begin{pmatrix} 100 \\ 200 \end{pmatrix}$.

Gegeben:

$$
\vec{k}_R = \begin{pmatrix} 2 & 8 & 3 \end{pmatrix}, \quad \vec{k}_Z = \begin{pmatrix} 10 & 15 & 5 \end{pmatrix}, \quad \vec{k}_E = \begin{pmatrix} 20 & 25 \end{pmatrix}, \quad \vec{p} = \begin{pmatrix} 500 & 800 \end{pmatrix}, \quad K_f = 10000
$$

**Variable Stückkosten:**

$$
\begin{align*}
\vec{k}_v &= \vec{k}_R \cdot RE + \vec{k}_Z \cdot ZE + \vec{k}_E \\
          &= \begin{pmatrix} 2 & 8 & 3 \end{pmatrix} \cdot \begin{pmatrix} 13 & 21 \\ 4 & 8 \\ 8 & 15 \end{pmatrix} + \begin{pmatrix} 10 & 15 & 5 \end{pmatrix} \cdot \begin{pmatrix} 2 & 3 \\ 1 & 2 \\ 1 & 2 \end{pmatrix} + \begin{pmatrix} 20 & 25 \end{pmatrix} \\
          &= \begin{pmatrix} 82 & 151 \end{pmatrix} + \begin{pmatrix} 40 & 70 \end{pmatrix} + \begin{pmatrix} 20 & 25 \end{pmatrix} \\
          &= \begin{pmatrix} 142 & 246 \end{pmatrix}
\end{align*}
$$

**Variable Kosten:**

$$
K_v = \vec{k}_v \cdot \vec{m} = 142 \cdot 100 + 246 \cdot 200 = 63400
$$

**Erlöse:**

$$
E = \vec{p} \cdot \vec{m} = 500 \cdot 100 + 800 \cdot 200 = 210000
$$

**Stückdeckungsbeitrag:**

$$
\vec{db} = \vec{p} - \vec{k}_v = \begin{pmatrix} 500 - 142 & 800 - 246 \end{pmatrix} = \begin{pmatrix} 358 & 554 \end{pmatrix}
$$

**Deckungsbeitrag:**

$$
DB = \vec{db} \cdot \vec{m} = 358 \cdot 100 + 554 \cdot 200 = 146600
$$

**Gewinn:**

$$
G = DB - K_f = 146600 - 10000 = 136600
$$

{% include dev/check-anker.html nummer=6 %}


## Räumung des Lagers bei mehrdeutiger Lösung

### Problemstellung

Bei der Berechnung des Outputs aus gegebenem Input kann es vorkommen, dass das lineare Gleichungssystem $RE \cdot \vec{m} = \vec{r}$ **mehrdeutig** lösbar ist. Das bedeutet: Es gibt unendlich viele Produktionsprogramme, mit denen das Lager vollständig geräumt werden kann. In diesem Fall enthält der Lösungsvektor einen **Parameter $t$**, der verschiedene Werte annehmen kann.

### Beispiel

Ein Unternehmen stellt aus drei Rohstoffen über Zwischenprodukte vier Endprodukte E1 bis E4 her. Der Rohstoffbedarfsvektor $\vec{r}$ und die Bedarfsmatrix $RE$ sind bekannt. Die Gleichung $RE \cdot \vec{m} = \vec{r}$ liefert nach Lösen des LGS den mehrdeutigen Produktionsvektor:

$$
\vec{m} = \begin{pmatrix} 50 + 2t \\ 80 - 3t \\ t \\ 120 - t \end{pmatrix}
$$

### Zulässiger Bereich für den Parameter

Da alle Mengen nicht-negativ sein müssen, ergeben sich Bedingungen für $t$:

$$
50 + 2t \geq 0 \quad\Rightarrow\quad t \geq -25
$$

$$
80 - 3t \geq 0 \quad\Rightarrow\quad t \leq 26{,}\overline{6}
$$

$$
t \geq 0
$$

$$
120 - t \geq 0 \quad\Rightarrow\quad t \leq 120
$$

Damit alle Ungleichungen gleichzeitig erfüllt sind, muss gelten: $0 \leq t \leq 26{,}\overline{6}$. Da die Mengen ganzzahlig sein müssen: $t \in [0;\,26]$.

### Minimierung und Maximierung

Wenn der Parameter $t$ variabel ist, können betriebswirtschaftliche Größen optimiert werden.

**Maximale Menge von E3:** $m_3 = t$ wird maximal für $t = 26$:

$$
\vec{m} = \begin{pmatrix} 102 \\ 2 \\ 26 \\ 94 \end{pmatrix}
$$

**Minimale variable Kosten:** Seien die variablen Stückkosten $\vec{k}_v = \begin{pmatrix} 10 & 15 & 30 & 8 \end{pmatrix}$. Dann gilt:

$$
K_v = \vec{k}_v \cdot \vec{m} = 10(50 + 2t) + 15(80 - 3t) + 30t + 8(120 - t) = 2660 - 3t
$$

$K_v$ wird minimal für den **größten** zulässigen Wert von $t$, also $t = 26$: $K_v = 2660 - 78 = 2582$.

**Maximaler Erlös:** Sei $\vec{p} = \begin{pmatrix} 25 & 20 & 50 & 12 \end{pmatrix}$. Dann gilt:

$$
E = \vec{p} \cdot \vec{m} = 25(50 + 2t) + 20(80 - 3t) + 50t + 12(120 - t) = 4290 + 28t
$$

$E$ wird maximal für $t = 26$: $E = 4290 + 728 = 5018$.

{% include dev/check-anker.html nummer=7 %}

### Bestimmung konkreter Produktionsvektoren

Neben Optimierungsfragen kann auch ein **konkreter Wert** von $t$ gesucht sein, der eine bestimmte Bedingung erfüllt.

**Beispiel 1:** Von E3 sollen genau 18 ME produziert werden. Da $m_3 = t$, folgt $t = 18$.

**Beispiel 2:** Insgesamt sollen 250 ME der Endprodukte hergestellt werden:

$$
(50 + 2t) + (80 - 3t) + t + (120 - t) = 250 \quad\Rightarrow\quad 250 - t = 250 \quad\Rightarrow\quad t = 0
$$

**Beispiel 3:** Von E3 sollen doppelt so viele ME wie von E2 hergestellt werden:

$$
t = 2 \cdot (80 - 3t) \quad\Rightarrow\quad t = 160 - 6t \quad\Rightarrow\quad 7t = 160 \quad\Rightarrow\quad t \approx 22{,}86
$$

Da $t$ ganzzahlig sein muss, ist diese Bedingung nicht exakt erfüllbar; der nächstliegende ganzzahlige Wert wäre $t = 23$.

**Beispiel 4:** Die variablen Kosten sollen $2600$ GE betragen:

$$
2660 - 3t = 2600 \quad\Rightarrow\quad t = 20
$$

{% include dev/check-anker.html nummer=8 %}


