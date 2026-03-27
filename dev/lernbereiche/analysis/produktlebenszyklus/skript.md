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

Der **Produktlebenszyklus** beschreibt die Entwicklung des jährlichen Umsatzes eines Produkts über die Zeit seit seiner Markteinführung. Die Umsatzfunktion $u(t)$ gibt den (wöchentlichen, monatlichen, jährlichen) Umsatz in Geldeinheiten (GE) zum Zeitpunkt $t$ (in Wochen, Monsten, Jahren) nach der Produkteinführung an.

Typische Produktlebenszyklusfunktionen bestehen aus einem Produkt von Polynomen und der natürlichen Exponentialfunktion, z.B.:

$$
u(t) = (-2t^2+24t) \cdot e^{-0{,}2t}
$$

Der Produktlebenszyklus durchläuft dabei häufig folgende Phasen:

1. **Einführungsphase**: Der Umsatz steigt zunächst langsam an.
2. **Wachstumsphase**: Der Umsatz wächst immer stärker.
3. **Reifephase**: Das Umsatzwachstum verlangsamt sich, der maximale Umsatz wird erreicht.
4. **Degenerationsphase**: Der Umsatz geht zurück.

Je nach Funktionstyp endet der Produktlebenszyklus auf zwei verschiedene Arten:

- **Marktaustritt**: Das Produkt wird vom Markt genommen, wenn der jährliche Umsatz auf null sinkt, d.h. $u(t)=0$ für ein $t > 0$.
- **Langfristiger Umsatz**: Der jährliche Umsatz nähert sich langfristig einem festen Wert $d > 0$ an, d.h. $\lim\limits_{t \to \infty} u(t) = d$.

## Kennzahlen des Produktlebenszyklus

Die folgenden **Kennzahlen** beschreiben den Produktlebenszyklus:

| Kennzahl | Bedeutung |
|---|---|
| $u(0)$ | Jährlicher Umsatz bei der **Produkteinführung** |
| Extremstelle (Hochpunkt) von $u$ | **Zeitpunkt des höchsten jährlichen Umsatzes** |
| Maximum von $u$ | **Höhe des höchsten jährlichen Umsatzes** |
| Extremstelle (Hochpunkt) von $u^{\prime}$ | Zeitpunkt des **stärksten Umsatzanstiegs** |
| Extremstelle (Tiefpunkt) von $u^{\prime}$ | Zeitpunkt des **stärksten Umsatzrückgangs** |
| $u^{\prime}(t_0)$ | **Jährliche Veränderung des Umsatzes** zum Zeitpunkt $t_0$ |
| $u(t)=0$ für $t>0$ | **Marktaustritt** |
| $\lim\limits_{t \to \infty}u(t)$ | **Langfristig zu erwartender jährlicher Umsatz** |


## Graphische Bestimmung der Kennzahlen

### Der Graph der Umsatzfunktion

Das folgende Diagramm zeigt zwei typische Produktlebenszyklusfunktionen:

$$u_1(t)=(-t^2+20t)\cdot e^{-0{,}2t} \qquad \text{(Marktaustritt)}$$

$$u_2(t)=(3t^2+8)\cdot e^{-0{,}3t}+2 \qquad \text{(langfristiger Umsatz)}$$

{% include dev/graph.html
   funktionen='[
    {"name":"u₁(t)", "term":"(-1*x^2+20*x)*exp(-0.2*x)", "beschreibung":"Marktaustritt", "xmax":20},
    {"name":"u₂(t)", "term":"(3*x^2+8)*exp(-0.3*x)+2", "beschreibung":"langfristiger Umsatz"}
   ]'
   punkte='[
     {"x":0,"y":0,"text":"u₁(0)=0"},
     {"x":3.82,"y":28.8,"text":"max. Umsatz u₁"},
     {"x":20,"y":0,"text":"Marktaustritt"},
     {"x":0,"y":10,"text":"u₂(0)=10"},
     {"x":6.24,"y":21.18,"text":"max. Umsatz u₂"},
     {"x":26,"y":2.3,"text":"langfristiger Umsatz → 2"}
   ]'
   titel="Zwei Typen von Produktlebenszyklusfunktionen"
   xachse="Zeit t in Jahren"
   yachse="jährlicher Umsatz in GE"
   xmin=0
   xmax=30
   ymin=-3
   ymax=35
