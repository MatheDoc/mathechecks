---
layout: module
title: "Ganzrationale ökonomische Funktionen erklärt – Kennzahlen und Berechnungen"
description: "Ganzrationale ökonomische Funktionen erklärt: Preis-Absatz-, Erlös-, Kosten- und Gewinnfunktion im Angebotspolypol und Angebotsmonopol, Kennzahlen graphisch und rechnerisch bestimmen – mit interaktivem Widget und Beispielen."
page_context: Lernbereich
nav: dashboard
body_class: page-module
module_key: skript
published: true
lernbereich: ganzrationale-oekonomische-funktionen
gebiet: analysis
permalink: /lernbereiche/analysis/ganzrationale-oekonomische-funktionen/skript.html
---

# Ganzrationale ökonomische Funktionen: Kennzahlen, Graphen und Berechnungen

## Ökonomische Funktionen

Die Velotec GmbH stellt Fahrradanhänger her. Wie viel nimmt sie ein, wenn sie 500 Anhänger verkauft? Auf dem Markt für Fahrradanhänger gibt es viele Anbieter, ein Anhänger kostet überall etwa 320 €. Velotec kann diesen Preis nicht beeinflussen: Wer teurer ist, verkauft nichts. 500 Anhänger bringen also 500 · 320 € = 160 000 € ein.

In ökonomischen Aufgaben rechnen wir mit **Mengeneinheiten (ME)** und **Geldeinheiten (GE)**. Bei Velotec ist 1 ME = 100 Anhänger und 1 GE = 1 000 €. Die Menge $x$ wird in ME angegeben, Preise in GE/ME und Erlöse, Kosten und Gewinne in GE. Der Preis von 320 € pro Anhänger entspricht 32 GE/ME.

### Preis-Absatz-Funktion

Die **Preis-Absatz-Funktion** $p$ gibt an, zu welchem Preis (in GE/ME) die Menge $x$ abgesetzt wird.

- Im **Angebotspolypol** gibt es viele Anbieter, der Preis wird vom Markt bestimmt. $p$ ist konstant, bei Velotec $p(x)=32$. Man spricht vom **Marktpreis**.
- Im **Angebotsmonopol** gibt es nur einen Anbieter. Er kann den Preis selbst festlegen, aber je höher der Preis, desto weniger wird gekauft. $p$ ist deshalb monoton fallend. In diesem Lernbereich ist $p$ dann linear, zum Beispiel $p(x)=-6x+84$.

### Erlösfunktion

Der **Erlös** ist das, was der Verkauf einbringt: Preis mal Menge.

$$
E(x) = p(x) \cdot x
$$

Für Velotec im Polypol ist $E(x)=32x$, also $E(5)=160$: 5 ME bringen 160 GE ein, das sind die 160 000 € vom Anfang. Im Polypol ist der Graph von $E$ eine Ursprungsgerade, deren Steigung der Marktpreis ist.

### Kostenfunktion

Die **Kostenfunktion** $K$ gibt die Gesamtkosten (in GE) für die Menge $x$ an. Für Velotec gilt

$$
K(x) = 0{,}5x^3 - 6x^2 + 30x + 48.
$$

Der konstante Summand $48$ sind die **Fixkosten**: Miete, Maschinen und Gehälter fallen auch an, wenn kein einziger Anhänger produziert wird. Der übrige Teil sind die variablen Kosten. Mit wachsender Menge steigen die Kosten immer, aber unterschiedlich schnell. Zuerst steigen sie immer langsamer, weil sich Maschinen besser auslasten lassen (**degressiv**). Ab einer bestimmten Menge steigen sie immer schneller, etwa durch Überstunden und Verschleiß (**progressiv**). Diesen Verlauf beschreibt eine ganzrationale Funktion dritten Grades.

### Gewinnfunktion

Der **Gewinn** ist Erlös minus Kosten:

$$
G(x) = E(x) - K(x)
$$

Für Velotec im Polypol ist $G(x) = 32x - (0{,}5x^3 - 6x^2 + 30x + 48) = -0{,}5x^3 + 6x^2 + 2x - 48$. Bei 5 ME bleiben $G(5)=160-110{,}5=49{,}5$ GE Gewinn. Bei 2 ME dagegen ist $G(2)=64-88=-24$: Der Erlös deckt die Kosten nicht, Velotec macht Verlust.

