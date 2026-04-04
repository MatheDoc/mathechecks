---
layout: dev-module
title: Produktlebenszyklus - Skript (Dev)
description: Dev-Lernbereich Produktlebenszyklus, Modul Skript.
page_context: Lernbereich
nav: dashboard
body_class: page-module-designs
module_key: skript
published: true
lernbereich: produktlebenszyklus
gebiet: analysis
permalink: /dev/lernbereiche/analysis/produktlebenszyklus/skript.html
---

## Einführung

Der Produktlebenszyklus beschreibt die Entwicklung des jährlichen Umsatzes eines Produkts über die Zeit seit seiner Markteinführung. Die Umsatzfunktion $u(t)$ gibt den (wöchentlichen, monatlichen, jährlichen) Umsatz in Geldeinheiten (GE) zum Zeitpunkt $t$ (in Wochen, Monsten, Jahren) nach der Produkteinführung an.

Typische Produktlebenszyklusfunktionen bestehen aus einem Produkt von Polynomen und der natürlichen Exponentialfunktion, z.B.:

$$
u(t) = (-2t^2+24t) \cdot e^{-0{,}2t}
$$

Der Produktlebenszyklus durchläuft dabei häufig folgende Phasen:

1. Einführungsphase: Der Umsatz steigt zunächst langsam an.
2. Wachstumsphase: Der Umsatz wächst immer stärker.
3. Reifephase: Das Umsatzwachstum verlangsamt sich, der maximale Umsatz wird erreicht.
4. Degenerationsphase: Der Umsatz geht zurück.

Je nach Funktionstyp endet der Produktlebenszyklus auf zwei verschiedene Arten:

- Marktaustritt: Das Produkt wird vom Markt genommen, wenn der jährliche Umsatz auf null sinkt, d.h. $u(t)=0$ für ein $t > 0$.
- Langfristiger Umsatz: Der jährliche Umsatz nähert sich langfristig einem festen Wert $d > 0$ an, d.h. $\lim\limits_{t \to \infty} u(t) = d$.

## Kennzahlen des Produktlebenszyklus

Die folgenden Kennzahlen beschreiben den Produktlebenszyklus:

| Kennzahl | Bedeutung |
|---|---|
| $u(0)$ | Jährlicher Umsatz bei der Produkteinführung |
| Extremstelle (Hochpunkt) von $u$ | Zeitpunkt des höchsten jährlichen Umsatzes |
| Maximum von $u$ | Höhe des höchsten jährlichen Umsatzes |
| Extremstelle (Hochpunkt) von $u^{\prime}$ | Zeitpunkt des stärksten Umsatzanstiegs |
| Extremstelle (Tiefpunkt) von $u^{\prime}$ | Zeitpunkt des stärksten Umsatzrückgangs |
| $u^{\prime}(t_0)$ | Jährliche Veränderung des Umsatzes zum Zeitpunkt $t_0$ |
| $u(t)=0$ für $t>0$ | Marktaustritt |
| $\lim\limits_{t \to \infty}u(t)$ | Langfristig zu erwartender jährlicher Umsatz |


## Graphische Bestimmung der Kennzahlen

### Der Graph der Umsatzfunktion


{% include dev/check-anker.html nummer="1" %}


Im Folgenden verwenden wir die Funktion $u(t)=(-2t^2+24t)\cdot e^{-0{,}2t}$ (mit Marktaustritt bei $t=12$) als durchgängiges Beispiel für die detaillierte Analyse.

### Der Graph der Ableitungsfunktion

Die Ableitung $u^{\prime}(t)$ gibt die jährliche Veränderung des Umsatzes an. Aus dem Graphen von $u^{\prime}(t)$ lassen sich diejenigen Kennzahlen ablesen, die nicht vom absoluten Wert des Umsatzes abhängen.

{% include dev/check-anker.html nummer="2" %}



## Rechnerische Bestimmung der Kennzahlen (ohne Integration)

Die Kennzahlen des Produktlebenszyklus lassen sich auch rechnerisch bestimmen. Dazu benötigen wir $u(t)$ sowie die ersten drei Ableitungen.

Wichtige Eigenschaft: Da $e^{-ct}>0$ für alle $t$ gilt, können bei der Nullstellensuche die Exponentialanteile vernachlässigt werden – es genügt, die Nullstellen des Polynomanteil zu bestimmen.


{% include dev/check-anker.html nummer="3" %}






## Kennzahlen mit Integration

Mithilfe der Integration lassen sich weitere Kennzahlen des Produktlebenszyklus berechnen.

Zetrale Beobachtung: Wenn $u(t)$ den jährlichen Umsatz angibt, dann gibt die Fläche unter dem Graphen von $u$ über einem Intervall $[a;b]$ den Gesamtumsatz in diesem Zeitraum an.

Wir müssen genauesten unterscheiden zwischen 

- dem **jährlichen Umsatz** $u(t)$ (Wert der Funktion $u$) und
- dem **Gesamtumsatz** (Fläche unter dem Graphen von $u$ über dem Intervall $[a;b]$).

### Formeln

- Umsatz über einen Zeitraum vom Ende des $a$-ten bis zum Ende des $b$-ten Jahres:

  $$
  \int_a^b u(t)\,dt
  $$

- Durchschnittlicher jährlicher Umsatz vom Ende des $a$-ten bis zum Ende des $b$-ten Jahres:

  $$
  \bar{u}=\frac{1}{n}\int_a^b u(t)\,dt
  $$