%}

**Funktion $u_1$ (Marktaustritt):**

- Umsatz bei Produkteinführung: $u_1(0)=0$ GE
- Höchster jährlicher Umsatz: ca. $28{,}8$ GE bei $t \approx 3{,}8$
- **Marktaustritt** bei $t=20$, da $u_1(20)=0$
- Der Umsatz sinkt auf null – das Produkt wird vom Markt genommen.

**Funktion $u_2$ (langfristiger Umsatz):**

- Umsatz bei Produkteinführung: $u_2(0)=10$ GE
- Höchster jährlicher Umsatz: ca. $21{,}2$ GE bei $t \approx 6{,}2$
- **Langfristiger Umsatz**: $\lim\limits_{t\to\infty}u_2(t)=2$ GE
- Der Umsatz nähert sich langfristig dem Wert $2$ GE an, erreicht aber nie null.

{% include info.html
index="1"
frage="Bestimme anhand des obigen Graphen für die Funktion $u_1$ die folgenden Kennzahlen: (a) den jährlichen Umsatz bei der Produkteinführung, (b) den Zeitpunkt und die Höhe des höchsten jährlichen Umsatzes, (c) den Zeitpunkt des Marktaustritts, (d) den jährlichen Umsatz nach 9 Jahren."
antwort="

**(a)** Umsatz bei der Produkteinführung: Wir lesen $u_1(0)=0$ GE ab.

**(b)** Der höchste Punkt des Graphen von $u_1$ liegt bei ca. $t\approx 3{,}8$ Jahren. Die Höhe des höchsten jährlichen Umsatzes beträgt ca. $28{,}8$ GE.

**(c)** Der Graph von $u_1$ schneidet die $t$-Achse bei $t=20$. Das Produkt wird also nach $20$ Jahren vom Markt genommen (**Marktaustritt**).

**(d)** Wir lesen vom Graphen ab: $u_1(9)\approx 16{,}4$ GE.

**Allgemein gilt:** Am **Graphen von $u(t)$** lassen sich ablesen:

- Umsatz bei Produkteinführung: $y$-Wert bei $t=0$
- Maximaler Umsatz: höchster Punkt des Graphen
- Marktaustritt: Schnittpunkt mit der $t$-Achse für $t>0$
- Langfristiger Umsatz: Wert, dem sich der Graph für große $t$ annähert (falls kein Marktaustritt)
- Funktionswerte: $y$-Wert an der gewünschten Stelle

"
%}

Im Folgenden verwenden wir die Funktion $u(t)=(-2t^2+24t)\cdot e^{-0{,}2t}$ (mit Marktaustritt bei $t=12$) als durchgängiges Beispiel für die detaillierte Analyse.

### Der Graph der Ableitungsfunktion

Die Ableitung $u^{\prime}(t)$ gibt die **jährliche Veränderung des Umsatzes** an. Aus dem Graphen von $u^{\prime}(t)$ lassen sich weitere Kennzahlen ablesen.

Für das obige Beispiel gilt:

$$u^{\prime}(t) = (0{,}4t^2-8{,}8t+24)\cdot e^{-0{,}2t}$$

{% include dev/graph.html
   funktionen='[
    {"name":"u\u2032(t)", "term":"(0.4*x^2-8.8*x+24)*exp(-0.2*x)", "beschreibung":"Ableitung der Umsatzfunktion"}
   ]'
   punkte='[
     {"x":3.19,"y":0,"text":"Nullstelle: max. Umsatz"},
     {"x":0,"y":24,"text":"stärkster Anstieg"},
     {"x":6.73,"y":-3.16,"text":"stärkster Rückgang"}
   ]'
   titel="Ableitung der Produktlebenszyklusfunktion"
   xachse="Zeit t in Jahren"
   yachse="Veränderung u\u2032(t) in GE/Jahr"
   xmin=0
   xmax=16
   ymin=-5
   ymax=28
%}

