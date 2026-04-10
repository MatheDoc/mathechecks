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

### Verflechtungsdiagramm

Die Struktur eines mehrstufigen Produktionsprozesses lässt sich als **Verflechtungsdiagramm** (auch Gozintograph, von engl. „the part that *goes into*") darstellen. Dabei werden die Güter als Knoten und die Bedarfsbeziehungen als Pfeile mit den jeweiligen Mengenangaben dargestellt.

Die Pfeile zeigen stets vom Input zum Output. Die Zahl auf einem Pfeil gibt an, wie viele ME des Inputs für eine ME des Outputs benötigt werden.

### Produktionsmatrizen

Die Beziehungen zwischen den Produktionsstufen lassen sich in **Produktionsmatrizen** zusammenfassen. In einer Produktionsmatrix gilt stets:

- **Zeile = Input** (was verbraucht wird)
- **Spalte = Output** (was hergestellt wird)

Die **Rohstoff-Zwischenprodukt-Matrix** $RZ$ gibt an, wie viele ME jedes Rohstoffs für eine ME jedes Zwischenprodukts benötigt werden. Die **Zwischenprodukt-Endprodukt-Matrix** $ZE$ gibt an, wie viele ME jedes Zwischenprodukts für eine ME jedes Endprodukts benötigt werden.

### Interpretation der Einträge

Ein Eintrag in der $i$-ten Zeile und $j$-ten Spalte einer Produktionsmatrix bedeutet: Für **1 ME** des Outputs $j$ werden so viele ME des Inputs $i$ benötigt. Ein Eintrag $0$ bedeutet, dass der entsprechende Input für dieses Output nicht benötigt wird.

Da die Einträge Mengen darstellen, dürfen sie **nicht negativ** sein.

### Zusammenhang: Verflechtungsdiagramm und Produktionsmatrizen

Jeder Pfeil im Verflechtungsdiagramm entspricht genau einem Eintrag in einer Produktionsmatrix: Ein Pfeil von Input $i$ zu Output $j$ mit dem Wert $v$ bedeutet, dass in der zugehörigen Produktionsmatrix der Eintrag in der $i$-ten Zeile und $j$-ten Spalte gleich $v$ ist. Umgekehrt lässt sich jeder Matrixeintrag als Pfeil im Diagramm ablesen.

Ist kein Pfeil zwischen zwei Gütern vorhanden, so ist der entsprechende Matrixeintrag $0$.

{% include dev/check-anker.html nummer=1 %}

{% include dev/check-anker.html nummer=2 %}


## Berechnung von Produktionsmatrizen

### Die Bedarfsmatrix

Neben den stufenweisen Produktionsmatrizen $RZ$ und $ZE$ ist häufig die direkte Beziehung zwischen Rohstoffen und Endprodukten von Interesse. Die **Rohstoff-Endprodukt-Matrix** (Bedarfsmatrix) $RE$ gibt an, wie viele ME jedes Rohstoffs für eine ME jedes Endprodukts insgesamt benötigt werden.

Die Idee: Die Matrix $RZ$ übersetzt Zwischenprodukte in Rohstoffe, die Matrix $ZE$ übersetzt Endprodukte in Zwischenprodukte. Hintereinander ausgeführt ergibt sich die direkte Übersetzung von Endprodukten in Rohstoffe – das entspricht dem Matrizenprodukt:

$$
RE = RZ \cdot ZE
$$

Ein Eintrag in $RE$ summiert dabei alle Rohstoffbeiträge über sämtliche Zwischenprodukte auf.

### Umstellung nach einzelnen Stufenmatrizen

Ist die Bedarfsmatrix $RE$ bekannt und eine der beiden Stufenmatrizen gegeben, so kann die fehlende Matrix berechnet werden – vorausgesetzt, die bekannte Matrix ist invertierbar.

Man beachte: Die Inverse einer Matrix existiert nur, wenn sie **quadratisch** und **invertierbar** (d. h. ihre Determinante ist ungleich null) ist. Die Inverse einer Produktionsmatrix kann durchaus **negative Einträge** besitzen – das ist kein Fehler, da die Inverse selbst keine Produktionsmatrix ist.

{% include dev/check-anker.html nummer=3 %}


## Mengenberechnungen: Vom Output zum Input

### Mengenvektoren

Die Mengen der einzelnen Güter werden als Spaltenvektoren zusammengefasst:

- $\vec{m}$: Produktionsvektor (Mengen der Endprodukte)
- $\vec{z}$: Zwischenproduktvektor
- $\vec{r}$: Rohstoffbedarfsvektor

### Berechnung

Ist der Output gegeben, so lässt sich der benötigte Input direkt berechnen, indem die entsprechende Produktionsmatrix mit dem Outputvektor multipliziert wird. Je nachdem, welche Ebenen betrachtet werden, gilt:

- **Rohstoffe aus Endprodukten:** $\vec{r} = RE \cdot \vec{m}$
- **Zwischenprodukte aus Endprodukten:** $\vec{z} = ZE \cdot \vec{m}$
- **Rohstoffe aus Zwischenprodukten:** $\vec{r} = RZ \cdot \vec{z}$

Das Prinzip ist stets dasselbe: Die Produktionsmatrix steht links, der Outputvektor rechts. Das Ergebnis ist der Inputvektor.

{% include dev/check-anker.html nummer=4 %}


## Mengenberechnungen: Vom Input zum Output

### Problemstellung

Ist umgekehrt der Input gegeben (z. B. die vorhandenen Rohstoffe) und der Output gesucht, so muss die Gleichung nach dem Outputvektor aufgelöst werden. Dafür gibt es zwei Wege:

- **Über die Inverse:** Falls die Produktionsmatrix quadratisch und invertierbar ist, lässt sich der Outputvektor direkt berechnen, z. B. $\vec{m} = RE^{-1} \cdot \vec{r}$.
- **Über ein LGS:** Ist die Produktionsmatrix nicht quadratisch (z. B. mehr Zeilen als Spalten), existiert keine Inverse. In diesem Fall wird die Gleichung als lineares Gleichungssystem gelöst.

### Lösbarkeit

Die Aufgabe „Räume das Lager vollständig" führt nicht immer zu einer eindeutigen Lösung. Es gibt drei Fälle:

- **Eindeutige Lösung:** Genau ein Produktionsprogramm verbraucht den gesamten Lagerbestand.
- **Keine Lösung:** Die vorhandenen Mengen lassen sich nicht passend kombinieren – eine vollständige Räumung ist unmöglich.
- **Mehrdeutige Lösung:** Es gibt unendlich viele Produktionsprogramme, die das Lager vollständig räumen. In diesem Fall enthält der Lösungsvektor einen Parameter. Dieser Fall wird im Abschnitt „Räumung des Lagers bei mehrdeutiger Lösung" vertieft.

{% include dev/check-anker.html nummer=5 %}


## Kosten, Erlöse und Gewinn

Auch für mehrstufige Produktionsprozesse können betriebswirtschaftliche Kennzahlen berechnet werden. Dazu werden neben den Produktionsmatrizen und Mengenvektoren zusätzliche **Geldvektoren** (Zeilenvektoren) benötigt.

### Kosten

Die variablen Kosten setzen sich aus drei Kostenarten zusammen:

**Rohstoffkosten:** Der Zeilenvektor $\vec{k}_R$ enthält die Kosten für eine ME jedes Rohstoffs. Die gesamten Rohstoffkosten ergeben sich durch Multiplikation mit dem Rohstoffbedarfsvektor – oder direkt über die Bedarfsmatrix und den Produktionsvektor:

$$
\text{Rohstoffkosten} = \vec{k}_R \cdot \vec{r} = \vec{k}_R \cdot RE \cdot \vec{m}
$$

**Fertigungskosten der 1. Produktionsstufe:** Der Zeilenvektor $\vec{k}_Z$ enthält die Fertigungskosten für eine ME jedes Zwischenprodukts. Die gesamten Fertigungskosten der 1. Stufe sind:

$$
\text{Fertigungskosten 1. Stufe} = \vec{k}_Z \cdot \vec{z} = \vec{k}_Z \cdot ZE \cdot \vec{m}
$$

**Fertigungskosten der 2. Produktionsstufe:** Der Zeilenvektor $\vec{k}_E$ enthält die Fertigungskosten für eine ME jedes Endprodukts. Die gesamten Fertigungskosten der 2. Stufe sind:

$$
\text{Fertigungskosten 2. Stufe} = \vec{k}_E \cdot \vec{m}
$$

**Variable Stückkosten:** Der Zeilenvektor $\vec{k}_v$ fasst alle drei Kostenanteile zusammen und gibt die variablen Kosten je Endprodukt an. Er ergibt sich durch Addition der drei Beiträge:

$$
\vec{k}_v = \vec{k}_R \cdot RE + \vec{k}_Z \cdot ZE + \vec{k}_E
$$

Jede Komponente von $\vec{k}_v$ enthält die gesamten variablen Kosten, die für die Herstellung einer ME des jeweiligen Endprodukts anfallen – einschließlich aller Rohstoff- und Fertigungskosten beider Stufen.

**Variable Kosten:** Die gesamten variablen Kosten ergeben sich durch Multiplikation mit dem Produktionsvektor:

$$
K_v = \vec{k}_v \cdot \vec{m}
$$

**Gesamtkosten:** Zu den variablen Kosten kommen die **Fixkosten** $K_f$ hinzu:

$$
K = K_v + K_f
$$

### Erlöse

Der Zeilenvektor $\vec{p}$ enthält die Verkaufspreise je Endprodukt. Der **Erlös** ist das Skalarprodukt aus Preisvektor und Produktionsvektor:

$$
E = \vec{p} \cdot \vec{m}
$$

### Deckungsbeitrag

Der **Stückdeckungsbeitrag** gibt an, wie viel jede verkaufte Endprodukt-ME zur Deckung der Fixkosten beiträgt. Er ist die Differenz aus Preis und variablen Stückkosten:

$$
\vec{db} = \vec{p} - \vec{k}_v
$$

Der **Deckungsbeitrag** ergibt sich als Skalarprodukt mit dem Produktionsvektor und entspricht der Differenz aus Erlösen und variablen Kosten:

$$
DB = \vec{db} \cdot \vec{m} = E - K_v
$$

### Gewinn

Der **Gewinn** ist die Differenz aus Deckungsbeitrag und Fixkosten:

$$
G = E - K = DB - K_f
$$

{% include dev/check-anker.html nummer=6 %}


## Räumung des Lagers bei mehrdeutiger Lösung

### Problemstellung

Bei der Berechnung des Outputs aus gegebenem Input kann es vorkommen, dass das lineare Gleichungssystem $RE \cdot \vec{m} = \vec{r}$ **mehrdeutig** lösbar ist. Das bedeutet: Es gibt unendlich viele Produktionsprogramme, mit denen das Lager vollständig geräumt werden kann. In diesem Fall enthält der Lösungsvektor einen **Parameter $t$**, der verschiedene Werte annehmen kann.

### Zulässiger Bereich für den Parameter

Da Produktionsmengen nicht negativ sein dürfen, muss jede Komponente des Lösungsvektors $\vec{m}$ größer oder gleich null sein. Aus jeder Komponente ergibt sich eine Ungleichung für $t$. Der **zulässige Bereich** ist das Intervall, in dem alle Ungleichungen gleichzeitig erfüllt sind.

Falls laut Aufgabenstellung ganzzahlige Mengen gefordert sind, müssen die Intervallgrenzen entsprechend nach innen gerundet werden.

### Minimierung und Maximierung

Da alle betriebswirtschaftlichen Größen (Kosten, Erlöse, Deckungsbeiträge, Gewinn) vom Produktionsvektor $\vec{m}$ abhängen und dieser wiederum von $t$, lassen sich diese Größen als **lineare Funktionen von $t$** darstellen. Das Vorgehen:

1. **Ausdruck aufstellen:** Die Zielgröße (z. B. $K_v = \vec{k}_v \cdot \vec{m}$) wird durch Einsetzen der Komponenten von $\vec{m}$ als Funktion von $t$ geschrieben.
2. **Vereinfachen:** Da jede Komponente von $\vec{m}$ linear in $t$ ist, ergibt sich stets ein Ausdruck der Form $a + bt$.
3. **Optimum bestimmen:** Eine lineare Funktion nimmt ihr Maximum und Minimum an den **Randpunkten** des zulässigen Intervalls an. Je nach Vorzeichen von $b$ wird das Optimum bei der oberen oder unteren Intervallgrenze erreicht.

{% include dev/check-anker.html nummer=7 %}

### Bestimmung konkreter Produktionsvektoren

Neben Optimierungsfragen kann auch ein **konkreter Wert** von $t$ gesucht sein, der eine bestimmte Bedingung erfüllt. Typische Zusatzbedingungen sind:

- **Mengenvorgabe:** Eine bestimmte Endproduktmenge ist vorgegeben, z. B. „Von E3 sollen genau 18 ME produziert werden." Man setzt die entsprechende Komponente von $\vec{m}$ gleich dem Zielwert und löst nach $t$ auf.
- **Mengenverhältnis:** Zwei Endproduktmengen stehen in einem festen Verhältnis zueinander, z. B. „Von E3 sollen doppelt so viele ME wie von E2 hergestellt werden." Man stellt die Verhältnisgleichung auf und löst nach $t$.
- **Gesamtmenge:** Die Summe aller Endproduktmengen ist vorgegeben. Man addiert alle Komponenten von $\vec{m}$ und setzt gleich.
- **Kostenvorgabe:** Die variablen Kosten oder der Erlös sollen einen bestimmten Wert annehmen. Man setzt den bereits aufgestellten Ausdruck $K_v(t)$ bzw. $E(t)$ gleich dem Zielwert.

In jedem Fall ergibt sich eine Gleichung in $t$, die gelöst wird. Anschließend ist zu prüfen, ob der gefundene Wert im zulässigen Bereich liegt und – falls ganzzahlige Mengen gefordert sind – ob eine ganzzahlige Lösung existiert.

{% include dev/check-anker.html nummer=8 %}


