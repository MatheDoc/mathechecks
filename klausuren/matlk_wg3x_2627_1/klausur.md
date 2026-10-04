---
fach: 1. Klausur Mathematik
klasse: WG3X
datum: 08.10.2026
thema: Mehrstufige Produktionsprozesse
bearbeitungszeit: 240 Minuten
logo: klausuren/templates/logo.png
---

# Teil A (ohne Hilfsmittel)

Die **Elbrad GmbH** stellt E-Bikes und Zubehör her. In allen Aufgaben bezeichnet ME die Mengeneinheit und GE die Geldeinheit.

## Aufgabe 1

In der Montagehalle I fertigt die Elbrad GmbH die E-Bike-Modelle E1 und E2 in einem zweistufigen Produktionsprozess. Aus den Rohstoffen R1, R2 und R3 werden zunächst die Baugruppen Z1 und Z2 hergestellt, aus diesen anschließend die Modelle E1 und E2. Für die Produktionsmatrizen gilt (Zeilen: Input, Spalten: Output):

$$RZ=\begin{pmatrix}2&1\\ r&3\\ 1&2\end{pmatrix},\qquad ZE=\begin{pmatrix}3&s\\ 1&2\end{pmatrix},\qquad RE=\begin{pmatrix}7&8\\ 12&15\\ 5&7\end{pmatrix}$$

Dabei sind $RZ$ die Rohstoff-Baugruppen-Matrix, $ZE$ die Baugruppen-Endprodukt-Matrix und $RE$ die Rohstoff-Endprodukt-Matrix. Die Werte $r$ und $s$ sind in der Produktionsplanung noch nicht eingetragen.

a) Stellen Sie die Matrizengleichung auf, mit der sich die fehlenden Werte bestimmen lassen, und berechnen Sie $r$ und $s$. \punkte{4}

b) Für einen Auftrag über 10 ME von E1 und 20 ME von E2 soll der Einkauf die benötigten Rohstoffmengen bestellen. Berechnen Sie diese. \punkte{2}

\newpage

## Aufgabe 2

In der Zubehörfertigung stellt die Elbrad GmbH aus den Rohstoffen Aluminium (R1) und Stahl (R2) die Produkte E1 (Gepäckträger), E2 (Lenker) und E3 (Sattelstütze) her. Die folgende Tabelle zeigt, wie viele ME der Rohstoffe für je eine ME der Produkte benötigt werden:

| | E1 | E2 | E3 |
|---|---|---|---|
| R1 | 2 | 1 | 3 |
| R2 | 1 | 2 | 3 |

Am Monatsende liegen noch 60 ME von R1 und 54 ME von R2 im Lager. Diese Bestände sollen vollständig verbraucht werden. Mit den Mengen $x_1$, $x_2$, $x_3$ von E1, E2, E3 ergibt sich die erweiterte Koeffizientenmatrix und daraus die Diagonalform

$$\left(\begin{array}{ccc|c}2&1&3&60\\1&2&3&54\end{array}\right)\ \longrightarrow\ \left(\begin{array}{ccc|c}1&0&1&22\\0&1&1&16\end{array}\right).$$

a) Bestimmen Sie den Lösungsvektor, der alle möglichen Produktionsprogramme beschreibt, mit dem die Lagerbestände vollständig verbraucht werden. \punkte{3}

b) Ermitteln Sie die größte Menge von E3, die sich dabei herstellen lässt, und geben Sie das zugehörige Produktionsprogramm an. \punkte{3}

\newpage

## Aufgabe 3

Die E-Bike-Modelle E1 und E2 der Montagehalle II entstehen aus den Rohstoffen R1 und R2 über die Baugruppen Z1 und Z2. Die Rohstoff-Baugruppen-Matrix $RZ$ und die Rohstoff-Endprodukt-Matrix $RE$ sind bekannt, die Baugruppen-Endprodukt-Matrix $ZE$ ist unbekannt:

$$RZ=\begin{pmatrix}3&2\\4&3\end{pmatrix},\qquad RE=\begin{pmatrix}8&18\\11&25\end{pmatrix}$$

a) Berechnen Sie die Inverse $RZ^{-1}$. \punkte{3}