Aus dem Graphen der Ableitungsfunktion lassen sich folgende Kennzahlen ablesen:

- **Zeitpunkt des höchsten jährlichen Umsatzes**: Die Nullstelle von $u^{\prime}(t)$ mit Vorzeichenwechsel von $+$ nach $-$ (hier bei $t \approx 3{,}2$). An dieser Stelle hat $u$ ein Maximum.
- **Zeitpunkt des stärksten Umsatzanstiegs**: Die Stelle, an der $u^{\prime}(t)$ den **größten Wert** annimmt (**globales Maximum** von $u^{\prime}$, hier bei $t=0$). **Achtung:** Das muss kein lokaler Hochpunkt von $u^{\prime}$ sein – oft liegt der stärkste Anstieg am Rand des Definitionsbereichs (z. B. bei der Produkteinführung).
- **Zeitpunkt des stärksten Umsatzrückgangs**: Die Stelle, an der $u^{\prime}(t)$ den **kleinsten Wert** annimmt (**globales Minimum** von $u^{\prime}$, hier bei $t \approx 6{,}7$). Auch hier kann der Rand relevant sein.
- **Jährliche Veränderung des Umsatzes nach $t_0$ Jahren**: Der Funktionswert $u^{\prime}(t_0)$.

{% include info.html
index="2"
frage="Bestimme anhand des obigen Graphen der Ableitungsfunktion: (a) den Zeitpunkt des höchsten jährlichen Umsatzes, (b) den Zeitpunkt des stärksten Umsatzanstiegs, (c) den Zeitpunkt des stärksten Umsatzrückgangs, (d) die jährliche Veränderung des Umsatzes nach 3 Jahren."
antwort="

**(a)** Die **Nullstelle** von $u^{\prime}$ mit Vorzeichenwechsel von $+$ nach $-$ liegt bei $t\approx 3{,}2$. Der höchste jährliche Umsatz wird also nach ca. $3{,}2$ Jahren erzielt.

**(b)** Gesucht ist das **globale Maximum** von $u^{\prime}(t)$. Wir vergleichen den Randwert $u^{\prime}(0)=24$ mit dem lokalen Hochpunkt (falls vorhanden). Hier ist $u^{\prime}(0)=24$ der größte Wert – der stärkste Umsatzanstieg findet also **bei der Produkteinführung** statt.

**(c)** Gesucht ist das **globale Minimum** von $u^{\prime}(t)$. Der tiefste Punkt des Graphen von $u^{\prime}$ liegt bei $t\approx 6{,}7$ mit $u^{\prime}(6{,}7)\approx -3{,}2$. Der stärkste Umsatzrückgang findet nach ca. $6{,}7$ Jahren statt.

**(d)** Wir lesen ab: $u^{\prime}(3)\approx 1{,}9$ GE/Jahr. Der Umsatz steigt nach $3$ Jahren noch leicht an.

**Allgemein gilt:** Am **Graphen von $u^{\prime}(t)$** lassen sich ablesen:

- Zeitpunkt des maximalen Umsatzes: Nullstelle mit VZW $+/-$
- Stärkster Anstieg: **globales Maximum** von $u^{\prime}$ (höchster Punkt, ggf. am Rand!)
- Stärkster Rückgang: **globales Minimum** von $u^{\prime}$ (tiefster Punkt, ggf. am Rand!)
- Jährliche Veränderung: Funktionswert von $u^{\prime}$

**Hinweis:** Die **lokalen** Extremstellen von $u^{\prime}(t)$ entsprechen den **Wendestellen** von $u(t)$. Aber für den stärksten Anstieg/Rückgang sind die **globalen** Extrema entscheidend – diese können auch am Rand liegen (z. B. bei $t=0$).

"
%}

## Rechnerische Bestimmung der Kennzahlen (ohne Integration)

Die Kennzahlen des Produktlebenszyklus lassen sich auch rechnerisch bestimmen. Dazu benötigen wir $u(t)$ sowie die Ableitungen $u^{\prime}(t)$ und $u^{\prime\prime}(t)$.