### Velotec wird Monopolist

Velotec entwickelt einen faltbaren Lastenanhänger mit patentierter Kupplung. Niemand sonst darf ihn anbieten, Velotec ist alleinige Anbieterin und legt den Preis selbst fest. Die Marktforschung ergibt die Preis-Absatz-Funktion $p(x)=-6x+84$: Verlangt Velotec 60 GE/ME, also 600 € pro Anhänger, werden 4 ME abgesetzt. Die Produktion läuft auf denselben Anlagen, die Kostenfunktion bleibt gleich.

Im Monopol ist der Erlös kein lineares Produkt mehr, denn der Preis hängt selbst von $x$ ab:

$$
E(x) = (-6x+84)\cdot x = -6x^2+84x, \qquad G(x) = -0{,}5x^3 + 54x - 48.
$$

Der Graph von $E$ ist eine nach unten geöffnete Parabel. Mehr verkaufen bringt also nicht immer mehr Erlös, weil dafür der Preis sinken muss.

### Funktionen aufstellen

Die vier Funktionen hängen über $E(x)=p(x)\cdot x$ und $G(x)=E(x)-K(x)$ zusammen. Sind zwei von ihnen bekannt, lassen sich die beiden anderen bestimmen. Die Gleichungen werden dafür umgestellt, zum Beispiel $K(x)=E(x)-G(x)$ oder $p(x)=\frac{E(x)}{x}$. Nur aus $p$ und $E$ allein lassen sich $K$ und $G$ nicht bestimmen, denn beide enthalten keine Information über die Kosten.

„$K(x)=E(x)+G(x)$.“ Stimmt das? Nein: Aus $G=E-K$ folgt $K=E-G$ und $E=G+K$. Ein zweiter typischer Fehler steckt in der Klammer: Bei $E(x)-K(x)$ wird die *ganze* Kostenfunktion abgezogen, also ändern alle Summanden von $K$ ihr Vorzeichen, auch die Fixkosten.

{% include check-anker.html nummer=1 %}

## Ökonomische Kennzahlen

Wie viele Anhänger muss Velotec mindestens verkaufen, um keinen Verlust zu machen? Bei welcher Menge ist der Gewinn am größten? Solche Fragen beantworten die **ökonomischen Kennzahlen**. Jede Kennzahl ist eine besondere Stelle oder ein besonderer Wert einer der vier Funktionen.

### Preis und Erlös

Diese Kennzahlen hängen von der Marktform ab.

| Kennzahl | Symbol | Bedeutung | mathematisch |
|---|---|---|---|
| Marktpreis (Polypol) | $p$ | Preis, den der Markt vorgibt | konstanter Wert von $p$ |
| Höchstpreis (Monopol) | $p_H$ | Preis, ab dem niemand mehr kauft | $y$-Achsenabschnitt von $p$ |
| Sättigungsmenge (Monopol) | $s_m$ | Menge, die beim Preis null abgesetzt wird | Nullstelle von $p$ |
| erlösmaximale Menge | $x_{Emax}$ | Menge mit dem größten Erlös | Maximalstelle von $E$ (Polypol: Kapazitätsgrenze) |
| maximaler Erlös | $E_{max}$ | größter möglicher Erlös | $E(x_{Emax})$ |

Im Polypol steigt die Erlösgerade immer weiter. Der Erlös wird deshalb bei der größten Menge maximal, die das Unternehmen herstellen kann, der **Kapazitätsgrenze**. Bei Velotec liegt sie bei 13 ME. Im Monopol hat die Erlösparabel dagegen einen echten Hochpunkt.

### Kosten

| Kennzahl | Symbol | Bedeutung | mathematisch |
|---|---|---|---|
| Fixkosten | $K_f$ | mengenunabhängige Kosten | $y$-Achsenabschnitt von $K$ |
| Übergang vom degressiven zum progressiven Kostenwachstum | $x_w$ | Menge, ab der die Kosten immer schneller steigen | Wendestelle von $K$ |

An der Wendestelle ist der Kostenanstieg am kleinsten: Links davon nimmt die Steigung von $K$ ab, rechts davon zu. Weil $K$ in beiden Marktformen gleich ist, liegt $x_w$ bei Velotec im Polypol wie im Monopol bei derselben Menge.

