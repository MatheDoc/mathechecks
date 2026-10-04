---
fach: 1. Klausur Mathematik
klasse: WG3X
datum: 08.10.2026
thema: Mehrstufige Produktionsprozesse
bearbeitungszeit: 240 Minuten
---

# Aufgaben

Die Lumina Leuchten GmbH fertigt Designleuchten für Wohn- und Gartenbereiche. Die Produktion erfolgt zweistufig: Aus Rohstoffen entstehen zunächst Zwischenprodukte (Baugruppen), die anschließend zu den Endprodukten zusammengebaut werden.

In allen Produktionsmatrizen stehen die Zeilen für die Inputs und die Spalten für die Outputs. Die Reihenfolge entspricht jeweils der Nummerierung der Güter. ME bezeichnet Mengeneinheiten, GE Geldeinheiten. Alle gefertigten Endprodukte werden verkauft; Ausschuss und Lagerverluste bleiben unberücksichtigt.

# Teil A (ohne Hilfsmittel)

## Aufgabe 1

Für die Wandleuchten-Linie „Lumo“ verarbeitet Lumina die Rohstoffe $R_1$ und $R_2$ zu den Baugruppen $Z_1$ und $Z_2$ und daraus die Endprodukte $E_1$ (Wandleuchte) und $E_2$ (Deckenleuchte). Im Datenblatt ist die Zusammensetzung der Endprodukte aus den Baugruppen nicht mehr lesbar. Bekannt sind die Matrix $RZ$ und die Bedarfsmatrix $RE$:

$$
RZ=\begin{pmatrix}2 & 1\\3 & 2\end{pmatrix},
\qquad
RE=\begin{pmatrix}8 & 6\\13 & 11\end{pmatrix}.
$$

a) Bestimmen Sie die inverse Matrix $RZ^{-1}$. \punkte{3}

b) Die Produktionsleitung möchte die Matrix $ZE$ rekonstruieren. Stellen Sie dazu eine Matrizengleichung für $ZE$ auf, formen Sie diese nach $ZE$ um und berechnen Sie $ZE$. \punkte{3}

\newpage

## Aufgabe 2

Für drei Leuchtenmodelle $E_1$ (Tischleuchte), $E_2$ (Stehleuchte) und $E_3$ (Pendelleuchte) werden nur die Rohstoffe $R_1$ (Aluminium) und $R_2$ (Glas) berücksichtigt. Die Bedarfsmatrix lautet

$$
RE=\begin{pmatrix}3 & 1 & 4\\2 & 4 & 6\end{pmatrix}.
$$

a) Berechnen Sie die Rohstoffmengen, die für die Herstellung von 10 ME $E_1$, 20 ME $E_2$ und 5 ME $E_3$ benötigt werden. \punkte{2}

b) Im Lager befinden sich noch 44 ME $R_1$ und 56 ME $R_2$, die vollständig aufgebraucht werden sollen. Für die Produktionsmengen $m_1$, $m_2$ und $m_3$ ergibt sich ein lineares Gleichungssystem mit der erweiterten Koeffizientenmatrix

$$
\left(\begin{array}{ccc|c}3 & 1 & 4 & 44\\2 & 4 & 6 & 56\end{array}\right),
$$

die sich auf die Diagonalform

$$
\left(\begin{array}{ccc|c}1 & 0 & 1 & 12\\0 & 1 & 1 & 8\end{array}\right)
$$

umformen lässt. Bestimmen Sie den Lösungsvektor, der alle Produktionsprogramme zur vollständigen Räumung des Lagers beschreibt, und geben Sie an, für welche Werte des Parameters die Mengen sinnvoll sind. \punkte{4}

\newpage

## Aufgabe 3

Für ein neues Prototyp-Set aus den Leuchten $E_1$, $E_2$ und $E_3$ soll ein Lager mit den Rohstoffen $R_1$, $R_2$ und $R_3$ vollständig geräumt werden. Gesucht sind die Produktionsmengen $m_1$, $m_2$ und $m_3$. Die Parameter $a$ und $b$ beschreiben den noch nicht endgültig festgelegten Materialbedarf von $E_3$ bzw. den Lagerbestand. Das zugehörige lineare Gleichungssystem wurde bereits auf Zeilenstufenform gebracht:

