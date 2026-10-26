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

Ein neuer Fahrradhelm kostet im Laden etwa 125 €. Viele Kunden hätten für ihren Helm aber deutlich mehr bezahlt, andere hätten ihn nur zu einem geringeren Preis angeboten. Wer profitiert also davon, dass sich ein einheitlicher Marktpreis bildet, und um wie viel? Um diese Frage zu beantworten, beschreibt ein Marktforschungsinstitut den Markt für Fahrradhelme in einer Region durch die Nachfragefunktion $p_N$ und die Angebotsfunktion $p_A$ mit

$$
\begin{align*}
p_N(x)&=45{,}75e^{-0{,}044x}-6{,}75\\
p_A(x)&=0{,}016x^2+0{,}022x+6.
\end{align*}
$$

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

Dabei ist $x$ die Menge in Mengeneinheiten (ME, 1 ME = 100 Helme) und $p_N(x)$ bzw. $p_A(x)$ der Preis in Geldeinheiten pro Mengeneinheit (GE/ME, 1 GE = 1000 €).

$p_N(x)$ ist der Preis, zu dem die Konsumenten insgesamt $x$ ME nachfragen. Je niedriger der Preis, desto mehr wird nachgefragt: $p_N$ ist monoton fallend. $p_A(x)$ ist der Preis, zu dem die Produzenten insgesamt $x$ ME anbieten. Je höher der Preis, desto mehr wird angeboten: $p_A$ ist monoton steigend. Anders als im Lernbereich [Marktgleichgewicht – Grundlagen](../marktgleichgewicht-grundlagen/skript.html) sind die Funktionen hier nicht linear, sondern zum Beispiel quadratisch oder exponentiell.

## Marktgleichgewicht bei nichtlinearen Funktionen

### Kennzahlen graphisch bestimmen

Die Kennzahlen des Marktes sind besondere Punkte der beiden Graphen. Im Diagramm des Leitbeispiels sind sie markiert:

- **Höchstpreis** ($y$-Achsenabschnitt von $p_N$): Zu diesem oder einem höheren Preis kauft niemand mehr einen Helm.
- **Sättigungsmenge** (Nullstelle von $p_N$): Mehr Helme würden selbst dann nicht nachgefragt, wenn sie verschenkt würden.
- **Mindestangebotspreis** ($y$-Achsenabschnitt von $p_A$): Erst über diesem Preis bieten die Produzenten überhaupt Helme an.
- **Marktgleichgewicht** (Schnittpunkt der Graphen): Hier stimmen angebotene und nachgefragte Menge überein. Seine Koordinaten sind die **Gleichgewichtsmenge** $x_G$ und der **Gleichgewichtspreis** $p_G$.
- **Umsatz im Marktgleichgewicht** $x_G\cdot p_G$: Das ist der Betrag, den die Konsumenten insgesamt bezahlen. Graphisch ist er die Fläche des grauen Rechtecks mit den Seitenlängen $x_G$ und $p_G$.



Typische Fehler: Höchstpreis und Sättigungsmenge gehören zur Nachfragefunktion, der Mindestangebotspreis zur Angebotsfunktion. Beim Ablesen des Marktgleichgewichts werden $x$- und $y$-Koordinate vertauscht. Der Umsatz ist die Rechteckfläche $x_G\cdot p_G$, nicht die Fläche unter einem der Graphen.

Warum wird der Graph von $p_N$ nach rechts immer flacher? Bei hohen Preisen kaufen nur wenige, die unbedingt einen Helm wollen; eine kleine Preissenkung gewinnt kaum neue Käufer. Bei niedrigen Preisen dagegen reicht schon eine kleine Preissenkung, damit viele zusätzliche Kunden zugreifen, die Menge wächst stark. Eine lineare Nachfragefunktion kann dieses Verhalten nicht abbilden.

{% include check-anker.html nummer="1" %}

### Kennzahlen berechnen

Rechnerisch wird jeder markierte Punkt zu einem Funktionswert oder einer Gleichung: Achsenabschnitte sind Funktionswerte an der Stelle $0$, die Sättigungsmenge ist eine Nullstelle, das Marktgleichgewicht ein Schnittpunkt. Neu gegenüber linearen Funktionen ist zweierlei:

- Gleichungen wie $45{,}75e^{-0{,}044x}-6{,}75=0{,}016x^2+0{,}022x+6$ lassen sich nicht von Hand nach $x$ auflösen. Wir lösen sie mit dem CAS.
- Das CAS liefert eventuell mehrere Lösungen. Ökonomisch sinnvoll sind nur Mengen $x\geq 0$, zu denen auch die Preise nicht negativ sind. Andere Lösungen werden mit dem Hinweis „nicht im ökonomischen Definitionsbereich“ verworfen.

Mit Zwischenergebnissen wie $x_G$ und $p_G$ rechnen wir ungerundet weiter, sonst weicht zum Beispiel der Umsatz $x_G\cdot p_G$ merklich ab.

**Staatlich festgelegter Preis.** Legt der Staat einen Preis fest, der vom Gleichgewichtspreis abweicht, passen Angebot und Nachfrage nicht mehr zusammen. Im Diagramm schneidet die waagerechte Gerade zum festgelegten Preis die beiden Graphen an verschiedenen Stellen: Bei $x_A$ den Graphen von $p_A$ (angebotene Menge), bei $x_N$ den Graphen von $p_N$ (nachgefragte Menge).

{% include graph.html
   funktionen='[
    {"name":"p<sub>N</sub>(x)", "term":"45.75*exp(-0.044*x)-6.75", "beschreibung":"Nachfragefunktion", "color":"#1f77b4"},
    {"name":"p<sub>A</sub>(x)", "term":"0.016*x^2+0.022*x+6", "beschreibung":"Angebotsfunktion", "color":"#d62728"},
    {"name":"p = 10", "term":"10", "beschreibung":"festgelegter Preis", "color":"#6b7280", "dash":"dash"}
   ]'
   hilfslinien='[
    {"x":15.1388,"y":10,"xLabel":"x<sub>A</sub>"},
    {"x":22.8362,"y":10,"xLabel":"x<sub>N</sub>"}
   ]'
   titel="Festgelegter Preis unter dem Gleichgewichtspreis"
   xachse="Menge x in ME"
   yachse="Preis p in GE/ME"
   xmin=0
   xmax=46
   ymin=0
   ymax=42
%}

Im Leitbeispiel liegt der festgelegte Preis von $10$ GE/ME unter dem Gleichgewichtspreis. Zu diesem günstigen Preis wollen mehr Konsumenten kaufen, als Produzenten anbieten: $x_N>x_A$, es besteht ein **Nachfrageüberschuss** der Höhe $x_N-x_A$. Liegt der festgelegte Preis über $p_G$, ist es umgekehrt, es entsteht ein **Angebotsüberschuss** $x_A-x_N$.

Typische Fehler: die beiden Mengen in der falschen Funktion bestimmen, die Art des Überschusses vertauschen oder bei $p_A(x)=P$ eine negative Lösung übernehmen.

Aus dem Alltag kennt man beide Fälle: Ein staatlich gedeckelter Preis unter dem Gleichgewichtspreis (z. B. bei Mieten) führt zu Wartelisten, also einem Nachfrageüberschuss. Ein garantierter Mindestpreis über dem Gleichgewichtspreis (z. B. für Agrarprodukte) führt zu Überproduktion, also einem Angebotsüberschuss.

{% include check-anker.html nummer="2" %}

## Konsumenten- und Produzentenrente

### Idee an einem kleinen Markt

Bevor wir mit Funktionen rechnen, betrachten wir einen kleinen Markt mit vier Konsumenten und vier Produzenten. Jeder Konsument möchte einen Helm kaufen, jeder Produzent einen Helm verkaufen. Der Marktpreis beträgt $30$ €. Überlege kurz, bevor du weiterliest: Wer profitiert in den Tabellen am meisten von diesem Preis, und wer gar nicht?

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

Bei diesem Preis werden drei Helme gekauft und drei verkauft: Der Markt ist im Gleichgewicht. Am meisten profitieren Anton und Alpha, deren Bereitschaft am weitesten vom Marktpreis entfernt ist. Daria und Delta gehen leer aus: Daria hätte durchaus etwas bezahlt, nur nicht $30$ €, und Delta hätte durchaus verkauft, nur nicht so billig.

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

Die rechte Form entsteht, weil $x_G\cdot p_G=\int_0^{x_G}p_G\,dx$ gilt.

