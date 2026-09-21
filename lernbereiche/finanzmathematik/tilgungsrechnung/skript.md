---
layout: module
title: "Tilgungsrechnung erklärt – Tilgungsplan, Annuitätenformel und Restschuld"
description: "Annuitätentilgung Schritt für Schritt: Tilgungsplan aufstellen, Annuität, Laufzeit und Restschuld berechnen, lückenhafte Tilgungspläne vervollständigen, Zinssatzwechsel, Sondertilgung und Tilgungspause."
page_context: Lernbereich
nav: dashboard
body_class: page-module
module_key: skript
published: true
lernbereich: tilgungsrechnung
gebiet: finanzmathematik
permalink: /lernbereiche/finanzmathematik/tilgungsrechnung/skript.html
---

# Tilgungsrechnung: ein Darlehen planmäßig zurückzahlen

## Einführung

Mara eröffnet ein kleines Café und nimmt dafür bei ihrer Bank ein Darlehen über 60 000 € zu 5 % auf. Die Bank schlägt eine **Annuitätentilgung** über zehn Jahre vor: Mara zahlt jedes Jahr denselben Betrag, die **Annuität** $A$. In diesem Betrag stecken zwei Dinge: die Zinsen für die noch offene Schuld und ein Tilgungsanteil, der die Schuld verringert. Es gilt also $A = Z_k + T_k$.

Im ersten Jahr sind 5 % von 60 000 €, also 3 000 €, Zinsen. Weil die Restschuld danach kleiner ist, fallen im zweiten Jahr weniger Zinsen an – bei gleicher Annuität bleibt mehr für die Tilgung. So werden die Zinsen von Jahr zu Jahr kleiner und der Tilgungsanteil entsprechend größer.

Bezeichnungen:

- $K_0$: Darlehenssumme, hier $60\,000$ €
- $RK_k$: Restschuld nach $k$ Jahren
- $Z_k$, $T_k$: Zinsen und Tilgung im Jahr $k$
- $A$: Annuität
- $q = 1 + \frac{p}{100}$: Zinsfaktor, hier $1{,}05$
- $n$: Laufzeit in Jahren, hier $10$

## Der Tilgungsplan

Wie hoch muss Maras jährliche Zahlung sein, damit die Schuld nach genau zehn Jahren getilgt ist? Die Antwort liefert ein Vergleich zweier Endwerte: Würde Mara zehn Jahre lang nichts zahlen, wäre die Schuld auf $K_0 \cdot q^{10}$ angewachsen. Ihre zehn Annuitäten bilden eine nachschüssige Rente mit Rate $A$, deren Endwert $\frac{A \cdot (q^{10} - 1)}{q - 1}$ ist. Am Ende soll beides gleich sein – die Zahlungen sollen die aufgezinste Schuld genau ausgleichen:

$$
K_0 \cdot q^n = \frac{A \cdot (q^n - 1)}{q - 1}
$$

Auflösen nach $A$ ergibt die **Annuitätenformel**:

$$
A = \frac{K_0 \cdot q^n \cdot (q - 1)}{q^n - 1}
$$

Für Mara: $A = \frac{60\,000 \cdot 1{,}05^{10} \cdot 0{,}05}{1{,}05^{10} - 1} \approx \frac{60\,000 \cdot 1{,}6289 \cdot 0{,}05}{0{,}6289} \approx 7\,770{,}27$ €. Umgekehrt lässt sich mit derselben Formel die Darlehenssumme bestimmen, die bei einer vorgegebenen Annuität möglich ist.

Mit der Annuität lässt sich die Rückzahlung Jahr für Jahr in einem **Tilgungsplan** verfolgen. Jede Zeile folgt demselben Schema:

| Jahr | Restschuld (Anfang) | Zinsen | Tilgung | Annuität | Restschuld (Ende) |
|---|---|---|---|---|---|
| $k$ | $RK_{k-1}$ | $Z_k = RK_{k-1} \cdot \frac{p}{100}$ | $T_k = A - Z_k$ | $A$ | $RK_k = RK_{k-1} - T_k$ |

Für Maras Darlehen lauten die ersten beiden Zeilen (Beträge in €):