$$
\left(\begin{array}{ccc|c}2 & 1 & 1 & 20\\0 & 3 & 1 & 12\\0 & 0 & a-3 & b-12\end{array}\right).
$$

a) Untersuchen Sie mithilfe des Rangkriteriums, für welche Werte von $a$ und $b$ das Gleichungssystem genau eine Lösung, unendlich viele Lösungen bzw. keine Lösung besitzt. Beschreiben Sie jeweils kurz, was dies für die Räumung des Lagers bedeutet. \punkte{4}

b) Bestimmen Sie für $a=5$ und $b=12$ die Lösung des Gleichungssystems. \punkte{2}

\newpage

# Teil B (mit Hilfsmittel)

## Aufgabe 4

In ihrem Hauptsortiment fertigt die Lumina Leuchten GmbH die Endprodukte $E_1$ (Tischleuchte), $E_2$ (Stehleuchte) und $E_3$ (Pendelleuchte). Aus den Rohstoffen $R_1$, $R_2$ und $R_3$ entstehen die Baugruppen $Z_1$, $Z_2$ und $Z_3$. Die Produktionsmatrizen lauten

$$
RZ=\begin{pmatrix}4 & 1 & 0\\0 & 3 & 1\\2 & 0 & 5\end{pmatrix},
\qquad
ZE=\begin{pmatrix}1 & 2 & 0\\2 & 1 & 3\\1 & 0 & 2\end{pmatrix}.
$$

Die variablen Kosten in GE je ME betragen:

| Rohstoff | $R_1$ | $R_2$ | $R_3$ |
|---|---|---|---|
| Rohstoffkosten | 2 | 3 | 4 |

| Baugruppe | $Z_1$ | $Z_2$ | $Z_3$ |
|---|---|---|---|
| Fertigungskosten 1. Stufe | 5 | 4 | 6 |

| Endprodukt | $E_1$ | $E_2$ | $E_3$ |
|---|---|---|---|
| Fertigungskosten 2. Stufe | 20 | 25 | 30 |

Die Verkaufspreise schwanken mit einem Marktparameter $t>0$ (z. B. durch Wechselkurse und Aktionen):

| Endprodukt | $E_1$ | $E_2$ | $E_3$ |
|---|---|---|---|
| Verkaufspreis in GE je ME | $t^2+140$ | $t+80$ | $-t^2+277$ |

a) Erläutern Sie die Bedeutung der Zahl in der zweiten Zeile und zweiten Spalte von $RZ$ und geben Sie an, welche Baugruppe keinen Rohstoff $R_2$ benötigt. \punkte{2}

b) Die Einkaufsabteilung plant direkt mit den Rohstoffen. Berechnen Sie die Bedarfsmatrix $RE$. \punkte{3}

c) Für einen Auftrag sollen 15 ME $E_1$, 80 ME $E_2$ und 25 ME $E_3$ gefertigt werden. Bestimmen Sie die dafür benötigten Mengen der drei Baugruppen und der drei Rohstoffe. \punkte{4}

d) Die Kalkulation benötigt die variablen Stückkosten je Endprodukt. Stellen Sie einen Matrixterm für den Vektor $\vec{k}_v$ der variablen Stückkosten auf und berechnen Sie $\vec{k}_v$. \punkte{4}

e) Zeigen Sie, dass für die Stückdeckungsbeiträge der drei Leuchten gilt:

| Endprodukt | $E_1$ | $E_2$ | $E_3$ |
|---|---|---|---|
| Stückdeckungsbeitrag in GE je ME | $t^2+40$ | $t-2$ | $-t^2+144$ |

\punkte{4}

f) Der Vertrieb möchte wissen, für welche Werte von $t$ jedes der drei Modelle einen positiven Stückdeckungsbeitrag liefert. Bestimmen Sie den zugehörigen Bereich von $t$. \punkte{3}

g) Ermitteln Sie den maximalen Deckungsbeitrag für den Auftrag aus c) und den zugehörigen Wert von $t$. Weisen Sie nach, dass es sich um ein Maximum handelt, und prüfen Sie, ob der Wert von $t$ im Bereich aus f) liegt. \punkte{5}

h) Ein Mitarbeiter sagt: „Solange der Gesamtdeckungsbeitrag des Auftrags positiv ist, lohnt sich jedes der drei Modelle.“ Beurteilen Sie diese Aussage am Beispiel $t=1$. \punkte{3}

