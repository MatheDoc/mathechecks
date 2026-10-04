---
fach: 1. Klausur Mathematik
klasse: WG3X
datum: 08.10.2026
thema: Mehrstufige Produktionsprozesse
bearbeitungszeit: 240 Minuten
---

# Aufgaben

Die Raumwerk GmbH fertigt modulare Messestände und zugehörige Montagesätze. Die Produktion erfolgt in zwei Stufen: Aus Rohstoffen entstehen zunächst Zwischenprodukte, die anschließend zu verkaufsfertigen Produkten zusammengestellt werden.

In allen Produktionsmatrizen stehen die Zeilen für die Inputs und die Spalten für die Outputs. Die Reihenfolge entspricht jeweils der Nummerierung der Güter. ME bezeichnet Mengeneinheiten. Alle gefertigten Endprodukte werden verkauft; Ausschuss und Lagerverluste bleiben unberücksichtigt.

# Teil A (ohne Hilfsmittel)

## Aufgabe 1

Für eine Versuchsserie verarbeitet Raumwerk drei Rohstoffe zu zwei Zwischenprodukten und daraus zu drei Endprodukten. Im Datenblatt sind die folgenden Matrizen ohne Bezeichnung der Produktionsstufen angegeben:

$$
P=\begin{pmatrix}
3 & 1 & 2\\
b & 2 & 1
\end{pmatrix},
\qquad
Q=\begin{pmatrix}
11 & 9 & 6\\
6 & c & 4\\
6 & 6 & 3
\end{pmatrix},
\qquad
S=\begin{pmatrix}
1 & a\\
2 & 0\\
0 & 3
\end{pmatrix}.
$$

a) Die Produktionsleitung benötigt ein vollständiges Datenblatt. Ordnen Sie die Matrizen den Produktionsstufen $RZ$, $ZE$ und $RE$ zu und begründen Sie Ihre Zuordnung anhand der Dimensionen. Stellen Sie die zugehörige Matrizengleichung auf und bestimmen Sie $a$, $b$ und $c$. \punkte{4}

b) Erläutern Sie die Bedeutung des Eintrags in der dritten Zeile und ersten Spalte von $Q$ für die Materialbeschaffung. \punkte{1}

\newpage

## Aufgabe 2

Gegeben sind die Matrizen

$$
A=\begin{pmatrix}3 & 2\\4 & 3\end{pmatrix},
\qquad
B=\begin{pmatrix}10 & 7\\18 & 13\end{pmatrix}.
$$

a) Bestimmen Sie $A^{-1}$ mithilfe des Gauß-Jordan-Algorithmus. Dokumentieren Sie die verwendeten Zeilenumformungen. \punkte{4}

b) Lösen Sie die Matrizengleichung $X\cdot A=B$. Geben Sie zunächst die Umstellung nach $X$ an und berechnen Sie anschließend $X$. \punkte{3}

\newpage

## Aufgabe 3

Raumwerk bietet drei Montagesätze $M_1$, $M_2$ und $M_3$ an. Für jeden Satz werden Profilstücke und Verbindungselemente benötigt:

| Rohstoffbedarf in ME je ME Montagesatz | $M_1$ | $M_2$ | $M_3$ |
|---|---|---|---|
| Profilstücke | 2 | 1 | 3 |
| Verbindungselemente | 1 | 1 | 1 |

Ein Restbestand von 36 ME Profilstücken und 16 ME Verbindungselementen soll vollständig verarbeitet werden. Das zugehörige LGS wurde bereits umgeformt:

$$
\left(\begin{array}{ccc|c}
1 & 0 & 2 & 20\\
0 & 1 & -1 & -4
\end{array}\right).
$$

Eine ME eines Montagesatzes entspricht einem vollständigen Satz.

a) Bestimmen Sie mit $m_3=t$ den allgemeinen Lösungsvektor $\vec{m}$ und erläutern Sie die Bedeutung des Parameters im Zusammenhang mit der Herstellung der Montagesätze. \punkte{4}

b) Die Lagerleitung möchte wissen, welche Lösungen tatsächlich produziert werden können. Bestimmen Sie alle zulässigen Werte von $t$ unter Berücksichtigung nichtnegativer, ganzzahliger Produktionsmengen. \punkte{2}