### Gewinn

| Kennzahl | Symbol | Bedeutung | mathematisch |
|---|---|---|---|
| Gewinnschwelle | $x_{GS}$ | Menge, ab der Gewinn erzielt wird | erste positive Nullstelle von $G$ |
| Gewinngrenze | $x_{GG}$ | Menge, bis zu der Gewinn erzielt wird | zweite positive Nullstelle von $G$ |
| gewinnmaximale Menge | $x_{Gmax}$ | Menge mit dem größten Gewinn | Maximalstelle von $G$ |
| maximaler Gewinn | $G_{max}$ | größter möglicher Gewinn | $G(x_{Gmax})$ |
| Break-even-Point | $BEP$ | Punkt, an dem Erlös und Kosten gleich sind | Schnittpunkt von $E$ und $K$ |
| gewinnmaximaler Preis (Monopol) | $p_{max}$ | Preis, zu dem die gewinnmaximale Menge abgesetzt wird | $p(x_{Gmax})$ |
| Cournotscher Punkt (Monopol) | $C$ | gewinnmaximale Menge mit zugehörigem Preis | $C(x_{Gmax}\mid p_{max})$ |

Zwischen Gewinnschwelle und Gewinngrenze liegt die **Gewinnzone**. Gewinnschwelle und Break-even-Point beschreiben dieselbe Stelle: Wo $E(x)=K(x)$ gilt, ist $G(x)=0$.

## Kennzahlen graphisch bestimmen

Im Graphen ist der Gewinn als Abstand zwischen Erlös- und Kostenkurve zu sehen. Das Widget zeigt die vier Funktionen von Velotec. Der Balken bei der eingestellten Menge $x$ verbindet $K(x)$ und $E(x)$. Seine Länge ist der Gewinn, die gestrichelte Linie trägt denselben Wert als $G(x)$ von der $x$-Achse aus ab.

- Bei $x=2$ ist der Balken grau. Woran erkennt man im Graphen, dass Velotec hier Verlust macht?
- Schiebe $x$ nach rechts, bis der Balken verschwindet. Was gilt dort für $G$?
- Bei welcher Menge ist der Balken am längsten? Vergleiche mit dem Hochpunkt von $G$.
- Schalte auf das Angebotsmonopol um. Bei $x=2$ ist der Balken jetzt blau. Warum?
- Liegt im Monopol das Gewinnmaximum an derselben Stelle wie das Erlösmaximum?

{% include widgets/widget-oekonomische-funktionen.html id="of-graphisch" menge=2 fixkosten="false" %}

Ist $K(x)$ größer als $E(x)$, liegt die Kostenkurve über der Erlöskurve und $G(x)$ ist negativ. Wo sich die beiden Kurven schneiden, verschwindet der Abstand: Hier liegen Gewinnschwelle und Gewinngrenze, also die Nullstellen von $G$. Der Gewinn ist maximal, wo die Erlöskurve am weitesten über der Kostenkurve liegt. Diese Stelle ist der Hochpunkt von $G$.

Im Monopol erzielt Velotec schon bei 2 ME Gewinn, weil der Preis dort $p(2)=72$ beträgt und damit weit über dem Marktpreis von 32 liegt. Dafür lässt sich höchstens die Sättigungsmenge von 14 ME absetzen. Insgesamt lohnt sich das Patent: Der maximale Gewinn steigt von etwa 96 GE im Polypol auf 168 GE im Monopol.

„Der Gewinn ist dort am größten, wo der Erlös am größten ist.“ Stimmt das? Nein. Im Monopol liegt das Erlösmaximum bei 7 ME, das Gewinnmaximum aber schon bei 6 ME. Rechts von 6 ME steigen die Kosten stärker als der Erlös, auch wenn der Erlös noch wächst.

Beim Ablesen hilft die Frage, auf welcher Kurve die Kennzahl liegt:

- **auf $p$:** Marktpreis (konstante Höhe), Höchstpreis ($y$-Achsenabschnitt), Sättigungsmenge (Nullstelle)
- **auf $E$:** erlösmaximale Menge und maximaler Erlös (Polypol: rechter Rand an der Kapazitätsgrenze, Monopol: Hochpunkt)
- **auf $K$:** Fixkosten ($y$-Achsenabschnitt), Übergang vom degressiven zum progressiven Kostenwachstum (Wendepunkt)
- **auf $G$:** Gewinnschwelle und Gewinngrenze (Nullstellen), gewinnmaximale Menge und maximaler Gewinn (Hochpunkt)