b) Bestimmen Sie die Matrix $ZE$ und geben Sie an, wie viele ME von Z1 und Z2 für eine ME von E2 benötigt werden. \punkte{3}

\newpage

# Teil B (mit Hilfsmitteln)

## Aufgabe 4

Die Standardlinie der Elbrad GmbH umfasst die E-Bike-Modelle E1 (City), E2 (Trekking) und E3 (Cargo). Sie werden zweistufig gefertigt: Aus den Rohstoffen R1, R2 und R3 entstehen die Baugruppen Z1, Z2 und Z3, aus diesen die Modelle. Die Mengen, die für je eine ME der Baugruppen bzw. der Modelle benötigt werden, zeigen die folgenden Tabellen:

| $RZ$ | Z1 | Z2 | Z3 |
|---|---|---|---|
| R1 | 4 | 1 | 0 |
| R2 | 2 | 3 | 1 |
| R3 | 1 | 2 | 3 |

| $ZE$ | E1 | E2 | E3 |
|---|---|---|---|
| Z1 | 1 | 2 | 1 |
| Z2 | 2 | 1 | 1 |
| Z3 | 1 | 1 | 2 |

a) Berechnen Sie die Rohstoff-Endprodukt-Matrix $RE$. \punkte{3}

b) Interpretieren Sie den Eintrag in der zweiten Zeile und dritten Spalte von $RE$ im Sachzusammenhang. \punkte{2}

c) Ein Händler bestellt 20 ME von E1, 30 ME von E2 und 10 ME von E3. Bestimmen Sie die dafür benötigten Mengen der Baugruppen und der Rohstoffe. \punkte{3}

d) Im Lager befinden sich 450 ME von R1, 530 ME von R2 und 500 ME von R3. Davon werden 40 ME von R1, 30 ME von R2 und 30 ME von R3 für ein Sondermodell auf einer Messe reserviert. Der Rest soll vollständig zu E1, E2 und E3 verarbeitet werden. Stellen Sie eine Matrizengleichung für die herstellbaren Mengen auf und bestimmen Sie diese. \punkte{5}

Die variablen Kosten der Produktion setzen sich aus den Rohstoffkosten und den Fertigungskosten beider Stufen zusammen (in GE pro ME):

| | R1 | R2 | R3 | Z1 | Z2 | Z3 | E1 | E2 | E3 |
|---|---|---|---|---|---|---|---|---|---|
| Kosten | 3 | 2 | 4 | 10 | 20 | 15 | 40 | 60 | 80 |

e) Zeigen Sie, dass für die variablen Stückkosten der drei Modelle $\vec{k}_v=(173\ \ 186\ \ 205)$ gilt. \punkte{4}

Die Verkaufspreise schwanken mit einem Marktparameter $t>0$ (z. B. durch Fördermittel und Wechselkurse):

| | E1 | E2 | E3 |
|---|---|---|---|
| Verkaufspreis in GE/ME | $t^2+148$ | $3t+174$ | $305-t^2$ |

f) Bestimmen Sie den Bereich von $t$, in dem alle drei Modelle einen positiven Stückdeckungsbeitrag erzielen. \punkte{3}

g) Der Vertrieb rechnet mit $t=4$. Beurteilen Sie, ob die Elbrad GmbH bei diesem Wert alle drei Modelle herstellen sollte. \punkte{2}

h) Die Geschäftsführung plant, 20 ME von E1, 30 ME von E2 und 10 ME von E3 zu verkaufen, und strebt dabei einen Deckungsbeitrag von 1 500 GE an. Ermitteln Sie, welchen Wert $t$ dafür annehmen muss, und prüfen Sie, ob dieser Wert im Bereich aus Teilaufgabe f) liegt. \punkte{5}

\newpage

## Aufgabe 5

In der Zubehörfertigung werden aus den Rohstoffen R1, R2 und R3 die vier Produkte E1 bis E4 hergestellt. Die folgende Tabelle gibt an, wie viele ME der Rohstoffe für je eine ME der Produkte benötigt werden:

| $RE$ | E1 | E2 | E3 | E4 |
|---|---|---|---|---|
| R1 | 2 | 3 | 3 | 2 |
| R2 | 2 | 5 | 2 | 3 |
| R3 | 3 | 5 | 5 | 4 |

Zum Quartalsende liegen 205 ME von R1, 240 ME von R2 und 335 ME von R3 im Lager. Diese Bestände sollen vollständig verbraucht werden.

a) Bestimmen Sie den Lösungsvektor, der alle möglichen Produktionsprogramme beschreibt. Verwenden Sie dabei die Menge von E4 als Parameter $t$. \punkte{4}

b) Bestimmen Sie den Bereich, in dem $t$ liegen darf, und geben Sie an, wie viele ME von E4 höchstens hergestellt werden können. \punkte{4}

c) Im nächsten Quartal sind die Lagerbestände andere. Begründen Sie mit dem Rangkriterium, dass das lineare Gleichungssystem für jeden beliebigen Lagerbestand unendlich viele Lösungen besitzt. Erläutern Sie, warum sich dennoch nicht jeder Lagerbestand vollständig verbrauchen lässt. \punkte{3}

d) Ein Kunde verlangt, dass von E1 doppelt so viele ME hergestellt werden wie von E2. Bestimmen Sie das zugehörige Produktionsprogramm für den Lagerbestand aus der Aufgabeneinleitung. \punkte{3}

Für die Produkte gelten folgende Werte (in GE pro ME):

| | E1 | E2 | E3 | E4 |
|---|---|---|---|---|
| variable Stückkosten | 22 | 30 | 28 | 18 |
| Verkaufspreis | 40 | 45 | 40 | 35 |

e) Bestimmen Sie das Produktionsprogramm mit dem höchsten Deckungsbeitrag und geben Sie diesen an. \punkte{5}

f) Ein Mitarbeiter schlägt vor, das Programm mit den geringsten variablen Kosten zu wählen. Beurteilen Sie diesen Vorschlag. \punkte{4}

g) Im Programm mit dem höchsten Deckungsbeitrag wird E3 nicht hergestellt, obwohl E3 einen positiven Stückdeckungsbeitrag hat. Erläutern Sie diesen Sachverhalt. \punkte{2}

\newpage

## Aufgabe 6

Die Elbrad GmbH entwickelt das Lastenrad E3 weiter. Neben E1 und E2 soll es aus den Rohstoffen R1, R2 und R3 gefertigt werden. Je nach Konstruktion benötigt eine ME von E3 dabei $a$ ME von R1. Die Rohstoff-Endprodukt-Matrix lautet

$$RE_a=\begin{pmatrix}1&2&a\\2&5&4\\1&3&2\end{pmatrix}\qquad(\text{Zeilen: R1, R2, R3; Spalten: E1, E2, E3}).$$

Im Lager befinden sich 56 ME von R1, 115 ME von R2 und 65 ME von R3. Diese Bestände sollen vollständig verbraucht werden.

a) Interpretieren Sie die Einträge der ersten Spalte von $RE_a$ im Sachzusammenhang und erläutern Sie, warum $a\geq 0$ gelten muss. \punkte{2}

b) Stellen Sie die erweiterte Koeffizientenmatrix des zugehörigen linearen Gleichungssystems auf und bringen Sie diese in Zeilenstufenform. Untersuchen Sie mit dem Rangkriterium, für welche Werte von $a$ sich die Lagerbestände vollständig verbrauchen lassen und für welche davon die Lösung eindeutig ist. \punkte{6}

c) Die Konstruktionsabteilung entscheidet sich für $a=3$. Bestimmen Sie das Produktionsprogramm, mit dem die Lagerbestände vollständig verbraucht werden. \punkte{3}

d) Für $a=2$ soll der Lagerbestand von R3 auf $r_3$ ME angepasst werden, sodass sich die Lagerbestände vollständig verbrauchen lassen. Bestimmen Sie $r_3$ und geben Sie alle sinnvollen Produktionsprogramme an. \punkte{6}

e) Für $a\neq2$ gilt bei dem ursprünglichen Lagerbestand für die Menge von E3 die Formel $m_3=\dfrac{6}{a-2}$. Die Konstruktionsabteilung möchte erreichen, dass genau 12 ME von E3 hergestellt werden. Bestimmen Sie den zugehörigen Wert von $a$ und prüfen Sie, ob sich damit ein sinnvolles Produktionsprogramm ergibt. \punkte{3}