\newpage

# Teil B (mit Hilfsmittel)

## Aufgabe 4

Für die reguläre Messestandserie verarbeitet Raumwerk Profilstangen $R_1$, Verbinderpakete $R_2$ und Plattenzuschnitte $R_3$ zu Rahmen $Z_1$ und Wandmodulen $Z_2$. Daraus entstehen die Standpakete Basis $E_1$, Info $E_2$ und Ecke $E_3$. Eine ME eines Standpakets entspricht einem vollständigen Paket.

Die Rohstoff-Zwischenprodukt-Matrix und die Rohstoff-Endprodukt-Matrix lauten:

$$
RZ=\begin{pmatrix}
2 & 1\\
1 & 3\\
0 & 2
\end{pmatrix},
\qquad
RE=\begin{pmatrix}
7 & 6 & 5\\
6 & 8 & 10\\
2 & 4 & 6
\end{pmatrix}.
$$

Ein Messeveranstalter bestellt 20 ME Basis, 30 ME Info und 10 ME Ecke. Dafür steht ein Rohstofflager mit 400 ME $R_1$, 450 ME $R_2$ und 250 ME $R_3$ zur Verfügung. Noch fehlende Rohstoffe können rechtzeitig zu den unten angegebenen Preisen nachbestellt werden.

Die Kosten in Euro je ME werden durch folgende Zeilenvektoren beschrieben:

$$
\vec{k}_R=\begin{pmatrix}4 & 2 & 3\end{pmatrix},
\qquad
\vec{k}_Z=\begin{pmatrix}5 & 4\end{pmatrix},
\qquad
\vec{k}_E=\begin{pmatrix}12 & 10 & 8\end{pmatrix}.
$$

$\vec{k}_Z$ enthält ausschließlich die zusätzlichen Fertigungskosten der ersten Stufe, $\vec{k}_E$ ausschließlich die zusätzlichen Fertigungskosten der zweiten Stufe. Der gesamte Rohstoffverbrauch wird unabhängig vom Einkaufszeitpunkt zu den angegebenen Rohstoffpreisen bewertet.

Die Verkaufspreise je ME betragen $p$ Euro für Basis, 120 Euro für Info und 130 Euro für Ecke. Dem Auftrag werden Fixkosten von 1800 Euro zugerechnet.

a) Im Produktionsplan fehlt die Zusammensetzung der Standpakete aus Rahmen und Wandmodulen. Stellen Sie eine Matrizengleichung für $ZE$ auf und bestimmen Sie $ZE$. Erläutern Sie anhand des Pakets Info die Bedeutung einer Spalte Ihres Ergebnisses. \punkte{5}

b) Ermitteln Sie die für den Auftrag benötigten Mengen der beiden Zwischenprodukte und der drei Rohstoffe. Untersuchen Sie, ob das Lager ausreicht, und geben Sie gegebenenfalls die nachzubestellenden Mengen an. \punkte{5}

c) Die Kalkulationsabteilung muss die Kosten aller Produktionsstufen berücksichtigen. Stellen Sie einen Matrixterm für den Vektor der variablen Stückkosten auf und berechnen Sie $\vec{k}_v$. \punkte{5}

d) Raumwerk möchte mit dem Auftrag einen Deckungsbeitrag von 2600 Euro erzielen. Bestimmen Sie den dafür erforderlichen Verkaufspreis $p$ für das Paket Basis. \punkte{5}

e) Ein Mitarbeiter behauptet: „Bei einem positiven Deckungsbeitrag ist der Auftrag auf jeden Fall profitabel.“ Beurteilen Sie diese Aussage allgemein und für den vorliegenden Auftrag, indem Sie dessen Gesamtkosten und Gewinn beim Preis aus d) ermitteln. \punkte{4}

\newpage

## Aufgabe 5

Raumwerk plant eine gesonderte Verkaufsaktion für dieselben Standpakete. Die variablen Stückkosten bleiben unverändert. Für diese Aufgabe dürfen Sie unabhängig von Ihren vorherigen Ergebnissen verwenden:

$$
\vec{k}_v=\begin{pmatrix}77 & 80 & 83\end{pmatrix}
\quad\text{in Euro je ME}.
$$

Ein Preisparameter $u>0$ beschreibt verschiedene Aktionsangebote. Die Verkaufspreise in Euro je ME sind:

| Standpaket | Basis $E_1$ | Info $E_2$ | Ecke $E_3$ |
|---|---|---|---|
| Verkaufspreis | $u^2+113$ | $2u+66$ | $183-u^2$ |

Für die Aktion sind feste Absatzmengen von 10 ME Basis, 40 ME Info und 30 ME Ecke vorgesehen. Die der Aktion zugerechneten Fixkosten betragen 1500 Euro.

a) Stellen Sie den Vektor der Stückdeckungsbeiträge in Abhängigkeit von $u$ auf. \punkte{3}

b) Die Geschäftsführung verlangt, dass jedes Standpaket einen strikt positiven Stückdeckungsbeitrag liefert. Bestimmen Sie den gemeinsamen Bereich von $u$, in dem diese Forderung erfüllt ist. Begründen Sie insbesondere, ob die Randwerte dazugehören. \punkte{4}

c) Bestimmen Sie den gesamten Deckungsbeitrag und den Gewinn der Aktion als Funktionen von $u$. Zeigen Sie, dass sich der Gewinn auch in der Form

$$
G(u)=1380-20(u-2)^2
$$

darstellen lässt. \punkte{5}

d) Vertraglich sind nur Aktionsangebote mit $8\leq u\leq9$ zulässig. Bestimmen Sie den gewinnmaximierenden Wert von $u$ und den maximalen Gewinn unter dieser Einschränkung. Begründen Sie Ihr Ergebnis ohne Differentialrechnung mithilfe der Darstellung aus c). Beurteilen Sie außerdem den Vorschlag, stattdessen $u=2$ zu wählen, sowohl hinsichtlich des Vertrags als auch hinsichtlich der Forderung aus b). \punkte{6}

\newpage

## Aufgabe 6

Nach Abschluss der Verkaufsaktion soll ein gesondertes Rohstofflager vollständig geräumt werden. Raumwerk fertigt daraus wieder die Standpakete Basis, Info und Ecke nach dem unveränderten Produktionsverfahren:

$$
RE=\begin{pmatrix}
7 & 6 & 5\\
6 & 8 & 10\\
2 & 4 & 6
\end{pmatrix}.
$$

Eine Bestandsliste nennt 720 ME $R_1$, 960 ME $R_2$ und 480 ME $R_3$. Auf einem zweiten Beleg stehen stattdessen 500 ME $R_3$; die übrigen Angaben stimmen überein. Die Produktionsleitung prüft beide Bestandsangaben zunächst mathematisch.

Für diese Lagerauflösung gelten feste Verkaufspreise und variable Stückkosten in Euro je ME:

$$
\vec{p}=\begin{pmatrix}110 & 120 & 140\end{pmatrix},
\qquad
\vec{k}_v=\begin{pmatrix}77 & 80 & 83\end{pmatrix}.
$$

Die zugerechneten Fixkosten betragen 2000 Euro. Produktionsmengen müssen nichtnegativ und ganzzahlig sein.

a) Untersuchen Sie mithilfe des Rangkriteriums die Lösbarkeit von $RE\cdot\vec{m}=\vec{r}$ für beide Bestandsangaben. Geben Sie jeweils den Rang der Koeffizientenmatrix und der erweiterten Matrix sowie die Anzahl der Unbekannten an. Dokumentieren Sie eine geeignete Zeilenumformung oder Zeilenabhängigkeit. Erläutern Sie, was Ihre Ergebnisse für eine vollständige Lagerräumung bedeuten und weshalb das Rangkriterium allein noch keine wirtschaftlich zulässige Produktion garantiert. \punkte{6}

Für die folgenden Teilaufgaben ist durch eine Inventur der Bestand von 480 ME $R_3$ bestätigt worden.

b) Bestimmen Sie alle Produktionsvektoren, die das Lager vollständig räumen, in Abhängigkeit von $m_3=t$. Leiten Sie den zulässigen Wertebereich von $t$ her. \punkte{6}