\newpage

## Aufgabe 5

Für das Gartensortiment stellt Lumina aus den Rohstoffen $R_1$, $R_2$ und $R_3$ über die Baugruppen $Z_1$, $Z_2$ und $Z_3$ die Endprodukte $E_1$ (Wegeleuchte), $E_2$ (Strahler) und $E_3$ (Laterne) her. Bekannt sind die Matrizen

$$
RZ=\begin{pmatrix}2 & 1 & 0\\1 & 3 & 1\\0 & 1 & 2\end{pmatrix},
\qquad
RE=\begin{pmatrix}7 & 6 & 4\\8 & 14 & 5\\5 & 6 & 6\end{pmatrix}.
$$

Die Matrix $ZE$ ist nicht dokumentiert. Die variablen Stückkosten betragen $\vec{k}_v=\begin{pmatrix}98 & 115 & 82\end{pmatrix}$ GE je ME, die Verkaufspreise $\vec{p}=\begin{pmatrix}150 & 170 & 140\end{pmatrix}$ GE je ME. Dem Gartensortiment werden Fixkosten von 4200 GE zugerechnet.

a) Bestimmen Sie die Matrix $ZE$. \punkte{4}

b) Im Lager liegen 490 ME $R_1$, 720 ME $R_2$ und 510 ME $R_3$, die vollständig verbraucht werden sollen. Ermitteln Sie das zugehörige Produktionsprogramm. \punkte{4}

c) Berechnen Sie für das Produktionsprogramm aus b) den Erlös, die gesamten variablen Kosten und den Gewinn. \punkte{3}

d) Eine zweite Bestandsliste nennt 320 ME $R_1$, 435 ME $R_2$ und 230 ME $R_3$. Beurteilen Sie, ob sich dieses Lager vollständig räumen lässt. \punkte{3}

e) Die Geschäftsführung möchte mit dem Programm aus b) einen Gewinn von 1500 GE erzielen. Bestimmen Sie den dafür erforderlichen Verkaufspreis der Laterne $E_3$, wenn die übrigen Preise unverändert bleiben. \punkte{3}

\newpage

## Aufgabe 6

Das Hauptsortiment aus Aufgabe 4 läuft aus. Das Restlager soll vollständig geräumt werden, indem die Endprodukte $E_1$, $E_2$ und $E_3$ nach unverändertem Verfahren gefertigt werden. Die Bedarfsmatrix lautet

$$
RE=\begin{pmatrix}6 & 9 & 3\\7 & 3 & 11\\7 & 4 & 10\end{pmatrix}.
$$

Im Lager befinden sich 330 ME $R_1$, 310 ME $R_2$ und 320 ME $R_3$. Für die Räumung gelten feste Verkaufspreise $\vec{p}=\begin{pmatrix}118 & 112 & 155\end{pmatrix}$ und variable Stückkosten $\vec{k}_v=\begin{pmatrix}100 & 82 & 133\end{pmatrix}$ (jeweils in GE je ME). Die zugerechneten Fixkosten betragen 1100 GE. Produktionsmengen müssen nichtnegativ und ganzzahlig sein.

a) Zeigen Sie mithilfe des Rangkriteriums, dass sich das Lager auf unendlich viele Arten vollständig räumen lässt, und bestimmen Sie alle zugehörigen Produktionsvektoren in Abhängigkeit von $m_3=t$. \punkte{5}

b) Bestimmen Sie den Bereich der zulässigen Werte von $t$. \punkte{3}

c) Ein Großkunde möchte doppelt so viele ME $E_2$ wie $E_3$ abnehmen. Ermitteln Sie das zugehörige Produktionsprogramm und prüfen Sie seine Zulässigkeit. \punkte{3}

d) Bestimmen Sie den Gewinn in Abhängigkeit von $t$. Ermitteln Sie, ab welchem Wert von $t$ die Räumung einen Gewinn erzielt, sowie das gewinnmaximale Produktionsprogramm und den maximalen Gewinn. \punkte{5}

e) Aufgrund von Lieferverträgen müssen mindestens 14 ME $E_1$ geliefert werden; zugleich lassen sich höchstens 25 ME $E_2$ absetzen. Bestimmen Sie unter diesen Bedingungen das gewinnmaximale Produktionsprogramm und den zugehörigen Gewinn. \punkte{4}