\newpage

# Lösungen

## Teil A

### Aufgabe 1

a) Es gilt $RZ\cdot ZE=RE$. Zweite Zeile mal erste Spalte: $3r+3=12\Rightarrow r=3$. Erste Zeile mal zweite Spalte: $2s+2=8\Rightarrow s=3$. Probe mit dem Eintrag in Zeile 2, Spalte 2: $r\cdot s+6=9+6=15$.

b) $\vec{r}=RE\cdot\begin{pmatrix}10\\20\end{pmatrix}=\begin{pmatrix}7\cdot10+8\cdot20\\12\cdot10+15\cdot20\\5\cdot10+7\cdot20\end{pmatrix}=\begin{pmatrix}230\\420\\190\end{pmatrix}$. Benötigt werden 230 ME von R1, 420 ME von R2 und 190 ME von R3.

### Aufgabe 2

a) Mit $x_3=t$ folgt aus der Diagonalform $x_1+t=22$ und $x_2+t=16$, also
$$\vec{x}=\begin{pmatrix}22\\16\\0\end{pmatrix}+t\begin{pmatrix}-1\\-1\\1\end{pmatrix}.$$

b) Alle Mengen müssen nichtnegativ sein: $22-t\geq0$, $16-t\geq0$, $t\geq0$, also $0\leq t\leq16$. Die größte Menge von E3 beträgt 16 ME; das Programm ist $(6\mid 0\mid 16)$, also 6 ME von E1, 0 ME von E2 und 16 ME von E3.

### Aufgabe 3

a) $$RZ^{-1}=\frac{1}{1}\begin{pmatrix}3&-2\\-4&3\end{pmatrix}=\begin{pmatrix}3&-2\\-4&3\end{pmatrix}$$

b) $ZE=RZ^{-1}\cdot RE=\begin{pmatrix}3&-2\\-4&3\end{pmatrix}\cdot\begin{pmatrix}8&18\\11&25\end{pmatrix}=\begin{pmatrix}2&4\\1&3\end{pmatrix}$.
Für eine ME von E2 werden 4 ME von Z1 und 3 ME von Z2 benötigt (zweite Spalte).

## Teil B

### Aufgabe 4

a) $RE=RZ\cdot ZE=\begin{pmatrix}6&9&5\\9&8&7\\8&7&9\end{pmatrix}$

b) Der Eintrag $7$ bedeutet: Für die Herstellung von 1 ME von E3 (Cargo) werden insgesamt 7 ME des Rohstoffs R2 benötigt (über alle Baugruppen hinweg).

c) Baugruppen: $\vec{z}=ZE\cdot\begin{pmatrix}20\\30\\10\end{pmatrix}=\begin{pmatrix}90\\80\\70\end{pmatrix}$, d. h. 90 ME von Z1, 80 ME von Z2 und 70 ME von Z3.
Rohstoffe: $\vec{r}=RE\cdot\begin{pmatrix}20\\30\\10\end{pmatrix}=\begin{pmatrix}440\\490\\460\end{pmatrix}$, d. h. 440 ME von R1, 490 ME von R2 und 460 ME von R3 (Kontrolle: $RZ\cdot\vec{z}$ liefert dasselbe).

d) Mit $\vec{m}$ als Vektor der herstellbaren Mengen, $\vec{s}=(40\ 30\ 30)^T$ und $\vec{r}=(450\ 530\ 500)^T$ gilt
$$RE\cdot\vec{m}+\vec{s}=\vec{r}\ \Rightarrow\ \vec{m}=RE^{-1}\cdot(\vec{r}-\vec{s})=RE^{-1}\cdot\begin{pmatrix}410\\500\\470\end{pmatrix}=\begin{pmatrix}30\\20\\10\end{pmatrix}.$$
Es können 30 ME von E1, 20 ME von E2 und 10 ME von E3 hergestellt werden.