c) Ein Vertriebspartner möchte genau halb so viele Pakete Ecke wie Pakete Info abnehmen. Ermitteln Sie das Produktionsprogramm, das diese Zusatzbedingung erfüllt und das Lager vollständig räumt. Prüfen Sie seine Zulässigkeit. \punkte{4}

d) Für eine alternative Vermarktung entfällt die Bedingung aus c). Bestimmen Sie den Gewinn in Abhängigkeit von $t$ und ermitteln Sie das gewinnmaximale Produktionsprogramm bei vollständiger Lagerräumung ohne weitere Absatzbeschränkungen. Geben Sie den maximalen Gewinn an. \punkte{5}

e) Tatsächlich lassen sich höchstens 45 ME Ecke verkaufen; zugleich müssen mindestens 40 ME Info geliefert werden. Bestimmen Sie unter diesen beiden Absatzbedingungen das gewinnmaximale Produktionsprogramm bei vollständiger Lagerräumung und den zugehörigen Gewinn. \punkte{5}

f) Die Einkaufsleitung schlägt vor, statt des Gewinns die variablen Kosten zu optimieren: „Das kostenminimale Produktionsprogramm ist hier eindeutig und deshalb automatisch auch gewinnmaximal.“ Untersuchen und beurteilen Sie diese Behauptung mithilfe der variablen Kosten als Funktion von $t$. \punkte{4}

\newpage

# Lösungen

## Aufgabe 1

a) $S$ ist $RZ$ mit der Dimension $3\times2$, $P$ ist $ZE$ mit der Dimension $2\times3$ und $Q$ ist $RE$ mit der Dimension $3\times3$. Die drei Rohstoffe bilden die Zeilen von $RZ$ und $RE$; die zwei Zwischenprodukte verbinden beide Stufen. Es gilt $S\cdot P=Q$.

Aus ausgewählten Einträgen folgt:

$$
3b=6\Rightarrow b=2,\qquad
1+2a=9\Rightarrow a=4,\qquad
c=2\cdot1+0\cdot2=2.
$$

b) Für eine ME des ersten Endprodukts werden über beide Produktionsstufen insgesamt 6 ME des dritten Rohstoffs benötigt.

\newpage

## Aufgabe 2

a) Mit $II\leftarrow II-\frac43 I$, anschließend $II\leftarrow3II$, $I\leftarrow I-2II$ und $I\leftarrow\frac13 I$:

$$
\left(\begin{array}{cc|cc}
3 & 2 & 1 & 0\\
4 & 3 & 0 & 1
\end{array}\right)
\sim
\left(\begin{array}{cc|cc}
3 & 2 & 1 & 0\\
0 & \frac13 & -\frac43 & 1
\end{array}\right)
\sim
\left(\begin{array}{cc|cc}
1 & 0 & 3 & -2\\
0 & 1 & -4 & 3
\end{array}\right).
$$

Damit ist $A^{-1}=\begin{pmatrix}3 & -2\\-4 & 3\end{pmatrix}$.

b) Multiplikation von rechts mit $A^{-1}$ ergibt:

$$
X=B\cdot A^{-1}
=\begin{pmatrix}10 & 7\\18 & 13\end{pmatrix}
\begin{pmatrix}3 & -2\\-4 & 3\end{pmatrix}
=\begin{pmatrix}2 & 1\\2 & 3\end{pmatrix}.
$$

\newpage

## Aufgabe 3

a) Aus $m_1+2t=20$ und $m_2-t=-4$ folgt

$$
\vec{m}(t)=\begin{pmatrix}20-2t\\t-4\\t\end{pmatrix}
=\begin{pmatrix}20\\-4\\0\end{pmatrix}
+t\begin{pmatrix}-2\\1\\1\end{pmatrix}.
$$

$t$ bezeichnet die Menge von $M_3$. Eine Erhöhung um eine ME ersetzt zwei ME $M_1$ durch jeweils eine zusätzliche ME $M_2$ und $M_3$, ohne den Rohstoffverbrauch zu verändern.