| Jahr | Restschuld (Anfang) | Zinsen | Tilgung | Annuität | Restschuld (Ende) |
|---|---|---|---|---|---|
| 1 | 60 000,00 | 3 000,00 | 4 770,27 | 7 770,27 | 55 229,73 |
| 2 | 55 229,73 | 2 761,49 | 5 008,78 | 7 770,27 | 50 220,95 |

Jede Zelle wird auf zwei Nachkommastellen gerundet, mit den gerundeten Werten wird weitergerechnet. In der letzten Zeile ist die Tilgung gleich der verbliebenen Restschuld; die letzte Annuität weicht dadurch meist um wenige Cent von $A$ ab – bei Mara beträgt sie 7 770,34 €, also 7 Cent mehr (**Rundungsdifferenz**). Bei kurzen Laufzeiten ist die Differenz oft nur ein oder zwei Cent, gelegentlich auch null.

Im folgenden Widget kannst du Darlehenssumme, Zinssatz und Laufzeit verändern (voreingestellt ist Maras Darlehen). Der Tilgungsplan wird zeilenweise berechnet; im Diagramm siehst du, wie der Zinsanteil der Annuität von Jahr zu Jahr sinkt und der Tilgungsanteil wächst.

{% include widgets/widget-tilgungsplan.html %}

{% include check-anker.html nummer="1" %}

## Laufzeit

Wie lange dauert die Rückzahlung, wenn Annuität und Darlehenssumme feststehen? Die Annuitätenformel lässt sich nur umständlich nach $n$ auflösen. Einfacher ist ein zweiter Zusammenhang, der die Annuität mit der Tilgung des ersten Jahres verbindet:

$$
A = T_1 \cdot q^n
$$

Er ergibt sich aus der Beobachtung, dass die Tilgung von Jahr zu Jahr um den Faktor $q$ wächst ($T_{k+1} = T_k \cdot q$, weil die eingesparten Zinsen der Tilgung zugutekommen). Im letzten Jahr ist $T_n = T_1 \cdot q^{n-1}$; diese Restschuld wird samt Zinsen durch die letzte Annuität abgelöst: $A = T_n \cdot q = T_1 \cdot q^n$. Aufgelöst nach $q^n = \frac{A}{T_1}$ liefert der Logarithmus die Laufzeit.

Könnte Mara jährlich 9 000 € aufbringen, wäre $T_1 = 9\,000 - 3\,000 = 6\,000$ € und $n = \frac{\ln(9\,000 / 6\,000)}{\ln 1{,}05} \approx 8{,}31$ – das Darlehen wäre schon im neunten Jahr getilgt.

{% include check-anker.html nummer="2" %}

## Restschuld

Nach fünf Jahren möchte Mara wissen, wie viel sie noch schuldet. Statt fünf Zeilen des Tilgungsplans zu rechnen, nutzt sie die **Restschuldformel**: Die Darlehenssumme wird $k$ Jahre aufgezinst, davon wird der Endwert der $k$ bereits gezahlten Annuitäten abgezogen.

$$
RK_k = K_0 \cdot q^k - \frac{A \cdot (q^k - 1)}{q - 1}
\qquad
RK_k = K_0 - \frac{T_1 \cdot (q^k - 1)}{q - 1}
$$

Für Mara: $RK_5 = 60\,000 \cdot 1{,}05^5 - \frac{7\,770{,}27 \cdot (1{,}05^5 - 1)}{0{,}05} \approx 33\,641{,}25$ €. Aus der Restschuld ergeben sich Zinsen und Tilgung des Folgejahres: $Z_6 \approx 33\,641{,}25 \cdot 0{,}05 \approx 1\,682{,}06$ € und $T_6 = A - Z_6 \approx 6\,088{,}21$ €. Die Gesamtzinsen über die Laufzeit sind $n \cdot A - K_0 = 10 \cdot 7\,770{,}27 - 60\,000 = 17\,702{,}70$ €.

{% include check-anker.html nummer="3" %}

## Sachaufgaben zu Annuitätendarlehen