e) $\vec{k}_v=\vec{k}_R\cdot RE+\vec{k}_Z\cdot ZE+\vec{k}_E$ mit $\vec{k}_R=(3\ 2\ 4)$, $\vec{k}_Z=(10\ 20\ 15)$, $\vec{k}_E=(40\ 60\ 80)$:
$$\vec{k}_R\cdot RE=(68\ \ 71\ \ 65),\qquad \vec{k}_Z\cdot ZE=(65\ \ 55\ \ 60)$$
$$\vec{k}_v=(68\ \ 71\ \ 65)+(65\ \ 55\ \ 60)+(40\ \ 60\ \ 80)=(173\ \ 186\ \ 205)$$

f) $\vec{db}=\vec{p}-\vec{k}_v=(t^2-25\ \ \ 3t-12\ \ \ 100-t^2)$.
E1: $t^2-25>0\Leftrightarrow t>5$ (wegen $t>0$). E2: $3t-12>0\Leftrightarrow t>4$. E3: $100-t^2>0\Leftrightarrow t<10$ (wegen $t>0$).
Alle drei Stückdeckungsbeiträge sind positiv für $5<t<10$.

g) Für $t=4$ ergibt sich $\vec{db}=(-9\ \ 0\ \ 84)$. E1 erzielt einen negativen Stückdeckungsbeitrag: Jede verkaufte ME deckt nicht einmal die variablen Kosten und vergrößert den Verlust. E2 trägt nichts zur Deckung der Fixkosten bei. Nur E3 ist lohnend; E1 und E2 sollten bei $t=4$ nicht hergestellt werden.

h) $DB(t)=\vec{db}\cdot\begin{pmatrix}20\\30\\10\end{pmatrix}=20(t^2-25)+30(3t-12)+10(100-t^2)=10t^2+90t+140$.
$10t^2+90t+140=1500\Leftrightarrow t^2+9t-136=0\Leftrightarrow t=8$ oder $t=-17$. Wegen $t>0$ ist $t=8$. Es gilt $5<8<10$, der Wert liegt im Bereich aus f).

### Aufgabe 5

a) Lösen von $RE\cdot\vec{m}=\vec{r}$ mit $m_4=t$:
$$\vec{m}=\begin{pmatrix}20\\30\\25\\0\end{pmatrix}+t\begin{pmatrix}2\\-1\\-1\\1\end{pmatrix}=\begin{pmatrix}20+2t\\30-t\\25-t\\t\end{pmatrix}$$

b) Alle Mengen $\geq0$: $20+2t\geq0$ (immer erfüllt für $t\geq0$), $30-t\geq0$, $25-t\geq0$, $t\geq0$. Also $0\leq t\leq25$. Von E4 können höchstens 25 ME hergestellt werden.

c) $RE$ hat nur drei Zeilen, also $rg(RE)\leq3$. Aus a) folgt $rg(RE)=3$ (drei Pivotzeilen in der Zeilenstufenform). Die erweiterte Matrix $(RE\mid\vec{r})$ hat ebenfalls drei Zeilen, also $rg(RE\mid\vec{r})=3$ für jedes $\vec{r}$. Wegen $rg(RE)=rg(RE\mid\vec{r})=3<4=n$ gibt es unendlich viele Lösungen.
Aber: Die Lösungen müssen nichtnegativ sein. Für manche Lagerbestände sind in jeder der unendlich vielen Lösungen mindestens eine Komponente negativ; dann ist keine Produktion möglich, die das Lager vollständig verbraucht.

d) Bedingung $m_1=2\cdot m_2$: $20+2t=2(30-t)\Leftrightarrow4t=40\Leftrightarrow t=10$. Es liegt $0\leq10\leq25$ vor. Produktionsprogramm: $(40\mid20\mid15\mid10)$.

e) $\vec{db}=\vec{p}-\vec{k}_v=(18\ \ 15\ \ 12\ \ 17)$.
$DB(t)=18(20+2t)+15(30-t)+12(25-t)+17t=1110+26t$.
$DB$ ist steigend in $t$, also maximal für $t=25$: $DB=1110+26\cdot25=1760$ GE bei dem Programm $(70\mid5\mid0\mid25)$.