b) $20-2t\geq0$, $t-4\geq0$ und $t\geq0$ ergeben $4\leq t\leq10$. Wegen der vollständigen Sätze gilt $t\in\{4,5,6,7,8,9,10\}$.

\newpage

## Aufgabe 4

a) Es gilt $RZ\cdot ZE=RE$. Für jede Spalte $(x,y)^T$ von $ZE$ liefern die erste und dritte Zeile

$$
2x+y=(RE)_{1j},\qquad 2y=(RE)_{3j}.
$$

Daraus folgt

$$
ZE=\begin{pmatrix}3 & 2 & 1\\1 & 2 & 3\end{pmatrix}.
$$

Auch die zweite Zeile ist erfüllt: $(1\quad3)\cdot ZE=(6\quad8\quad10)$. Ein Paket Info benötigt 2 ME Rahmen und 2 ME Wandmodule.

b) Für $\vec{m}=(20,30,10)^T$:

$$
\vec{z}=ZE\cdot\vec{m}
=\begin{pmatrix}130\\110\end{pmatrix},
\qquad
\vec{r}=RE\cdot\vec{m}
=\begin{pmatrix}370\\460\\220\end{pmatrix}.
$$

Benötigt werden 130 ME Rahmen und 110 ME Wandmodule. Das Lager reicht nicht aus: 10 ME Verbinderpakete $R_2$ müssen nachbestellt werden. Für $R_1$ und $R_3$ ist keine Nachbestellung nötig; jeweils 30 ME bleiben übrig.

c) Alle drei Kostenarten werden addiert:

$$
\begin{aligned}
\vec{k}_v
&=\vec{k}_R\cdot RE+\vec{k}_Z\cdot ZE+\vec{k}_E\\
&=\begin{pmatrix}46 & 52 & 58\end{pmatrix}
+\begin{pmatrix}19 & 18 & 17\end{pmatrix}
+\begin{pmatrix}12 & 10 & 8\end{pmatrix}\\
&=\begin{pmatrix}77 & 80 & 83\end{pmatrix}
\quad\text{in Euro je ME}.
\end{aligned}
$$

d) $K_v=77\cdot20+80\cdot30+83\cdot10=4770$ Euro und $E=20p+4900$ Euro. Daher:

$$
DB=E-K_v=20p+130=2600
\quad\Rightarrow\quad p=123{,}50.
$$

Das Paket Basis muss für 123,50 Euro je ME verkauft werden.

e) $K=4770+1800=6570$ Euro; $G=DB-K_f=2600-1800=800$ Euro. Der Auftrag ist profitabel. Allgemein ist die Aussage falsch: Ein positiver Deckungsbeitrag deckt zunächst nur einen Teil der Fixkosten. Positiver Gewinn entsteht erst bei $DB>K_f$.

\newpage

## Aufgabe 5

a) $\vec{db}(u)=\vec{p}(u)-\vec{k}_v=\begin{pmatrix}u^2+36 & 2u-14 & 100-u^2\end{pmatrix}$ in Euro je ME.

b) Für $u>0$ gilt:

$$
u^2+36>0\text{ stets},\qquad
2u-14>0\Leftrightarrow u>7,\qquad
100-u^2>0\Leftrightarrow u<10.
$$

Der gemeinsame Bereich ist $7<u<10$. Bei $u=7$ ist der Stückdeckungsbeitrag von Info null, bei $u=10$ der von Ecke; beide Randwerte sind ausgeschlossen.

c) Mit dem Aktionsvektor $(10,40,30)^T$:

$$
\begin{aligned}
DB(u)&=10(u^2+36)+40(2u-14)+30(100-u^2)\\
&=-20u^2+80u+2800,\\
G(u)&=DB(u)-1500=-20u^2+80u+1300\\
&=1380-20(u-2)^2.
\end{aligned}
$$

Die Geldbeträge sind in Euro angegeben.

d) Auf $[8;9]$ ist $u-2$ positiv und wächst mit $u$. Deshalb wächst $(u-2)^2$ und der Gewinn sinkt. Das Maximum liegt bei $u=8$:

$$
G(8)=1380-20\cdot36=660\text{ Euro}.
$$