**Wichtige Eigenschaft:** Da $e^{-ct}>0$ für alle $t$ gilt, können bei der Nullstellensuche die Exponentialanteile vernachlässigt werden – es genügt, den **Polynomanteil** gleich null zu setzen.

### Beispiel

Gegeben sei die Umsatzfunktion

$$u(t)=(-2t^2+24t)\cdot e^{-0{,}2t}$$

mit den Ableitungen:

$$
\begin{align*}
u^{\prime}(t) &= (0{,}4t^2-8{,}8t+24)\cdot e^{-0{,}2t}\\
u^{\prime\prime}(t) &= (-0{,}08t^2+2{,}56t-13{,}6)\cdot e^{-0{,}2t}
\end{align*}
$$

### Umsatz bei Produkteinführung

$$u(0)=(-2\cdot 0^2+24\cdot 0)\cdot e^{0}=0 \text{ GE}$$

### Marktaustritt und langfristiger Umsatz

Für den **Marktaustritt** lösen wir $u(t)=0$ mit $t > 0$. Da $e^{-0{,}2t}\neq 0$:

$$
\begin{align*}
-2t^2+24t &= 0\\
t(-2t+24) &= 0\\
t_1 = 0 \quad&\quad t_2 = 12
\end{align*}
$$

Das Produkt wird nach $12$ Jahren vom Markt genommen.

**Hinweis:** Bei Funktionen der Form $u(t)=p(t)\cdot e^{-ct}+d$ mit $d>0$ gibt es keinen Marktaustritt. Stattdessen gilt $\lim\limits_{t\to\infty} u(t)=d$ (langfristiger Umsatz).

### Maximaler jährlicher Umsatz

Notwendige Bedingung $u^{\prime}(t)=0$:

$$
\begin{align*}
0{,}4t^2-8{,}8t+24 &= 0 \quad |:0{,}4\\
t^2-22t+60 &= 0 \quad |\text{ pq-Formel}\\
t_{1{,}2} &= 11\pm\sqrt{121-60}\\
t_1 &\approx 3{,}19 \quad t_2 \approx 18{,}81
\end{align*}
$$

Nur $t_1 \approx 3{,}19$ liegt im Produktlebenszyklus $[0;\,12]$.

Hinreichende Bedingung: $u^{\prime\prime}(3{,}19) \approx -4{,}78 < 0$ ✓ (Maximum)

$$u(3{,}19) \approx (-2\cdot 3{,}19^2+24\cdot 3{,}19)\cdot e^{-0{,}2\cdot 3{,}19} \approx 29{,}67 \text{ GE}$$

Der höchste jährliche Umsatz beträgt ca. $29{,}67$ GE nach ca. $3{,}19$ Jahren.

### Stärkster Umsatzanstieg und -rückgang

Wir bestimmen die **Wendestellen von $u$** (= Extremstellen von $u^{\prime}$) über $u^{\prime\prime}(t)=0$:

$$
\begin{align*}
-0{,}08t^2+2{,}56t-13{,}6 &= 0 \quad |:(-0{,}08)\\
t^2-32t+170 &= 0 \quad |\text{ pq-Formel}\\
t_{1{,}2} &= 16 \pm\sqrt{256-170}\\
t_1 &\approx 6{,}73 \quad t_2 \approx 25{,}27
\end{align*}
$$

Nur $t_1 \approx 6{,}73$ liegt im Produktlebenszyklus. Es gilt $u^{\prime}(6{,}73) \approx -3{,}16 < 0$, also handelt es sich um den **stärksten Umsatzrückgang**.

Für den **stärksten Umsatzanstieg** prüfen wir den Rand: $u^{\prime}(0)=24 > 0$. Der stärkste Anstieg liegt bei $t=0$.