f) Eine Mitarbeiterin schlägt vor, $E_1$ nicht mehr zu fertigen, da $E_1$ den kleinsten Stückdeckungsbeitrag liefert. Beurteilen Sie diesen Vorschlag mithilfe Ihrer Ergebnisse aus d) und e). \punkte{3}

\newpage

# Lösungen

## Aufgabe 1

a) $\det(RZ)=2\cdot2-1\cdot3=1$. Damit ist

$$
RZ^{-1}=\frac{1}{1}\begin{pmatrix}2 & -1\\-3 & 2\end{pmatrix}=\begin{pmatrix}2 & -1\\-3 & 2\end{pmatrix}.
$$

b) Es gilt $RE=RZ\cdot ZE$. Multiplikation von links mit $RZ^{-1}$ ergibt $ZE=RZ^{-1}\cdot RE$:

$$
ZE=\begin{pmatrix}2 & -1\\-3 & 2\end{pmatrix}\cdot\begin{pmatrix}8 & 6\\13 & 11\end{pmatrix}
=\begin{pmatrix}16-13 & 12-11\\-24+26 & -18+22\end{pmatrix}
=\begin{pmatrix}3 & 1\\2 & 4\end{pmatrix}.
$$

\newpage

## Aufgabe 2

a) 

$$
\vec{r}=RE\cdot\vec{m}=\begin{pmatrix}3 & 1 & 4\\2 & 4 & 6\end{pmatrix}\cdot\begin{pmatrix}10\\20\\5\end{pmatrix}=\begin{pmatrix}30+20+20\\20+80+30\end{pmatrix}=\begin{pmatrix}70\\130\end{pmatrix}.
$$

Es werden 70 ME $R_1$ und 130 ME $R_2$ benötigt.

b) Mit $m_3=t$ folgt $m_1+t=12$ und $m_2+t=8$, also $m_1=12-t$ und $m_2=8-t$:

$$
\vec{m}=\begin{pmatrix}12\\8\\0\end{pmatrix}+t\begin{pmatrix}-1\\-1\\1\end{pmatrix},\qquad t\in\mathbb{R}.
$$

Sinnvoll sind nur nichtnegative Mengen: $t\geq0$, $12-t\geq0$ und $8-t\geq0$, also $0\leq t\leq8$.

\newpage

## Aufgabe 3

a) Die Koeffizientenmatrix hat für $a\neq3$ drei Zeilen mit Einträgen ungleich null, also $rg(A)=3$; die Anzahl der Unbekannten ist $n=3$.

- $a\neq3$ (beliebiges $b$): $rg(A)=rg(A\mid y)=3=n$ → genau eine Lösung. Das Lager lässt sich auf genau eine Weise vollständig räumen.
- $a=3$ und $b=12$: Die letzte Zeile ist eine Nullzeile, $rg(A)=rg(A\mid y)=2<3$ → unendlich viele Lösungen. Es gibt mehrere Produktionsprogramme, die das Lager räumen.
- $a=3$ und $b\neq12$: $rg(A)=2<rg(A\mid y)=3$ → keine Lösung. Das Lager lässt sich nicht vollständig räumen.

b) Für $a=5$ und $b=12$ lautet die letzte Zeile $2m_3=0$, also $m_3=0$. Aus Zeile 2: $3m_2+0=12$, also $m_2=4$. Aus Zeile 1: $2m_1+4+0=20$, also $m_1=8$.

$$
\vec{m}=\begin{pmatrix}8\\4\\0\end{pmatrix}
$$

\newpage

## Aufgabe 4

a) Die 3 gibt an, dass für 1 ME der Baugruppe $Z_2$ genau 3 ME des Rohstoffs $R_2$ benötigt werden. Die Baugruppe $Z_1$ benötigt keinen Rohstoff $R_2$ (Eintrag 0 in der zweiten Zeile, erste Spalte).

b)

$$
RE=RZ\cdot ZE=\begin{pmatrix}6 & 9 & 3\\7 & 3 & 11\\7 & 4 & 10\end{pmatrix}.
$$

c) Mit $\vec{m}=\begin{pmatrix}15\\80\\25\end{pmatrix}$:

$$
\vec{z}=ZE\cdot\vec{m}=\begin{pmatrix}175\\185\\65\end{pmatrix},
\qquad
\vec{r}=RE\cdot\vec{m}=\begin{pmatrix}885\\620\\675\end{pmatrix}.
$$

Benötigt werden 175 ME $Z_1$, 185 ME $Z_2$, 65 ME $Z_3$ sowie 885 ME $R_1$, 620 ME $R_2$ und 675 ME $R_3$. (Kontrolle: $RZ\cdot\vec{z}=\vec{r}$.)

d) Mit $\vec{k}_R=(2\;\;3\;\;4)$, $\vec{k}_Z=(5\;\;4\;\;6)$, $\vec{k}_E=(20\;\;25\;\;30)$:

$$
\vec{k}_v=\vec{k}_R\cdot RE+\vec{k}_Z\cdot ZE+\vec{k}_E=(61\;\;43\;\;79)+(19\;\;14\;\;24)+(20\;\;25\;\;30)=(100\;\;82\;\;133).
$$

e) Mit $\vec{p}=(t^2+140\;\;\;t+80\;\;\;-t^2+277)$ gilt $\vec{db}=\vec{p}-\vec{k}_v$:

$$
\vec{db}=(t^2+140-100\;\;\;t+80-82\;\;\;-t^2+277-133)=(t^2+40\;\;\;t-2\;\;\;-t^2+144).
$$

f) $E_1$: $t^2+40>0$ gilt für alle $t$. $E_2$: $t-2>0\Leftrightarrow t>2$. $E_3$: $-t^2+144>0\Leftrightarrow t^2<144\Leftrightarrow t<12$ (wegen $t>0$). Alle drei Stückdeckungsbeiträge sind genau für $2<t<12$ positiv.

g) 

$$
DB(t)=\vec{db}\cdot\vec{m}=15(t^2+40)+80(t-2)+25(-t^2+144)=-10t^2+80t+4040.
$$

$DB'(t)=-20t+80=0\Rightarrow t=4$; $DB''(t)=-20<0$, also liegt ein Maximum vor. $DB(4)=-160+320+4040=4200$. Der maximale Deckungsbeitrag beträgt 4200 GE bei $t=4$; wegen $2<4<12$ liegt $t$ im Bereich aus f).

h) Für $t=1$: $\vec{db}=(41\;\;-1\;\;143)$ und $DB(1)=-10+80+4040=4110>0$. Dennoch ist $db_2=-1<0$: Jede ME $E_2$ verringert den Deckungsbeitrag. Ohne $E_2$ wäre $DB=15\cdot41+25\cdot143=4190>4110$. Die Aussage ist falsch: Ein positiver Gesamtdeckungsbeitrag sagt nichts darüber aus, ob jedes einzelne Modell einen positiven Beitrag liefert.

\newpage

## Aufgabe 5

a) Aus $RE=RZ\cdot ZE$ folgt $ZE=RZ^{-1}\cdot RE$ (mit $\det(RZ)=8\neq0$):

$$
ZE=RZ^{-1}\cdot RE=\frac{1}{8}\begin{pmatrix}5 & -2 & 1\\-2 & 4 & -2\\1 & -2 & 5\end{pmatrix}\cdot\begin{pmatrix}7 & 6 & 4\\8 & 14 & 5\\5 & 6 & 6\end{pmatrix}=\begin{pmatrix}3 & 1 & 2\\1 & 4 & 0\\2 & 1 & 3\end{pmatrix}.
$$

b) Aus $RE\cdot\vec{m}=\vec{r}$ folgt $\vec{m}=RE^{-1}\cdot\vec{r}$ ($RE$ ist invertierbar mit $\det(RE)=152$):

$$
\vec{m}=RE^{-1}\cdot\begin{pmatrix}490\\720\\510\end{pmatrix}=\begin{pmatrix}30\\20\\40\end{pmatrix}.
$$

Gefertigt werden 30 ME $E_1$, 20 ME $E_2$ und 40 ME $E_3$.

c) 

$$
E=\vec{p}\cdot\vec{m}=150\cdot30+170\cdot20+140\cdot40=13500,
$$

$$
K_v=\vec{k}_v\cdot\vec{m}=98\cdot30+115\cdot20+82\cdot40=8520,
$$

$$
G=E-K_v-K_f=13500-8520-4200=780.
$$