$u=8$ erfüllt auch $7<u<10$. Der Vorschlag $u=2$ würde zwar den Scheitelwert von 1380 Euro liefern, ist aber vertraglich ausgeschlossen. Zudem wäre der Stückdeckungsbeitrag von Info $2\cdot2-14=-10$ Euro je ME und damit negativ.

\newpage

## Aufgabe 6

a) Die dritte Zeile der Koeffizientenmatrix erfüllt die Abhängigkeit

$$
5\,III+2\,I-4\,II=0.
$$

Die ersten beiden Zeilen sind unabhängig, beispielsweise wegen $7\cdot8-6\cdot6=20\neq0$. Deshalb ist $rg(RE)=2$; die Zahl der Unbekannten ist $n=3$.

Für den Bestand $(720,960,480)^T$ gilt dieselbe Abhängigkeit rechts:

$$
5\cdot480+2\cdot720-4\cdot960=0.
$$

Also $rg(RE\mid\vec{r})=2<n=3$: Das LGS hat unendlich viele reelle Lösungen. Eine vollständige Lagerräumung ist algebraisch möglich.

Für den Bestand $(720,960,500)^T$ entsteht dagegen die Widerspruchszeile:

$$
5\cdot500+2\cdot720-4\cdot960=100,\qquad 0=100.
$$

Hier ist $rg(RE\mid\vec{r})=3>rg(RE)=2$: Es gibt keine Lösung, also keine vollständige Lagerräumung nach diesem Verfahren. Auch bei gleichen Rängen müssen Produktionsmengen zusätzlich auf Nichtnegativität und Ganzzahligkeit geprüft werden.

b) Für den bestätigten Bestand ergibt die Umformung:

$$
\left(\begin{array}{ccc|c}
7 & 6 & 5 & 720\\
6 & 8 & 10 & 960\\
2 & 4 & 6 & 480
\end{array}\right)
\sim
\left(\begin{array}{ccc|c}
1 & 0 & -1 & 0\\
0 & 1 & 2 & 120\\
0 & 0 & 0 & 0
\end{array}\right).
$$

Somit

$$
\vec{m}(t)=\begin{pmatrix}t\\120-2t\\t\end{pmatrix},
\qquad t\in\{0,1,\ldots,60\}.
$$

Der Bereich folgt aus $t\geq0$ und $120-2t\geq0$ sowie der Ganzzahligkeit der Paketzahlen.

c) $m_3=\frac12m_2$ ergibt $t=\frac12(120-2t)$, also $t=30$. Damit ist $\vec{m}=(30,60,30)^T$. Alle Mengen sind nichtnegativ und ganzzahlig, $t=30$ liegt im zulässigen Bereich.

d) $\vec{db}=\vec{p}-\vec{k}_v=(33,40,57)$. Damit:

$$
G(t)=33t+40(120-2t)+57t-2000=2800+10t.
$$

Der Gewinn wächst mit $t$. Ohne weitere Absatzbeschränkungen ist $t=60$ optimal: $\vec{m}=(60,0,60)^T$, $G_{\max}=3400$ Euro.

e) Die Absatzbedingungen ergeben $t\leq45$ und $120-2t\geq40$, also $t\leq40$. Zusammen mit b) gilt $t\in\{0,1,\ldots,40\}$. Optimal ist $t=40$: $\vec{m}=(40,40,40)^T$ und $G=3200$ Euro.

f) Die variablen Kosten betragen

$$
K_v(t)=77t+80(120-2t)+83t=9600\text{ Euro}.
$$

Sie sind für alle zulässigen Produktionsprogramme gleich. Es gibt daher kein eindeutiges Kostenminimum. Der Rohstoffverbrauch ist durch die Lagerräumung festgelegt; auch die Zwischenproduktmengen sind hier stets $(240,240)^T$. Die zusätzlichen Fertigungskosten der zweiten Stufe bleiben ebenfalls gleich, da $12t+10(120-2t)+8t=1200$ gilt. Die unterschiedlichen Gewinne entstehen durch unterschiedliche Erlöse. Kostenminimale Programme sind deshalb nicht automatisch gewinnmaximal; etwa $t=0$ liefert nur 2800 Euro Gewinn.
