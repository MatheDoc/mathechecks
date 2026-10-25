---
layout: module
title: "Konsumentenrente und Produzentenrente erklärt – mit Beispielen"
description: "Marktgleichgewicht mit nichtlinearen Funktionen, Konsumentenrente und Produzentenrente graphisch und rechnerisch, Abschöpfung der Konsumentenrente durch einen Teilmarkt – mit Beispielen."
page_context: Lernbereich
nav: dashboard
body_class: page-module
module_key: skript
published: true
lernbereich: marktgleichgewicht-vertiefung
gebiet: analysis
permalink: /lernbereiche/analysis/marktgleichgewicht-vertiefung/skript.html
---

# Konsumentenrente und Produzentenrente am Marktgleichgewicht

Ein Marktforschungsinstitut beschreibt den Markt für Fahrradhelme in einer Region durch die Nachfragefunktion $p_N$ und die Angebotsfunktion $p_A$ mit

$$
\begin{align*}
p_N(x)&=45{,}75e^{-0{,}044x}-6{,}75\\
p_A(x)&=0{,}016x^2+0{,}022x+6.
\end{align*}
$$

Dabei ist $x$ die Menge in Mengeneinheiten (ME, 1 ME = 100 Helme) und $p_N(x)$ bzw. $p_A(x)$ der Preis in Geldeinheiten pro Mengeneinheit (GE/ME, 1 GE = 1000 €). Dieses Leitbeispiel begleitet uns durch das ganze Skript.

$p_N(x)$ ist der Preis, zu dem die Konsumenten insgesamt $x$ ME nachfragen. Je niedriger der Preis, desto mehr wird nachgefragt: $p_N$ ist monoton fallend. $p_A(x)$ ist der Preis, zu dem die Produzenten insgesamt $x$ ME anbieten. Je höher der Preis, desto mehr wird angeboten: $p_A$ ist monoton steigend. Anders als im Lernbereich [Marktgleichgewicht – Grundlagen](../marktgleichgewicht-grundlagen/skript.html) sind die Funktionen hier nicht linear, sondern zum Beispiel quadratisch oder exponentiell.

## Marktgleichgewicht bei nichtlinearen Funktionen

### Kennzahlen graphisch bestimmen

Im Diagramm des Leitbeispiels lesen wir die Kennzahlen ab:

- **Höchstpreis:** $y$-Achsenabschnitt von $p_N$, hier $39$ GE/ME. Zu diesem oder einem höheren Preis kauft niemand.
- **Sättigungsmenge:** Nullstelle von $p_N$, hier etwa $43{,}5$ ME. So viel würde selbst zum Preis $0$ GE/ME höchstens nachgefragt.
- **Mindestangebotspreis:** $y$-Achsenabschnitt von $p_A$, hier $6$ GE/ME. Erst über diesem Preis bieten die Produzenten an.
- **Marktgleichgewicht:** Schnittpunkt der beiden Graphen, hier etwa $(19{,}6\mid 12{,}6)$. Die **Gleichgewichtsmenge** $x_G\approx 19{,}6$ ME wird zum **Gleichgewichtspreis** $p_G\approx 12{,}6$ GE/ME gehandelt.
- **Umsatz im Marktgleichgewicht:** $x_G\cdot p_G\approx 19{,}6\cdot 12{,}6\approx 247$ GE. Graphisch ist das die Fläche des Rechtecks mit den Seitenlängen $x_G$ und $p_G$.

{% include graph.html
   funktionen='[
    {"name":"p<sub>N</sub>(x)", "term":"45.75*exp(-0.044*x)-6.75", "beschreibung":"Nachfragefunktion", "color":"#1f77b4"},
    {"name":"p<sub>A</sub>(x)", "term":"0.016*x^2+0.022*x+6", "beschreibung":"Angebotsfunktion", "color":"#d62728"}
   ]'
   flaechen='[
    {"term":"12.5715", "von":0, "bis":19.5903, "farbe":"rgba(120,120,120,0.25)", "name":"Umsatz im Marktgleichgewicht"}
   ]'
   punkte='[
    {"x":0,"y":39,"text":"Höchstpreis"},
    {"x":0,"y":6,"text":"Mindestangebotspreis"},
    {"x":19.5903,"y":12.5715,"text":"Marktgleichgewicht"},
    {"x":43.4920,"y":0,"text":"Sättigungsmenge"}
   ]'
   titel="Markt für Fahrradhelme"
   xachse="Menge x in ME"
   yachse="Preis p in GE/ME"
   xmin=0
   xmax=46
   ymin=0
   ymax=42
