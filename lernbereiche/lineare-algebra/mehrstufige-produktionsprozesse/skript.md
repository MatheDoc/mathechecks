---
layout: skript
title: Mehrstufige Produktionsprozesse
description: Mehrstufige Produktionsprozesse - Skript
lernbereich: mehrstufige-produktionsprozesse
---

## Einführung

{%include info.html
index="1"
frage="Interpretation von Matrizenelementen"
antwort="Produktionsmatrizen geben an, wie viele ME eines Inputprodukts für eine ME eines Outputprodukts benötigt werden, dabei gilt:

- Zeilentitel ➡️ Input
- Spaltentitel ➡️ Output

Ist z.B.

$$
RZ =
\begin{pmatrix}
3&5\\
4&2\\
\end{pmatrix},
$$

so sind die Rohstoffe der Input und die Zwischenprodukte der Output. Die $4$ bedeutet also: Für eine ME von Z1 werden $4$ ME von R2 benötigt.

"
%}

<div id="skript-aufgabe-1"></div>

{%include info.html
index="2"
frage="Berechnung von Produktionsmatrizen"
antwort="Die Produktionsmatrix eines zweistufigen Produktionsprozesses $RE$ ist das Produkt der Produktionsmatrizen der ersten ($RZ$) und zweiten Stufe ($ZE$):

$$
RE=RZ\cdot ZE
$$

Diese Gleichung kann, falls die jeweilgen inversen Matrizen existieren, nach $RZ$ und $ZE$ umgeformt werden:

* $RZ = RE\cdot ZE^{-1}$
* $ZE=RZ^{-1}\cdot RE$

"
%}

<div id="skript-aufgabe-2"></div>

{%include info.html
index="3"
frage="Berechnung des Inputs"
antwort="Mit einer Produktionsmatrix lässt sich aus einem gegebenen Output der benötigte Input bestimmen:

* $\vec{r}=RE\cdot\vec{m}$
* $\vec{z}=ZE\cdot\vec{m}$
* $\vec{r}=RZ\cdot\vec{z}$



"
%}

<div id="skript-aufgabe-3"></div>

{%include info.html
index="4"
frage="Berechnung des Outputs"
antwort="Die Gleichungen (siehe 3. Info) können, falls die jeweilgen inversen Matrizen existieren, so umgeformt werden, dass sich aus einem gegebenen Input der mögliche Output bestimmt werden kann:

* $\vec{m}=RE^{-1}\cdot\vec{r}$
* $\vec{m}=ZE^{-1}\cdot\vec{z}$
* $\vec{z}=RZ^{-1}\cdot\vec{r}$

"
%}

<div id="skript-aufgabe-4"></div>

{%include info.html
index="5"
frage="Berechnung betriebswirtschaftlicher Kennzahlen"
antwort="
### Kosten

* Rohstoffkosten

$$
\begin{align*}
\vec{k}_R\cdot \vec{r}&=\vec{k}_R\cdot RE\cdot\vec{m}
\end{align*}
$$

* Fertigungskosten der 1. Produktionsstufe

$$
\begin{align*}
\vec{k}_Z\cdot \vec{z}&=\vec{k}_Z\cdot ZE\cdot\vec{m}
\end{align*}
$$

* Fertigungskosten der 2. Produktionsstufe

$$
\begin{align*}
\vec{k}_E\cdot \vec{m}&=
\end{align*}
$$

* Variable Stückkosten:

$$
\begin{align*}
\vec{k}_v&=\vec{k}_R\cdot RE + \vec{k}_Z\cdot ZE + \vec{k}_E
\end{align*}
$$

* Variable Kosten:

$$
\begin{align*}
K_v&=\vec{k}_v\cdot\vec{m}\\
    &=\vec{k}_R\cdot RE\cdot\vec{m} + \vec{k}_Z\cdot ZE\cdot\vec{m} + \vec{k}_E\cdot\vec{m}$
\end{align*}
$$

* Fixkosten

$$
\begin{align*}
K_{f}
\end{align*}
$$

* Gesamtkosten

$$
\begin{align*}
K=K_v+K_{f}
\end{align*}
$$

### Erlöse

* Gesamterlös:

$$
\begin{align*}
E=\vec{p}\cdot {m}
\end{align*}
$$

### Deckungsbeiträge

* Stückdeckungsbeitrag:

$$
\begin{align*}
\vec{db}=\vec{p}-\vec{k}_v
\end{align*}
$$

* Gesamtdeckungsbeitrag:

$$
\begin{align*}
DB=\vec{db}\cdot\vec{m}
\end{align*}
$$

### Gewinne

* Gesamtgewinn:

$$
\begin{align*}
G=E-K
\end{align*}
$$

"
%}

<div id="skript-aufgabe-5"></div>