{% include info.html
index="3"
frage="Die Funktion $u(t)=(7{,}6t^2+15)\cdot e^{-0{,}4t}+1$ gibt den jährlichen Umsatz an, mit $u^{\prime}(t)=(-3{,}04t^2+15{,}2t-6)\cdot e^{-0{,}4t}$ und $u^{\prime\prime}(t)=(1{,}216t^2-12{,}16t+17{,}6)\cdot e^{-0{,}4t}$. Bestimme (a) $u(0)$, (b) den langfristigen Umsatz, (c) den Zeitpunkt und die Höhe des maximalen Umsatzes, (d) den Zeitpunkt des stärksten Anstiegs."
antwort="

**(a) Umsatz bei Produkteinführung:**

$$u(0)=(7{,}6\cdot 0+15)\cdot e^{0}+1=16 \text{ GE}$$

**(b) Langfristiger Umsatz:**

Da $(7{,}6t^2+15)\cdot e^{-0{,}4t}\to 0$ für $t\to\infty$:

$$\lim_{t\to\infty}u(t) = 0 + 1 = 1 \text{ GE}$$

**(c) Maximaler Umsatz:** Setze $u^{\prime}(t)=0$:

$$
\begin{align*}
-3{,}04t^2+15{,}2t-6 &= 0 \quad |:(-3{,}04)\\
t^2-5t+\frac{6}{3{,}04} &= 0\\
t^2 - 5t + 1{,}97 &= 0 \quad |\text{ pq-Formel}\\
t_{1{,}2} &= 2{,}5\pm\sqrt{6{,}25-1{,}97}\\
t_1 &\approx 0{,}43 \quad t_2 \approx 4{,}57
\end{align*}
$$

Prüfe $u^{\prime\prime}(4{,}57)\approx (1{,}216\cdot 20{,}88-12{,}16\cdot 4{,}57+17{,}6)\cdot e^{-1{,}83} \approx -1{,}74 < 0$ ✓ (Maximum)

$$u(4{,}57) \approx (7{,}6\cdot 20{,}88+15)\cdot e^{-1{,}83}+1 \approx 28{,}92 \text{ GE}$$

**(d) Stärkster Umsatzanstieg:** Setze $u^{\prime\prime}(t)=0$:

$$
\begin{align*}
1{,}216t^2-12{,}16t+17{,}6 &= 0 \quad |:1{,}216\\
t^2-10t+14{,}47 &= 0 \quad |\text{ pq-Formel}\\
t_{1{,}2} &= 5\pm\sqrt{25-14{,}47}\\
t_1 &\approx 1{,}76 \quad t_2 \approx 8{,}24
\end{align*}
$$

$u^{\prime}(1{,}76)\approx 6{,}52 > 0$ und $u^{\prime}(8{,}24)\approx -1{,}91 < 0$.

$t_1\approx 1{,}76$ ist der Zeitpunkt des stärksten Umsatzanstiegs. Prüfe Rand: $u^{\prime}(0)=-6 <0$, also liegt der stärkste Anstieg tatsächlich bei $t_1\approx 1{,}76$.

**Hinweis:** Bei diesem Funktionstyp fällt der Umsatz bei der Produkteinführung zunächst, bevor er ansteigt.

"
%}

## Kennzahlen mit Integration

Mithilfe der Integration lassen sich weitere Kennzahlen des Produktlebenszyklus berechnen.

### Formeln

- **Umsatz über einen Zeitraum** vom Ende des $a$-ten bis zum Ende des $b$-ten Jahres:

$$\int_a^b u(t)\,dt$$

- **Durchschnittlicher jährlicher Umsatz** in den ersten $n$ Jahren:

$$\bar{u}=\frac{1}{n}\int_0^n u(t)\,dt$$

- **Gesamtumsatz** während des Produktlebenszyklus (von $t=0$ bis zum Ende $t=T$):

$$U_{\text{gesamt}}=\int_0^T u(t)\,dt$$

Dabei ist $T$ der Zeitpunkt des Marktaustritts oder das angegebene Ende des Produktlebenszyklus.

### Beispiel

Für $u(t)=(-2t^2+24t)\cdot e^{-0{,}2t}$ mit Marktaustritt bei $t=12$ berechnen wir (mit TR):

- **Gesamtumsatz**: $\displaystyle\int_0^{12} u(t)\,dt \approx 199{,}77$ GE

- **Umsatz vom Ende des 3. bis zum Ende des 9. Jahres**: $\displaystyle\int_3^9 u(t)\,dt \approx 126{,}00$ GE