%}

Typische Fehler: Höchstpreis und Sättigungsmenge gehören zur Nachfragefunktion, der Mindestangebotspreis zur Angebotsfunktion. Der Umsatz ist die Rechteckfläche $x_G\cdot p_G$, nicht die Fläche unter einem der Graphen.

{% include check-anker.html nummer="1" %}

### Kennzahlen berechnen

Rechnerisch übersetzen wir jede Kennzahl in einen Funktionswert oder eine Gleichung:

- **Höchstpreis:** $p_N(0)=45{,}75-6{,}75=39$ GE/ME. **Mindestangebotspreis:** $p_A(0)=6$ GE/ME.
- **Sättigungsmenge:** $p_N(x)=0 \Leftrightarrow e^{-0{,}044x}=\frac{6{,}75}{45{,}75} \Leftrightarrow x=\frac{1}{0{,}044}\ln\left(\frac{45{,}75}{6{,}75}\right)\approx 43{,}49$ ME.
- **Marktgleichgewicht:** $p_N(x)=p_A(x)$. Eine Gleichung mit $e$-Funktion und Polynom lässt sich nicht von Hand umformen, wir lösen sie mit dem CAS: $x_G\approx 19{,}59$ ME. Den Gleichgewichtspreis liefert eine der beiden Funktionen: $p_G=p_N(19{,}59)\approx 12{,}57$ GE/ME.
- **Umsatz im Marktgleichgewicht:** $x_G\cdot p_G\approx 19{,}5903\cdot 12{,}5715\approx 246{,}28$ GE, also etwa 246 280 €.

Bei nichtlinearen Funktionen liefert das CAS oft mehrere Lösungen. Ökonomisch sinnvoll sind nur Lösungen mit $x\geq 0$, bei denen auch die Preise nicht negativ sind. Eine negative Lösung wird mit dem Hinweis „nicht im ökonomischen Definitionsbereich“ verworfen.

**Staatlich festgelegter Preis.** Wird der Preis nicht vom Markt bestimmt, sondern zum Beispiel auf $10$ GE/ME festgelegt, so passen Angebot und Nachfrage nicht mehr zusammen. Wir berechnen beide Mengen:

$$
\begin{align*}
p_N(x)=10 &\Rightarrow x_N\approx 22{,}84\\
p_A(x)=10 &\Rightarrow x_A\approx 15{,}14 \quad (x\approx -16{,}51 \text{ entfällt})
\end{align*}
$$

Es werden $22{,}84$ ME nachgefragt, aber nur $15{,}14$ ME angeboten: Es besteht ein **Nachfrageüberschuss** von $22{,}84-15{,}14=7{,}70$ ME. Allgemein gilt: Liegt der festgelegte Preis unter $p_G$, entsteht ein Nachfrageüberschuss, liegt er über $p_G$, ein **Angebotsüberschuss**.

{% include check-anker.html nummer="2" %}

## Konsumenten- und Produzentenrente

### Idee an einem kleinen Markt

Bevor wir mit Funktionen rechnen, betrachten wir einen kleinen Markt mit vier Konsumenten und vier Produzenten. Jeder Konsument möchte einen Helm kaufen, jeder Produzent einen Helm verkaufen. Der Marktpreis beträgt $30$ €.

| Konsument | Zahlungsbereitschaft | individuelle Konsumentenrente |
| --------- | -------------------- | ----------------------------- |
| Anton     | $60$ €               | $60-30=30$ €                  |
| Berta     | $45$ €               | $45-30=15$ €                  |
| Cem       | $35$ €               | $35-30=5$ €                   |
| Daria     | $25$ €               | kauft nicht                   |

Anton wäre bereit gewesen, $60$ € zu zahlen, zahlt aber nur $30$ €. Er spart $30$ €. Die **Konsumentenrente** $KR$ ist die Summe dieser Ersparnisse:

$$
KR=30+15+5=50 \text{ €}.
$$

Gleichwertig ist: gesamte Zahlungsbereitschaft der Käufer minus ihre Ausgaben, also $(60+45+35)-3\cdot 30=140-90=50$ €.