In Textaufgaben ist zu klären, welche Größen gegeben sind und ob Annuität, Darlehenssumme, Laufzeit oder Restschuld gesucht ist. „Gleich hohe Jahresraten“ deutet auf $A$, „welcher Kredit ist möglich“ auf $K_0$, „nach wie vielen Jahren getilgt“ auf $n$ und „Schulden nach $k$ Jahren“ auf $RK_k$.

{% include check-anker.html nummer="4" %}

## Tilgungsplan vervollständigen

Sind nur einzelne Werte eines Tilgungsplans bekannt, werden die Zusammenhänge $A = Z_k + T_k$, $Z_k = RK_{k-1} \cdot \frac{p}{100}$ und $RK_k = RK_{k-1} - T_k$ genutzt – auch rückwärts, etwa $RK_{k-1} = RK_k + T_k$. Kennt man aus einer Zeile Restschuld und Zinsen, lässt sich sogar der Zinssatz rekonstruieren: In Maras zweiter Zeile ist $\frac{2\,761{,}49}{55\,229{,}73} \cdot 100 \approx 5\,\%$.

{% include check-anker.html nummer="5" %}

## Zinssatzwechsel

Nach fünf Jahren läuft Maras Zinsbindung aus; die Bank bietet für die restlichen fünf Jahre 4 % an. Die Restschuld zum Zeitpunkt des Wechsels wird als neue Darlehenssumme und die Restlaufzeit als neue Laufzeit in die Annuitätenformel eingesetzt:

$$
A_{\text{neu}} = \frac{33\,641{,}25 \cdot 1{,}04^5 \cdot 0{,}04}{1{,}04^5 - 1} \approx 7\,556{,}74\,\text{€}
$$

Der Tilgungsplan wird ab dem sechsten Jahr mit der neuen Annuität und dem neuen Zinssatz fortgeführt; die Zinsen im sechsten Jahr sind dann $33\,641{,}25 \cdot 0{,}04 \approx 1\,345{,}65$ €.

{% include check-anker.html nummer="6" %}

## Sondertilgung und Tilgungspause

Das Café läuft gut: Zusammen mit der fünften Annuität leistet Mara eine **Sondertilgung** von 10 000 €. Die Restschuld sinkt damit auf $33\,641{,}25 - 10\,000 = 23\,641{,}25$ €. Anschließend gibt es zwei Möglichkeiten:

- Die Laufzeit bleibt bei zehn Jahren, die Annuität wird neu berechnet: $A_{\text{neu}} = \frac{23\,641{,}25 \cdot 1{,}05^5 \cdot 0{,}05}{1{,}05^5 - 1} \approx 5\,460{,}53$ €.
- Die Annuität bleibt bei 7 770,27 €, die Laufzeit verkürzt sich: $T_1' = 7\,770{,}27 - 23\,641{,}25 \cdot 0{,}05 \approx 6\,588{,}21$ € und $n = \frac{\ln(7\,770{,}27 / 6\,588{,}21)}{\ln 1{,}05} \approx 3{,}38$ – statt fünf nur noch gut drei Jahre.

Wäre das Jahr dagegen schlecht gelaufen, könnte Mara eine **Tilgungspause** vereinbaren: Im sechsten Jahr zahlt sie nur die Zinsen ($33\,641{,}25 \cdot 0{,}05 \approx 1\,682{,}06$ €), die Restschuld bleibt unverändert. Auch hier gibt es dieselben zwei Möglichkeiten:

- Die Gesamtlaufzeit bleibt bei zehn Jahren: Die Annuität für die verbleibenden vier Jahre wird neu berechnet und fällt höher aus ($\approx 9\,487{,}23$ €), weil ein Tilgungsjahr fehlt.
- Die Annuität bleibt bei 7 770,27 €: Nach der Pause ist die Situation genau dieselbe wie vor der Pause, die Rückzahlung dauert also noch fünf Jahre – die Gesamtlaufzeit verlängert sich um das Pausenjahr auf elf Jahre.

In allen Fällen ist das Vorgehen gleich: aktuelle Restschuld als neues $K_0$, dann entweder mit fester Restlaufzeit die Annuität oder mit fester Annuität die Laufzeit bestimmen.

{% include check-anker.html nummer="7" %}