Ist ein Term mit konkreten Zahlen gegeben, lässt sich seine ökonomische Bedeutung mit der Tabelle erkennen: Ein Produkt aus Gleichgewichtsmenge und Gleichgewichtspreis ist der Umsatz, ein Integral über $p_N$ die Zahlungsbereitschaft, ein Integral über $p_A$ die Angebotsbereitschaft. Die Differenz entscheidet über Konsumenten- oder Produzentenrente.

### Renten graphisch deuten und abschätzen

Die Konsumentenrente ist die Fläche zwischen dem Graphen von $p_N$ und der waagerechten Geraden $p=p_G$ über $[0;x_G]$. Die Produzentenrente ist die Fläche zwischen der Geraden $p=p_G$ und dem Graphen von $p_A$ über $[0;x_G]$.

Schätze nach Augenmaß, bevor du Kästchen zählst: Ist die blaue Fläche mehr als doppelt so groß wie die rote? Sie ist es deutlich, die Konsumenten profitieren im Leitbeispiel also wesentlich stärker vom Marktgleichgewicht als die Produzenten.

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

**Abschätzen durch Kästchenzählen.** Ohne Funktionsterme lassen sich die Renten nur abschätzen. Jedes Kästchen des Gitters steht für einen festen Geldbetrag: Breite in ME mal Höhe in GE/ME, hier $2\cdot 2=4$ GE. Teilweise bedeckte Kästchen werden so zusammengefasst, dass sie sich ungefähr zu vollen Kästchen ergänzen.

Typische Fehler:

- Die Fläche bis zur $x$-Achse statt bis zur Geraden $p=p_G$ zählen. Das ergibt die Zahlungsbereitschaft bzw. die Angebotsbereitschaft, nicht die Rente.
- Bis zur Sättigungsmenge statt bis $x_G$ zählen.
- Ein Kästchen mit $1$ GE ansetzen, statt Breite mal Höhe zu rechnen.

{% include check-anker.html nummer="3" %}

### Renten berechnen und deuten

Sind die Funktionsterme bekannt, berechnen wir die Renten mit den Formeln aus dem Abschnitt „Von der Summe zum Integral“. Zuerst wird das Marktgleichgewicht bestimmt, danach werden die Integrale mit dem CAS ausgewertet, und zwar mit den ungerundeten Werten von $x_G$ und $p_G$. Im Leitbeispiel ergeben sich $KR\approx 222{,}13$ GE und $PR\approx 84{,}42$ GE. Die Schätzung durch Kästchenzählen liegt also schon nahe am exakten Wert.

**Deutung im Sachzusammenhang.** Ein Zahlenwert allein genügt nicht, gefragt ist meist auch seine Bedeutung:

- Die Konsumentenrente ist der Betrag, den die Konsumenten insgesamt sparen, weil sie nur den Gleichgewichtspreis zahlen, obwohl manche von ihnen mehr zu zahlen bereit wären.
- Die Produzentenrente ist der Betrag, den die Produzenten insgesamt zusätzlich einnehmen, weil sie den Gleichgewichtspreis erhalten, obwohl manche von ihnen auch billiger angeboten hätten.

„Die Konsumentenrente ist der Gewinn der Konsumenten.“ Stimmt das? Nur ungenau: Die Konsumenten nehmen kein Geld ein, sie geben weniger aus, als sie zu zahlen bereit wären. Ebenso ist die Produzentenrente nicht der Gewinn der Produzenten, denn Kosten wie Fixkosten werden nicht abgezogen.

Typische Fehler: den Umsatz nicht abziehen, bis zur Sättigungsmenge integrieren oder mit stark gerundeten Gleichgewichtswerten rechnen.

{% include check-anker.html nummer="4" %}

## Abschöpfung der Konsumentenrente

Die Konsumentenrente ist Geld, das die Konsumenten zu zahlen bereit wären, aber nicht zahlen müssen. Ein Anbieter kann versuchen, einen Teil davon zu erhalten. Er bildet dazu einen **Teilmarkt** mit höherem Preis. Man spricht von **Preisdifferenzierung**. Beispiele sind gebundene Bücher, die vor der günstigeren Taschenbuchausgabe erscheinen, oder neue Smartphones, die zum Start teurer sind als einige Monate später.