- **Durchschnittlicher jährlicher Umsatz in den ersten 6 Jahren**: $\displaystyle\frac{1}{6}\int_0^6 u(t)\,dt \approx 23{,}69$ GE

{% include info.html
index="4"
frage="Die Funktion $u(t)=(16{,}2t^2+11)\cdot e^{-0{,}7t}+5$ gibt den jährlichen Umsatz an. Der Produktlebenszyklus endet nach 11 Jahren. Bestimme (a) den Gesamtumsatz, (b) den jährlichen Umsatz nach 8 Jahren, (c) den durchschnittlichen jährlichen Umsatz in den ersten 7 Jahren, (d) den Umsatz vom Ende des 3. bis zum Ende des 9. Jahres."
antwort="

**(a) Gesamtumsatz:**

$$\int_0^{11} u(t)\,dt \approx 163{,}53 \text{ GE (TR)}$$

**(b) Jährlicher Umsatz nach 8 Jahren:**

$$u(8)=(16{,}2\cdot 64+11)\cdot e^{-5{,}6}+5 \approx 8{,}87 \text{ GE}$$

**(c) Durchschnittlicher jährlicher Umsatz (erste 7 Jahre):**

$$\bar{u}=\frac{1}{7}\int_0^7 u(t)\,dt \approx 18{,}92 \text{ GE (TR)}$$

**(d) Umsatz vom Ende des 3. bis zum Ende des 9. Jahres:**

$$\int_3^9 u(t)\,dt \approx 88{,}55 \text{ GE (TR)}$$

**Hinweis:** Die Berechnung der Integrale bei Produktlebenszyklusfunktionen erfolgt mit dem Taschenrechner (TR), da keine elementare Stammfunktion existiert.

"
%}

## Der EKG-Zyklus

Beim **EKG-Zyklus** (**E**rlös – **K**osten – **G**ewinn) werden neben der Erlösfunktion $E(t)$ auch die Kostenfunktion $K(t)$ und die daraus resultierende Gewinnfunktion

$$G(t)=E(t)-K(t)$$

betrachtet.

### Typische Funktionsformen

$$
\begin{align*}
E(t) &= p(t)\cdot e^{-ct} &&\text{(Erlöse)}\\
K(t) &= q(t)\cdot e^{-ct}+K_f &&\text{(variable Kosten + Fixkosten)}
\end{align*}
$$

Dabei gilt:
- $E(0)=0$: Zu Beginn werden keine Erlöse erzielt.
- $K(0)=K_f > 0$: Von Beginn an fallen **Fixkosten** an.
- Daraus folgt: $G(0) = -K_f < 0$, d.h. zu Beginn entstehen **Verluste**.

### Kennzahlen des EKG-Zyklus

**Zeitraum der Kostendeckung:** Die Kosten werden gedeckt, solange $G(t) \geq 0$ gilt, also

$$E(t) \geq K(t) \quad\Leftrightarrow\quad G(t) \geq 0$$

Die Grenzen $t_1$ und $t_2$ dieses Zeitraums bestimmt man durch $G(t)=0$ (TR).

**Gesamtgewinn** während des Produktlebenszyklus:

$$G_{\text{gesamt}}=\int_0^T G(t)\,dt = \int_0^T \big(E(t)-K(t)\big)\,dt$$

**Maximaler Gesamtverlust:** Der Gesamtverlust ist der kumulierte Verlust seit der Produkteinführung:

$$V(t) = -\int_0^t G(s)\,ds$$

Der maximale Gesamtverlust tritt dort auf, wo $V(t)$ maximal ist.

**Typischer Verlauf:** Da $G(0)=-K_f < 0$, startet die Gewinnfunktion im negativen Bereich. Typischerweise hat $G(t)$ zwei positive Nullstellen $t_1$ und $t_2$:

- Für $0 \leq t < t_1$: $G(t)<0$ → Verluste, $V(t)$ steigt
- Für $t_1 < t < t_2$: $G(t)>0$ → Gewinne, $V(t)$ sinkt
- Für $t > t_2$: $G(t)<0$ → erneut Verluste, $V(t)$ steigt wieder

Damit gibt es **zwei Kandidaten** für den maximalen Gesamtverlust:

$$V(t_1) = -\int_0^{t_1} G(t)\,dt \qquad\text{und}\qquad V(T) = -\int_0^{T} G(t)\,dt$$

Der maximale Gesamtverlust ist:

$$V_{\max} = \max\big(V(t_1),\; V(T)\big)$$

Falls die Kosten **nie** gedeckt werden ($G(t)<0$ für alle $t$), gibt es keine Gewinnphase und der maximale Gesamtverlust liegt am Ende des Lebenszyklus: $V_{\max} = V(T)$.

Das folgende Diagramm zeigt den typischen Verlauf am Beispiel der Gewinnfunktion $G(t)=(-0{,}4t^3+11t^2)\cdot e^{-0{,}2t}-36{,}5$:

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

- **Rote Fläche links** ($0$ bis $t_1$): Anfangsverluste – $V(t_1)$ entspricht dieser Fläche.
- **Grüne Fläche** ($t_1$ bis $t_2$): Gewinnphase – reduziert den kumulierten Verlust.
- **Rote Fläche rechts** ($t_2$ bis $T$): Erneute Verluste am Ende des Lebenszyklus.

Falls die grüne Fläche größer ist als die rechte rote Fläche, gilt $V(t_1) > V(T)$ und der maximale Gesamtverlust liegt bei $t_1$. Andernfalls liegt er am Ende des Lebenszyklus.

{% include info.html
index="5"
frage="Die Funktionen $E(t)=(-0{,}8t^3+22t^2)\cdot e^{-0{,}2t}$ und $K(t)=(-0{,}4t^3+11t^2)\cdot e^{-0{,}2t}+36{,}5$ geben den jährlichen Erlös und die jährlichen Kosten an. Der Lebenszyklus endet nach 27,5 Jahren. Bestimme (a) den Zeitraum der Kostendeckung, (b) die jährlichen Gewinne nach 16 Jahren, (c) den Gesamtgewinn, (d) den Zeitpunkt des maximalen Gesamtverlusts."
antwort="

**Gewinnfunktion:**

$$
\begin{align*}
G(t) &= E(t)-K(t)\\
&= (-0{,}8t^3+22t^2)\cdot e^{-0{,}2t} - \big((-0{,}4t^3+11t^2)\cdot e^{-0{,}2t}+36{,}5\big)\\
&= (-0{,}4t^3+11t^2)\cdot e^{-0{,}2t} - 36{,}5
\end{align*}
$$

**(a) Zeitraum der Kostendeckung:** Löse $G(t)=0$ (TR):

$$(-0{,}4t^3+11t^2)\cdot e^{-0{,}2t} = 36{,}5$$

$$t_1 \approx 2{,}43 \quad t_2 \approx 17{,}57$$

Die Kosten werden im Zeitraum $[2{,}43;\; 17{,}57]$ gedeckt.

**(b) Jährliche Gewinne nach 16 Jahren:**

$$G(16) = (-0{,}4\cdot 4096+11\cdot 256)\cdot e^{-3{,}2} - 36{,}5 \approx 11{,}50 \text{ GE}$$

**(c) Gesamtgewinn:**

$$G_{\text{gesamt}} = \int_0^{27{,}5} G(t)\,dt \approx 305{,}76 \text{ GE (TR)}$$

**(d) Maximaler Gesamtverlust:** Wir vergleichen die beiden Kandidaten:

**Kandidat 1** – erste Nullstelle $t_1 \approx 2{,}43$:

$$V(t_1) = -\int_0^{2{,}43} G(t)\,dt \approx 73{,}24 \text{ GE (TR)}$$

**Kandidat 2** – Ende des Lebenszyklus $T = 27{,}5$:

$$V(T) = -\int_0^{27{,}5} G(t)\,dt = -G_{\text{gesamt}} \approx -305{,}76 \text{ GE}$$

Da $V(T) < 0$ (am Ende liegt ein Nettogewinn vor), ist $V(t_1) > V(T)$.

Der maximale Gesamtverlust beträgt ca. $73{,}24$ GE und tritt nach ca. $2{,}43$ Jahren auf.

"
%}