Erlös 13500 GE, variable Kosten 8520 GE, Gewinn 780 GE.

d) $\vec{m}=RE^{-1}\cdot\begin{pmatrix}320\\435\\230\end{pmatrix}=\begin{pmatrix}40\\10\\-5\end{pmatrix}$. Die Lösung ist eindeutig, enthält aber $m_3=-5<0$. Negative Produktionsmengen sind nicht möglich, also lässt sich dieses Lager nicht vollständig räumen.

e) Bei $\vec{m}=(30\;\;20\;\;40)$ und Fixkosten 4200 GE gilt $G=780$. Für 1500 GE fehlen 720 GE; bei 40 ME $E_3$ muss der Preis daher um $720:40=18$ GE steigen. Alternativ: $30\cdot52+20\cdot55+40\,(p_3-82)-4200=1500\Rightarrow p_3=158$. Der Verkaufspreis der Laterne muss 158 GE je ME betragen.

\newpage

## Aufgabe 6

a) Erweiterte Matrix $(RE\mid\vec{r})$ mit $\vec{r}=\begin{pmatrix}330\\310\\320\end{pmatrix}$, umgeformt (z. B. mit dem GTR) zu

$$
\left(\begin{array}{ccc|c}1 & 0 & 2 & 40\\0 & 1 & -1 & 10\\0 & 0 & 0 & 0\end{array}\right).
$$

Es gilt $rg(RE)=rg(RE\mid\vec{r})=2<3=n$, also unendlich viele Lösungen. Mit $m_3=t$ folgt $m_1=40-2t$ und $m_2=10+t$:

$$
\vec{m}=\begin{pmatrix}40\\10\\0\end{pmatrix}+t\begin{pmatrix}-2\\1\\1\end{pmatrix}.
$$

b) $m_1\geq0\Rightarrow t\leq20$; $m_2\geq0\Rightarrow t\geq-10$; $m_3\geq0\Rightarrow t\geq0$. Zulässig sind die ganzen Zahlen $t$ mit $0\leq t\leq20$.

c) $m_2=2m_3\Rightarrow10+t=2t\Rightarrow t=10$. Produktionsprogramm: $\vec{m}=(20\;\;20\;\;10)^T$. Alle Mengen sind nichtnegativ und ganzzahlig, $t=10$ liegt in $[0;20]$, das Programm ist zulässig.

d) 

$$
E(t)=\vec{p}\cdot\vec{m}=5840+31t,\qquad K_v(t)=\vec{k}_v\cdot\vec{m}=4820+15t,
$$

$$
G(t)=E(t)-K_v(t)-1100=16t-80.
$$

$G(t)>0\Leftrightarrow t>5$: Ab $t=6$ erzielt die Räumung einen Gewinn. $G$ ist streng monoton steigend, das Maximum liegt am rechten Rand $t=20$: $\vec{m}=(0\;\;30\;\;20)^T$ mit $G(20)=240$ GE.

e) $m_1\geq14\Rightarrow40-2t\geq14\Rightarrow t\leq13$; $m_2\leq25\Rightarrow10+t\leq25\Rightarrow t\leq15$. Damit gilt $0\leq t\leq13$. Da $G$ steigend ist, gilt $t=13$: $\vec{m}=(14\;\;23\;\;13)^T$ mit $G(13)=16\cdot13-80=128$ GE.

f) Mit $\vec{db}=\vec{p}-\vec{k}_v=(18\;\;30\;\;22)$ hat $E_1$ tatsächlich den kleinsten Stückdeckungsbeitrag. Bei der Räumung ohne weitere Bedingungen ist es gewinnmaximal, $E_1$ gar nicht zu fertigen ($t=20$, $G=240$ GE). Die Begründung liegt aber nicht allein im kleinen Stückdeckungsbeitrag, sondern darin, dass $E_1$ bei begrenztem Lager viel Rohstoff verbraucht (je 2 ME $E_1$ weniger ermöglichen je 1 ME $E_2$ und $E_3$ mehr). Mit den Lieferverträgen aus e) darf $E_1$ nicht entfallen (mindestens 14 ME); der Gewinn sinkt dann von 240 GE auf 128 GE, die Mindestliefermenge ist aber zu erfüllen. Der Vorschlag ist daher nur ohne Liefervertrag sinnvoll.