Im Diagramm verlangt der Anbieter der Fahrradhelme auf dem Teilmarkt den Preis $p_2=20$ GE/ME. Dort kaufen alle, deren Zahlungsbereitschaft mindestens $p_2$ beträgt. Das sind so viele Mengeneinheiten, wie die Nachfragefunktion zum Preis $p_2$ angibt: Die Teilmarktmenge $x_2$ ist die Lösung von $p_N(x_2)=p_2$. Die übrigen Konsumenten bis zur Gleichgewichtsmenge kaufen danach zum Gleichgewichtspreis $p_G$.

Die ersten $x_2$ ME werden also jeweils um $p_2-p_G$ teurer verkauft. Der **abgeschöpfte Betrag** ist das grau schraffierte Rechteck mit der Breite $x_2$ und der Höhe $p_2-p_G$:

$$
\text{abgeschöpfter Betrag}=x_2\cdot(p_2-p_G).
$$

Dieser Betrag geht von den Konsumenten an die Produzenten. Den Konsumenten bleibt nur noch die Konsumentenrente $KR_1+KR_2$: das Flächenstück über dem Rechteck und das Flächenstück rechts davon.

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

Bei welchem Teilmarktpreis wird möglichst viel abgeschöpft? Naheliegend wäre: beim höchsten Preis. Probiere es im Widget aus. Schiebe $x_2$ ganz nach links, dann ganz nach rechts, und beobachte das graue Rechteck und den Betrag $A$. An welcher Stelle ist $A$ am größten, und warum ist das Rechteck an beiden Rändern klein?

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

Links ist der Teilmarktpreis zwar hoch, aber nur wenige zahlen ihn: Das Rechteck ist hoch und schmal. Rechts kaufen viele auf dem Teilmarkt, aber kaum teurer als zum Gleichgewichtspreis: Das Rechteck ist breit und flach. Das Maximum liegt dazwischen, also gerade nicht beim höchsten Preis.

Da $p_2=p_N(x_2)$ gilt, hängt der abgeschöpfte Betrag nur von $x_2$ ab. Wir erhalten die **Zielfunktion**

$$
A(x_2)=x_2\cdot\left(p_N(x_2)-p_G\right).
$$

$A(x_2)$ ist die Rechteckfläche: Breite $x_2$ mal Höhe $p_N(x_2)-p_G$. Für $x_2=0$ und für $x_2=x_G$ ist $A=0$, dazwischen liegt das Maximum. Gesucht ist also ein Hochpunkt von $A$, bestimmt mit notwendiger und hinreichender Bedingung, genau wie beim Maximieren einer Gewinnfunktion. Im Widget zeigt „Maximum zeigen“ den Hochpunkt für das Leitbeispiel.

**Deutung:** Die Maximalstelle $x_2$ gibt an, welche Menge auf dem Teilmarkt verkauft wird, $p_2=p_N(x_2)$ ist der zugehörige Teilmarktpreis und $A(x_2)$ der größtmögliche abgeschöpfte Betrag bei *einem* zusätzlichen Teilmarkt. Weitere Teilmärkte würden noch mehr abschöpfen. Graphisch ist $P(x_2\mid p_2)$ der Punkt auf dem Graphen von $p_N$, der die rechte obere Ecke des größtmöglichen Rechtecks bildet.

Typische Fehler: $p_A$ statt $p_N$ einsetzen, $p_G$ nicht abziehen, oder $x_2$ als Ergebnis angeben, obwohl nach dem Preis $p_2$ gefragt ist.

{% include check-anker.html nummer="5" %}

## Rückblick

Alle Größen dieses Skripts sind Flächen im selben Diagramm: der Umsatz als Rechteck unter dem Gleichgewichtspunkt, die Zahlungs- und Angebotsbereitschaft als Flächen unter den Graphen, die beiden Renten als Flächen zwischen Graph und Gleichgewichtspreis und die Abschöpfung als Rechteck innerhalb der Konsumentenrente. Damit ist auch die Eingangsfrage beantwortet: Vom Marktgleichgewicht profitieren Konsumenten und Produzenten, und wie stark, zeigen die beiden Renten. Denkt man die Preisdifferenzierung weiter, mit immer mehr Teilmärkten, so wird schließlich fast die gesamte Konsumentenrente abgeschöpft.