Bei Mengen gehört die $x$-Koordinate zur Antwort, bei Preisen, Erlösen, Kosten und Gewinnen die $y$-Koordinate. Ein häufiger Fehler ist, beim Hochpunkt von $G$ die falsche Koordinate anzugeben.

{% include check-anker.html nummer=2 %}

## Grenzbetrachtung

Velotec produziert im Polypol gerade 4 ME. Lohnt es sich, noch etwas mehr herzustellen? Das hängt davon ab, ob eine zusätzliche Mengeneinheit mehr einbringt, als sie kostet. Diese Frage beantworten die Ableitungen der ökonomischen Funktionen, die **Grenzfunktionen**:

- **Grenzerlös** $E'(x)$: um wie viel der Erlös ungefähr steigt, wenn eine ME mehr abgesetzt wird
- **Grenzkosten** $K'(x)$: um wie viel die Kosten ungefähr steigen, wenn eine ME mehr produziert wird
- **Grenzgewinn** $G'(x)=E'(x)-K'(x)$: um wie viel sich der Gewinn ungefähr ändert

Grenzgrößen sind Beträge pro Mengeneinheit und werden wie Preise in GE/ME angegeben. Deshalb zeichnet man sie in ein eigenes Diagramm.

Bei Velotec gilt $K'(x)=1{,}5x^2-12x+30$. Im Polypol ist $E'(x)=32$: Jede zusätzliche ME bringt genau den Marktpreis ein, die Grenzerlösgerade ist die Preisgerade. Im Monopol ist $E'(x)=-12x+84$. Die Gerade fällt doppelt so steil wie $p(x)=-6x+84$, denn um eine ME mehr abzusetzen, muss Velotec den Preis für *alle* Anhänger senken.

Das Widget zeigt links die Gesamtgrößen $E$, $K$ und $G$, rechts die Grenzgrößen. Beide Balken gehören zur selben Menge $x$.

- Bei $x=4$ ist der rechte Balken blau und $G'(4)=32-6=26$. Was bedeutet das für Velotec? Wie verläuft der Graph von $G$ links an dieser Stelle?
- Schiebe $x$ bis zum Schnittpunkt von $E'$ und $K'$. Was passiert dort mit dem linken Balken?
- Bei welcher Menge ist der rechte Balken am längsten? Wo liegt diese Stelle beim Graphen von $K'$?
- Schalte auf das Angebotsmonopol um. Wo schneidet $E'$ die $x$-Achse, und was gilt dort für $E$?

{% include widgets/widget-oekonomische-funktionen.html id="of-grenz" menge=4 fixkosten="false" grenz="true" %}

Solange $E'(x)>K'(x)$ ist, bringt eine weitere ME mehr Erlös als Kosten: $G'(x)>0$, der Gewinn steigt. Wo sich $E'$ und $K'$ schneiden, ist $G'(x)=0$. Danach übersteigen die Grenzkosten den Grenzerlös und der Gewinn fällt. Die **gewinnmaximale Menge** ist deshalb die Schnittstelle, an der $K'$ von unten nach oben durch $E'$ läuft. Im Polypol heißt das: Preis gleich Grenzkosten, bei Velotec bei etwa 8,16 ME. Im Monopol schneiden sich $E'$ und $K'$ bei 6 ME.

Weitere Kennzahlen lassen sich direkt ablesen:

- **Tiefpunkt von $K'$:** Hier steigen die Kosten am langsamsten. Seine Stelle ist der Übergang vom degressiven zum progressiven Kostenwachstum, bei Velotec $x_w=4$ ME. Der $y$-Wert sind die minimalen Grenzkosten, hier 6 GE/ME.
- **Nullstelle von $E'$ (Monopol):** Bis dort steigt der Erlös, danach fällt er. Das ist die erlösmaximale Menge, bei Velotec 7 ME, also genau die halbe Sättigungsmenge.
- **Konstanter Wert von $E'$ (Polypol):** Er ist der Marktpreis.
- **Senkrechter Abstand von $E'$ und $K'$:** Er ist der Grenzgewinn an dieser Stelle.