- Gesamtumsatz während des Produktlebenszyklus (von $t=0$ bis zum Ende $t=T$):

  $$
  U_{\text{gesamt}}=\int_0^T u(t)\,dt
  $$

  Dabei ist $T$ der Zeitpunkt des Marktaustritts oder das angegebene Ende des Produktlebenszyklus.

{% include dev/check-anker.html nummer="4" %}

## Der EKG-Zyklus

Beim EKG-Zyklus (Erlös – Kosten – Gewinn) werden neben der Erlösfunktion $E(t)$ auch die Kostenfunktion $K(t)$ und die daraus resultierende Gewinnfunktion $G(t)=E(t)-K(t)$ betrachtet.

### Typische Funktionsformen

$$
\begin{align*}
E(t) &= p(t)\cdot e^{-ct} &&\text{(Erlöse)}\\
K(t) &= q(t)\cdot e^{-ct}+K_f &&\text{(variable Kosten + Fixkosten)}
\end{align*}
$$

Dabei gilt:

- $E(0)=0$: Zu Beginn werden keine Erlöse erzielt.
- $K(0)=K_f > 0$: Von Beginn an fallen Fixkosten an.
- Daraus folgt: $G(0) = -K_f < 0$, d.h. zu Beginn entstehen Verluste.

### Kennzahlen des EKG-Zyklus

- Zeitraum der Kostendeckung:

  Die Kosten werden gedeckt, solange $G(t) \geq 0$ gilt, also

  $$E(t) \geq K(t) \quad\Leftrightarrow\quad G(t) \geq 0$$

  Die Grenzen $t_1$ und $t_2$ dieses Zeitraums bestimmt man durch $G(t)=0$.

- Gesamtgewinn während des Produktlebenszyklus:

  $$
  G_{\text{gesamt}}=\int_0^T G(t)\,dt = \int_0^T \big(E(t)-K(t)\big)\,dt
  $$

  Dabei ist $T$ der Zeitpunkt des Marktaustritts oder das angegebene Ende des Produktlebenszyklus.

### Zeitpunkt des maximalen Gesamtverlusts

Da typischerweise $G(0)=-K_f < 0$, startet die Gewinnfunktion im negativen Bereich. Häufig hat $G(t)$ zwei positive Nullstellen $t_1$ und $t_2$:

- Für $t\in [0;t_1]$ gilt $G(t)<0$ → Die Verluste nehmen zu bzw. die Gewinne nehmen ab
- Für $t\in[t_1; t_2]$ gilt $G(t)>0$ → Die Verluste nehmen ab bzw. die Gewinne nehmen zu
- Für $t > t_2$: $G(t)<0$ → Die Verluste nehmen erneut zu bzw. die Gewinne nehmen ab

Damit gibt es zwei Kandidaten für den maximalen Gesamtverlust: $t_1$ und $T$ (Ende des Lebenszyklus). 

Das folgende Diagramm verdeutlicht die Situation am Beispiel der Gewinnfunktion

$$
G(t)=(-0{,}4t^3+11t^2)\cdot e^{-0{,}2t}-36{,}5.
$$

{% include dev/graph.html
   funktionen='[
    {"name":"G(t)", "term":"(-0.4*x^3+11*x^2)*exp(-0.2*x)-36.5", "beschreibung":"Gewinnfunktion"}
   ]'
   flaechen='[
    {"term":"(-0.4*x^3+11*x^2)*exp(-0.2*x)-36.5", "von":0, "bis":2.43, "farbe":"rgba(220,50,50,0.25)", "name":"Anfangsverlust"},
    {"term":"(-0.4*x^3+11*x^2)*exp(-0.2*x)-36.5", "von":2.43, "bis":17.57, "farbe":"rgba(50,160,50,0.25)", "name":"Gewinnphase"},
    {"term":"(-0.4*x^3+11*x^2)*exp(-0.2*x)-36.5", "von":17.57, "bis":27.5, "farbe":"rgba(220,50,50,0.25)", "name":"Spätverlust"}
   ]'
   punkte='[
     {"x":0,"y":-36.5,"text":"G(0)=-Kf"},
     {"x":2.43,"y":0,"text":"t₁≈2,43"},
     {"x":17.57,"y":0,"text":"t₂≈17,57"},
     {"x":27.5,"y":-36.5,"text":"T=27,5"}
   ]'
   titel="Gewinnfunktion G(t) – Phasen des EKG-Zyklus"
   xachse="Zeit t in Jahren"
   yachse="jährlicher Gewinn in GE"
   xmin=0
   xmax=29
   ymin=-45
   ymax=70
%}

- Rote Fläche links ($0$ bis $t_1$): Anfangsverluste – $V(t_1)$ entspricht dieser Fläche.
- Grüne Fläche ($t_1$ bis $t_2$): Gewinnphase – reduziert den kumulierten Verlust.
- Rote Fläche rechts ($t_2$ bis $T$): Erneute Verluste am Ende des Lebenszyklus.

Falls

$$
\int_0^{t_1}G(t)\,dt < \int_0^{T}G(t)\,dt
$$

ist, so sind die anfänglichen Verluste größer als ein möglicher Gesamtverlust, und der Zeitpunkt der maximalen Verlusts ist $t_1$.

{% include dev/check-anker.html nummer="5" %}