| Produzent | Angebotsbereitschaft | individuelle Produzentenrente |
| --------- | -------------------- | ----------------------------- |
| Alpha     | $15$ €               | $30-15=15$ €                  |
| Beta      | $20$ €               | $30-20=10$ €                  |
| Gamma     | $28$ €               | $30-28=2$ €                   |
| Delta     | $40$ €               | verkauft nicht                |

Alpha hätte schon für $15$ € verkauft, erhält aber $30$ €. Die **Produzentenrente** $PR$ ist die Summe dieser Mehreinnahmen:

$$
PR=15+10+2=27 \text{ €}.
$$

Gleichwertig ist: Umsatz minus gesamte Angebotsbereitschaft der Verkäufer, also $3\cdot 30-(15+20+28)=90-63=27$ €.

Bei diesem Preis werden drei Helme gekauft und drei verkauft: Der Markt ist im Gleichgewicht.

### Von der Summe zum Integral

Auf einem großen Markt gibt $p_N(x)$ an, welcher Preis für die „$x$-te“ Mengeneinheit gerade noch gezahlt würde. Summieren wir diese Zahlungsbereitschaften über alle Einheiten von $0$ bis $x_G$, erhalten wir ein Integral. Ebenso gibt $p_A(x)$ an, zu welchem Preis die $x$-te Einheit gerade noch angeboten würde.

| Term | Bedeutung | Fläche im Diagramm |
| ---- | --------- | ------------------ |
| $\int_0^{x_G}p_N(x)\,dx$ | Zahlungsbereitschaft der Konsumenten | unter dem Graphen von $p_N$ über $[0;x_G]$ |
| $\int_0^{x_G}p_A(x)\,dx$ | Angebotsbereitschaft der Produzenten | unter dem Graphen von $p_A$ über $[0;x_G]$ |
| $x_G\cdot p_G$ | Umsatz im Marktgleichgewicht | Rechteck mit den Seiten $x_G$ und $p_G$ |

Damit übertragen wir die beiden Definitionen vom kleinen Markt:

$$
\begin{align*}
KR&=\underbrace{\int_0^{x_G}p_N(x)\,dx}_{\text{Zahlungsbereitschaft}}-\underbrace{x_G\cdot p_G}_{\text{Umsatz}}=\int_0^{x_G}\left(p_N(x)-p_G\right)dx\\
PR&=\underbrace{x_G\cdot p_G}_{\text{Umsatz}}-\underbrace{\int_0^{x_G}p_A(x)\,dx}_{\text{Angebotsbereitschaft}}=\int_0^{x_G}\left(p_G-p_A(x)\right)dx
\end{align*}
$$

Die rechte Form entsteht, weil $x_G\cdot p_G=\int_0^{x_G}p_G\,dx$ gilt. Beide Formen kommen in Abituraufgaben vor.

### Renten graphisch deuten und abschätzen

Die Konsumentenrente ist die Fläche zwischen dem Graphen von $p_N$ und der waagerechten Geraden $p=p_G$ über $[0;x_G]$. Die Produzentenrente ist die Fläche zwischen der Geraden $p=p_G$ und dem Graphen von $p_A$ über $[0;x_G]$.

{% include graph.html
   funktionen='[
    {"name":"p<sub>N</sub>(x)", "term":"45.75*exp(-0.044*x)-6.75", "beschreibung":"Nachfragefunktion", "color":"#1f77b4"},
    {"name":"p<sub>A</sub>(x)", "term":"0.016*x^2+0.022*x+6", "beschreibung":"Angebotsfunktion", "color":"#d62728"}
   ]'
   flaechen='[
    {"term":"45.75*exp(-0.044*x)-6.75", "von":0, "bis":19.5903, "basis":12.5715, "farbe":"rgba(31,119,180,0.3)", "name":"Konsumentenrente (KR)"},
    {"term":"0.016*x^2+0.022*x+6", "von":0, "bis":19.5903, "basis":12.5715, "farbe":"rgba(214,39,40,0.3)", "name":"Produzentenrente (PR)"}
   ]'
   hilfslinien='[
    {"x":19.5903,"y":12.5715}
   ]'
   titel="Konsumenten- und Produzentenrente"
   xachse="Menge x in ME"
   yachse="Preis p in GE/ME"
   xmin=0
   xmax=30
   ymin=0
   ymax=42
   xdtick=2
   ydtick=2