Manchmal ist statt $E'$ und $K'$ direkt die **Grenzgewinnfunktion** $G'$ gezeichnet. Bei Velotec im Polypol ist $G'(x)=-1{,}5x^2+12x+2$. Ihr Graph ist eine nach unten geöffnete Parabel:

- **Vorzeichen von $G'$:** Liegt der Graph oberhalb der $x$-Achse, steigt der Gewinn, liegt er darunter, fällt er.
- **Nullstelle mit Vorzeichenwechsel von $+$ nach $-$:** Hier hört der Gewinn auf zu steigen. Das ist die gewinnmaximale Menge, bei Velotec etwa 8,16 ME, dieselbe Stelle wie der Schnittpunkt von $E'$ und $K'$.
- **Hochpunkt von $G'$:** Hier steigt der Gewinn am stärksten. Er liegt an der Wendestelle von $G$, bei Velotec bei 4 ME mit einem Grenzgewinn von 26 GE/ME. Im Polypol ist das genau der Tiefpunkt von $K'$, weil $E'$ konstant ist und der Abstand zu $K'$ dort am größten wird.

„Im Schnittpunkt von $E'$ und $K'$ liegt der Break-even-Point.“ Stimmt das? Nein. Dort sind die *Steigungen* von $E$ und $K$ gleich, nicht ihre Werte. Gewinnschwelle, Gewinngrenze und der maximale Gewinn selbst lassen sich aus den Grenzfunktionen nicht ablesen, dafür braucht man $E$, $K$ oder $G$.

{% include check-anker.html nummer=3 %}

## Kennzahlen berechnen

Aus dem Graphen lassen sich die Kennzahlen nur ungefähr ablesen. Genau werden sie mit der Differentialrechnung bestimmt. Der erste Schritt ist immer, die gesuchte Kennzahl einem mathematischen Konzept zuzuordnen:

| mathematisches Konzept | Ansatz | Kennzahlen |
|---|---|---|
| $y$-Achsenabschnitt | $f(0)$ berechnen | $p_H$, $K_f$ |
| Nullstelle | $f(x)=0$ lösen | $s_m$, $x_{GS}$, $x_{GG}$ |
| Maximalstelle | $f'(x)=0$ lösen, $f''(x)<0$ prüfen | $x_{Emax}$ (Monopol), $x_{Gmax}$ |
| Wendestelle | $f''(x)=0$ lösen, $f'''(x)\neq 0$ prüfen | $x_w$ |
| Funktionswert | Stelle einsetzen | $E_{max}$, $G_{max}$, $p_{max}$ |

Dabei zählt nur der **ökonomische Definitionsbereich**: Mengen sind nicht negativ, im Polypol höchstens so groß wie die Kapazitätsgrenze und im Monopol höchstens so groß wie die Sättigungsmenge. Die Gleichung $G(x)=0$ hat bei Velotec drei Lösungen, eine davon negativ. Sie wird verworfen, die beiden positiven sind Gewinnschwelle und Gewinngrenze.

Typische Sonderfälle:

- Im Polypol ist $E'(x)=p$ konstant und nie null. Die erlösmaximale Menge ergibt sich deshalb nicht über die Ableitung, sondern ist die Kapazitätsgrenze.
- Liegt die Maximalstelle von $G$ hinter der Kapazitätsgrenze, kann sie nicht produziert werden. Dann ist der Gewinn an der Kapazitätsgrenze am größten.
- Ist $G$ im ganzen Definitionsbereich negativ, gibt es weder Gewinnschwelle noch Gewinngrenze.

Ein Wert wie $x_{Gmax}\approx 8{,}16$ ME ist ein Rechenergebnis. Im Sachzusammenhang heißt er: Bei etwa 816 Anhängern ist der Gewinn am größten. Jede Antwort gehört deshalb mit Einheit in einen Antwortsatz.

{% include check-anker.html nummer=4 %}

## Gewinnsituationen analysieren

Als Monopolist kann Velotec Preis und Absatzmenge nicht unabhängig voneinander festlegen: Zu jeder Menge gehört über die Preis-Absatz-Funktion genau ein Preis. Velotec wählt deshalb die gewinnmaximale Menge und verlangt den Preis, zu dem sich genau diese Menge absetzen lässt. Beide zusammen bilden den **Cournotschen Punkt**

$$
C\bigl(x_{Gmax}\mid p(x_{Gmax})\bigr).
$$

Für Velotec ist $C(6\mid 48)$: Am meisten verdient das Unternehmen, wenn es 600 Faltanhänger zu je 480 € anbietet.

„Der Cournotsche Punkt ist der Hochpunkt der Gewinnfunktion.“ Stimmt das? Nein. Er liegt auf dem Graphen von $p$, nicht auf dem von $G$. Seine $x$-Koordinate ist zwar die gewinnmaximale Menge, die $y$-Koordinate ist aber ein Preis in GE/ME und kein Gewinn.

### Veränderte Fixkosten

Die Miete für die Fertigungshalle steigt. Was bedeutet das für Velotecs Gewinn und für den Cournotschen Punkt? Im Widget sind Gewinnzone und Cournotscher Punkt eingeblendet.

- Erhöhe die Fixkosten von 48 GE auf 100 GE. Wie verändert sich der Graph von $G$?
- Was passiert mit Gewinnschwelle und Gewinngrenze, was mit der gewinnmaximalen Menge?
- Bleibt der Cournotsche Punkt an seiner Stelle?
- Bei welchen Fixkosten verschwindet die Gewinnzone?

{% include widgets/widget-oekonomische-funktionen.html id="of-fixkosten" marktform="monopol" umschalten="false" menge=6 gewinnzone="true" cournot="true" %}

Die Fixkosten sind der konstante Summand von $K$ und gehen mit negativem Vorzeichen in $G$ ein. Steigen sie um 52 GE, verschiebt sich der Graph von $G$ um 52 GE nach unten. Die Gewinnzone wird kleiner: Die Gewinnschwelle rückt von 0,90 ME auf etwa 1,92 ME, die Gewinngrenze von 9,92 ME auf etwa 9,30 ME. Der maximale Gewinn sinkt genau um 52 GE auf 116 GE.

Die gewinnmaximale Menge bleibt dagegen bei 6 ME. Beim Ableiten fällt der konstante Summand weg, $G'$ und damit die Gleichung $G'(x)=0$ ändern sich nicht. Weil die Menge gleich bleibt, bleibt auch der Preis $p(6)=48$ und damit der ganze Cournotsche Punkt.

Gewinn ist nur möglich, solange $G_{max}>0$ gilt. Die Fixkosten dürfen also höchstens um den bisherigen maximalen Gewinn steigen, bei Velotec auf $48+168=216$ GE.

### Weitere Fragen an die Gewinnfunktion

Mit der Gewinnfunktion lassen sich viele Entscheidungen begründen. Der Ansatz ergibt sich jeweils aus der Frage:

- **Mindestgewinn:** Bei welchen Mengen beträgt der Gewinn mindestens $c$ GE? Die Gleichung $G(x)=c$ liefert die Grenzen des Mengenbereichs.
- **Grenzgewinn:** $G'(x_0)$ gibt an, wie stark der Gewinn bei $x_0$ wächst. Bei Velotec ist $G'(4)=30$: Eine zusätzliche ME bringt dort ungefähr 30 GE mehr Gewinn. Ist $G'(x_0)>0$, ist das Gewinnmaximum noch nicht erreicht, ist $G'(x_0)<0$, ist es überschritten.
- **Grenzerlös gleich Grenzkosten:** Die Gleichung $E'(x)=K'(x)$ ist eine andere Schreibweise für $G'(x)=0$, also die notwendige Bedingung für das Gewinnmaximum.
- **Lohnt sich eine Maßnahme?** Eine Werbekampagne soll Velotecs Absatz von 4 ME auf 6 ME steigern. Der Gewinn wächst dadurch um $G(6)-G(4)=168-136=32$ GE. Kostet die Kampagne 40 GE, lohnt sie sich nicht. Verglichen wird der Gewinnzuwachs, nicht der neue Gesamtgewinn.
- **Patent läuft aus:** Kommen Konkurrenten auf den Markt, gilt wieder ein fester Marktpreis. Velotec rechnet dann wie im Polypol und verdient mit 32 GE/ME nur noch etwa 96 GE statt 168 GE.

{% include check-anker.html nummer=5 %}