f) $K_v(t)=\vec{k}_v\cdot\vec{m}=22(20+2t)+30(30-t)+28(25-t)+18t=2040+4t$.
$K_v$ ist steigend, also minimal für $t=0$: $K_v=2040$ GE bei dem Programm $(20\mid30\mid25\mid0)$. Dort beträgt der Deckungsbeitrag nur $DB(0)=1110$ GE und damit 650 GE weniger als das Maximum von 1760 GE. Der Vorschlag ist nicht sinnvoll: Entscheidend ist der Deckungsbeitrag, nicht nur die Kosten; bei $t=25$ steigen die variablen Kosten zwar um 100 GE, die Erlöse aber um 750 GE.

g) Erhöht man $t$ um 1, werden 2 ME mehr von E1 und 1 ME mehr von E4 hergestellt, dafür je 1 ME weniger von E2 und E3 (Rohstoffverbrauch bleibt gleich). Der Deckungsbeitrag ändert sich um $2\cdot18+17-15-12=26$ GE. Der Tausch lohnt sich, bis E3 vollständig verdrängt ist ($t=25$). E3 ist zwar für sich genommen lohnend, bindet aber die knappen Rohstoffe schlechter als E1 und E4.

### Aufgabe 6

a) Die Einträge $1$, $2$, $1$ der ersten Spalte geben an, dass für 1 ME von E1 genau 1 ME von R1, 2 ME von R2 und 1 ME von R3 benötigt werden. Der Rohstoffbedarf kann nicht negativ sein, daher $a\geq0$.

b) Erweiterte Koeffizientenmatrix und Umformung ($II-2\cdot I$, $III-I$, dann $III-II$):
$$\left(\begin{array}{ccc|c}1&2&a&56\\2&5&4&115\\1&3&2&65\end{array}\right)\to\left(\begin{array}{ccc|c}1&2&a&56\\0&1&4-2a&3\\0&1&2-a&9\end{array}\right)\to\left(\begin{array}{ccc|c}1&2&a&56\\0&1&4-2a&3\\0&0&a-2&6\end{array}\right)$$
Fall $a\neq2$: $rg(A)=rg(A\mid\vec{r})=3=n$, also genau eine Lösung (Lager räumbar, eindeutig).
Fall $a=2$: Die letzte Zeile lautet $(0\ 0\ 0\mid6)$, also $rg(A)=2<3=rg(A\mid\vec{r})$: keine Lösung, das Lager lässt sich nicht vollständig verbrauchen.

c) Für $a=3$: $m_3=\frac{6}{3-2}=6$; aus Zeile II: $m_2+(4-6)\cdot6=3\Rightarrow m_2=15$; aus Zeile I: $m_1+2\cdot15+3\cdot6=56\Rightarrow m_1=8$. Programm: $(8\mid15\mid6)$.

d) Für $a=2$ lautet die letzte Zeile nach Umformung $(0\ 0\ 0\mid r_3+56-115)$. Unendlich viele Lösungen ergeben sich genau für $r_3+56-115=0$, also $r_3=59$.
Dann gilt $rg(A)=rg(A\mid\vec{r})=2<3$. Mit $m_3=t$: Zeile II: $m_2=3$; Zeile I: $m_1+2\cdot3+2t=56\Rightarrow m_1=50-2t$.
$$\vec{m}=\begin{pmatrix}50\\3\\0\end{pmatrix}+t\begin{pmatrix}-2\\0\\1\end{pmatrix}$$
Nichtnegativität: $50-2t\geq0\Rightarrow t\leq25$. Sinnvoll sind alle Programme mit $0\leq t\leq25$.

e) $\frac{6}{a-2}=12\Leftrightarrow a-2=0{,}5\Leftrightarrow a=2{,}5$. Zeile II: $m_2+(4-5)\cdot12=3\Rightarrow m_2=15$; Zeile I: $m_1+2\cdot15+2{,}5\cdot12=56\Rightarrow m_1=-4$. Wegen $m_1<0$ ist das Programm nicht herstellbar: Mit $a=2{,}5$ lässt sich das Lager nicht sinnvoll vollständig verbrauchen, die Konstruktionsabteilung muss einen anderen Wert für $a$ wählen.