%}

**Abschätzen durch Kästchenzählen.** Ein Kästchen ist $2$ ME breit und $2$ GE/ME hoch, es steht also für $2\cdot 2=4$ GE. Die blaue Fläche umfasst etwa $55$ Kästchen, also $KR\approx 55\cdot 4=220$ GE. Die rote Fläche umfasst etwa $21$ Kästchen, also $PR\approx 21\cdot 4=84$ GE. Schon ohne Rechnung sehen wir: Die Konsumentenrente ist mehr als doppelt so groß wie die Produzentenrente.

Typische Fehler:

- Die Fläche bis zur $x$-Achse statt bis zur Geraden $p=p_G$ zählen. Das ergibt die Zahlungsbereitschaft bzw. die Angebotsbereitschaft, nicht die Rente.
- Bis zur Sättigungsmenge statt bis $x_G$ zählen.
- Ein Kästchen mit $1$ GE ansetzen, statt Breite mal Höhe zu rechnen.

{% include check-anker.html nummer="3" %}

### Renten berechnen und deuten

Im Leitbeispiel berechnen wir die Integrale mit dem CAS und verwenden dabei die ungerundeten Werte $x_G$ und $p_G$:

$$
\begin{align*}
KR&=\int_0^{x_G}p_N(x)\,dx-x_G\cdot p_G\approx 468{,}41-246{,}28=222{,}13\\
PR&=x_G\cdot p_G-\int_0^{x_G}p_A(x)\,dx\approx 246{,}28-161{,}86=84{,}42
\end{align*}
$$

Die Schätzungen aus dem Diagramm ($220$ GE und $84$ GE) werden bestätigt.

**Deutung im Sachzusammenhang.** Die Konsumentenrente beträgt etwa $222{,}13$ GE, also etwa 222 130 €. Diesen Betrag sparen die Konsumenten, die bereit gewesen wären, mehr als den Gleichgewichtspreis von $12{,}57$ GE/ME zu zahlen. Die Produzentenrente beträgt etwa $84{,}42$ GE. Diesen Betrag nehmen die Produzenten mehr ein, die auch zu einem niedrigeren Preis als $12{,}57$ GE/ME angeboten hätten.

**Terme erkennen.** In Aufgaben ohne Hilfsmittel wird oft ein Term vorgegeben, dessen Bedeutung zu benennen ist. Ein Term der Form „Integral über $p_N$ von $0$ bis $x_G$ minus $x_G\cdot p_G$“ ist die Konsumentenrente. „$x_G\cdot p_G$ minus Integral über $p_A$“ ist die Produzentenrente.

Typische Fehler: den Umsatz nicht abziehen, bis zur Sättigungsmenge integrieren oder mit stark gerundeten Gleichgewichtswerten rechnen.

{% include check-anker.html nummer="4" %}

## Abschöpfung der Konsumentenrente

Die Konsumentenrente ist Geld, das die Konsumenten zu zahlen bereit wären, aber nicht zahlen müssen. Ein Anbieter kann versuchen, einen Teil davon zu erhalten. Er bildet dazu einen **Teilmarkt** mit höherem Preis, zum Beispiel durch einen früheren Verkaufsstart oder eine Premium-Ausführung. Man spricht von **Preisdifferenzierung**.

Im Leitbeispiel werden die Helme zunächst auf einem Teilmarkt für $p_2=20$ GE/ME angeboten. Dort kaufen alle, deren Zahlungsbereitschaft mindestens $20$ GE/ME beträgt:

$$
p_N(x_2)=20 \Rightarrow x_2\approx 12{,}20 \text{ ME}.
$$

Die übrigen Konsumenten bis zur Gleichgewichtsmenge kaufen danach zum Gleichgewichtspreis $p_G$. Die ersten $x_2$ ME werden also um $p_2-p_G$ teurer verkauft. Der **abgeschöpfte Betrag** ist das grau schraffierte Rechteck:

$$
x_2\cdot(p_2-p_G)\approx 12{,}1968\cdot(20-12{,}5715)\approx 90{,}60 \text{ GE}.
$$

Dieser Betrag geht von den Konsumenten an die Produzenten. Den Konsumenten bleibt nur noch die Konsumentenrente $KR_1+KR_2\approx 222{,}13-90{,}60=131{,}53$ GE.

{% include graph.html
   funktionen='[
    {"name":"p<sub>N</sub>(x)", "term":"45.75*exp(-0.044*x)-6.75", "beschreibung":"Nachfragefunktion", "color":"#1f77b4"},
    {"name":"p<sub>A</sub>(x)", "term":"0.016*x^2+0.022*x+6", "beschreibung":"Angebotsfunktion", "color":"#d62728"}
   ]'
   flaechen='[
    {"term":"45.75*exp(-0.044*x)-6.75", "von":0, "bis":12.1968, "basis":20, "farbe":"rgba(59,130,246,0.25)", "name":"KR<sub>2</sub>"},
    {"term":"45.75*exp(-0.044*x)-6.75", "von":12.1968, "bis":19.5903, "basis":12.5715, "farbe":"rgba(16,185,129,0.25)", "name":"KR<sub>1</sub>"},
    {"term":"20", "von":0, "bis":12.1968, "basis":12.5715, "farbe":"rgba(120,120,120,0.6)", "schraffur":true, "name":"abgeschöpfter Betrag"}
   ]'
   hilfslinien='[
    {"x":12.1968,"y":20,"xLabel":"x<sub>2</sub>"},
    {"x":19.5903,"y":12.5715,"xLabel":"x<sub>G</sub>","yLabel":"p<sub>G</sub>"}
   ]'
   titel="Preisdifferenzierung: Abschöpfung der Konsumentenrente"
   xachse="Menge x in ME"
   yachse="Preis p in GE/ME"
   xmin=0
   xmax=30
   ymin=0
   ymax=42
%}

### Maximale Abschöpfung

Bei welchem Teilmarktpreis wird möglichst viel abgeschöpft? Ein hoher Preis $p_2$ ergibt ein hohes, aber schmales Rechteck, weil nur wenige so viel zahlen. Ein niedriger Preis ergibt ein breites, aber flaches Rechteck. Im Widget kannst du $x_2$ verschieben und den abgeschöpften Betrag beobachten:

{% include widgets/widget-abschoepfung.html
   id="abschoepfung"
   term_n="45.75*exp(-0.044*x)-6.75"
   term_a="0.016*x^2+0.022*x+6"
   xmax=40
   ymax=42
   start_x2=12.1968
   xachse="Menge x in ME"
   yachse="Preis p in GE/ME"
%}

Da $p_2=p_N(x_2)$ gilt, hängt der abgeschöpfte Betrag nur von $x_2$ ab. Wir erhalten die **Zielfunktion**

$$
A(x_2)=x_2\cdot\left(p_N(x_2)-p_G\right).
$$

$A(x_2)$ ist die Rechteckfläche: Breite $x_2$ mal Höhe $p_N(x_2)-p_G$. Für $x_2=0$ und für $x_2=x_G$ ist $A=0$, dazwischen liegt das Maximum. Im Leitbeispiel ist

$$
A(x_2)=x_2\cdot\left(45{,}75e^{-0{,}044x_2}-6{,}75-12{,}57\right).
$$

Mit dem CAS lösen wir die notwendige Bedingung $A'(x_2)=0$ und erhalten $x_2\approx 8{,}67$. Wegen $A''(8{,}67)\approx -2{,}22<0$ liegt ein Maximum vor. Der zugehörige Teilmarktpreis ist $p_2=p_N(8{,}67)\approx 24{,}49$ GE/ME, und es werden $A(8{,}67)\approx 103{,}34$ GE abgeschöpft.

**Deutung:** Bietet der Anbieter auf einem Teilmarkt $8{,}67$ ME zum Preis von $24{,}49$ GE/ME an, so schöpft er mit diesem einen Teilmarkt die Konsumentenrente maximal ab, nämlich um etwa $103{,}34$ GE. Weitere Teilmärkte würden noch mehr abschöpfen. Im Abitur heißt die Zielfunktion oft anders, zum Beispiel $h(x)=x\cdot(p_N(x)-p_G)$, und gesucht ist der zugehörige Punkt $P(x_2\mid p_2)$ auf dem Graphen von $p_N$.

Typische Fehler: $p_A$ statt $p_N$ einsetzen, $p_G$ nicht abziehen, oder $x_2$ als Ergebnis angeben, obwohl nach dem Preis $p_2$ gefragt ist.

{% include check-anker.html nummer="5" %}
