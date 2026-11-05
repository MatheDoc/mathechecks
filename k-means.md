# K-Means: Inhalte und Aufgaben

## Hinweise

- Konvention bei gleichem Abstand: Der Wert wird dem Cluster mit dem kleineren Index zugewiesen (bei A und B also Cluster A).
- Mehrdimensionaler Fall: keine unterschiedlichen Achsenskalierungen, nur gleichartige Größen (z. B. Längen).
- Mehrdimensionaler Fall: Abstandsdefinitiion nötig, Vektorbegriff einführen?, evtl adhoc Definition $d(X;P)=\sqrt{(p_1-x_1)^2 + (p_2-x_2)^2}$, Mittelwerte komponenetenweise berechnen, Abstandsquadrate für einfachere Rechnung (Bezug Fehlerfunktione)
- Güte berechnen: Summe der Abstandsquadrate aller Punkte zu ihren zugeordneten Clustern.
- Startzentren-Abhängigkeit: Gleiche Daten, zwei verschiedene Startzentren, zwei verschiedene Endergebnisse. Anschließend über die SSE entscheiden, welches besser ist. Das zeigt lokale Optima.
- Ellenbogen-Methode wohl zu kompliziert.
- Graphisch: Mittelsenkechte

## Ablauf einer Iteration

1. Abstände zu den Clusterzentren berechnen (kann übersprungen werden, wenn nur die Zuordnung relevant ist).
2. Jeden Wert dem nächstgelegenen Zentrum zuordnen.
3. Neue Zentren als Mittelwerte der Cluster berechnen.

Konvergenz: Die Zuordnung ändert sich nicht mehr (und damit bleiben auch die Zentren gleich).

## Eindimensional, 10 Werte, 2 Zentren

### Aufgabe

Gegeben sind die Werte

2; 4; 5; 7; 8; 9; 11,5; 12; 13,5; 15

und die Startzentren $z_A = 4$ und $z_B = 10$.

Führen Sie das K-Means-Verfahren bis zur Konvergenz durch.


### Lösung

**1. Iteration**

Alte Zentren: $z_A = 4$ und $z_B = 10$

| Wert | $\mid x_i-z_A\mid$ | $\mid x_i-z_B\mid$ | Cluster |
|:---:|:---:|:---:|:---:|
| 2    | 2    | 8    | A |
| 4    | 0    | 6    | A |
| 5    | 1    | 5    | A |
| 7    | 3    | 3    | A (Gleichstand) |
| 8    | 4    | 2    | B |
| 9    | 5    | 1    | B |
| 11,5 | 7,5  | 1,5  | B |
| 12   | 8    | 2    | B |
| 13,5 | 9,5  | 3,5  | B |
| 15   | 11   | 5    | B |

Neue Zentren:

$z_A = \frac{2+4+5+7}{4} = \frac{18}{4} = 4{,}5$

$z_B = \frac{8+9+11{,}5+12+13{,}5+15}{6} = \frac{69}{6} = 11{,}5$

**2. Iteration**

Alte Zentren: $z_A = 4{,}5$ und $z_B = 11{,}5$

| Wert | $\mid x_i-z_A\mid$ | $\mid x_i-z_B\mid$ | Cluster |
|:---:|:---:|:---:|:---:|
| 2    | 2,5  | 9,5  | A |
| 4    | 0,5  | 7,5  | A |
| 5    | 0,5  | 6,5  | A |
| 7    | 2,5  | 4,5  | A |
| 8    | 3,5  | 3,5  | A (Gleichstand) |
| 9    | 4,5  | 2,5  | B |
| 11,5 | 7    | 0    | B |
| 12   | 7,5  | 0,5  | B |
| 13,5 | 9    | 2    | B |
| 15   | 10,5 | 3,5  | B |

Neue Zentren:

$z_A = \frac{2+4+5+7+8}{5} = \frac{26}{5} = 5{,}2$

$z_B = \frac{9+11{,}5+12+13{,}5+15}{5} = \frac{61}{5} = 12{,}2$

**3. Iteration**

Alte Zentren: $z_A = 5{,}2$ und $z_B = 12{,}2$

| Wert | $\mid x_i-z_A\mid$ | $\mid x_i-z_B\mid$ | Cluster |
|:---:|:---:|:---:|:---:|
| 2    | 3,2  | 10,2 | A |
| 4    | 1,2  | 8,2  | A |
| 5    | 0,2  | 7,2  | A |
| 7    | 1,8  | 5,2  | A |
| 8    | 2,8  | 4,2  | A |
| 9    | 3,8  | 3,2  | B |
| 11,5 | 6,3  | 0,7  | B |
| 12   | 6,8  | 0,2  | B |
| 13,5 | 8,3  | 1,3  | B |
| 15   | 9,8  | 2,8  | B |

Die Zuordnung der Werte zu den Clustern hat sich gegenüber der vorherigen Iteration nicht verändert. Damit bleiben auch die Clusterzentren unverändert. Das Verfahren konvergiert.

Die endgültigen Clusterzentren sind:

$\boxed{z_A = 5{,}2 \qquad z_B = 12{,}2}$

## Eindimensional, 12 Werte, 3 Zentren

### Aufgabe

Gegeben sind die Werte

1; 2,5; 4; 6,5; 7; 7,5; 8; 11; 11,5; 14; 16,5; 17

und die Startzentren $z_A = 1$, $z_B = 4$ und $z_C = 7$.

Führe das K-Means-Verfahren bis zur Konvergenz durch.


### Musterlösung

**1. Iteration**

Alte Zentren: $z_A = 1$, $z_B = 4$ und $z_C = 7$

| Wert | $\mid x_i-z_A\mid$ | $\mid x_i-z_B\mid$ | $\mid x_i-z_C\mid$ | Cluster |
|:---:|:---:|:---:|:---:|:---:|
| 1    | 0    | 3    | 6    | A |
| 2,5  | 1,5  | 1,5  | 4,5  | A (Gleichstand) |
| 4    | 3    | 0    | 3    | B |
| 6,5  | 5,5  | 2,5  | 0,5  | C |
| 7    | 6    | 3    | 0    | C |
| 7,5  | 6,5  | 3,5  | 0,5  | C |
| 8    | 7    | 4    | 1    | C |
| 11   | 10   | 7    | 4    | C |
| 11,5 | 10,5 | 7,5  | 4,5  | C |
| 14   | 13   | 10   | 7    | C |
| 16,5 | 15,5 | 12,5 | 9,5  | C |
| 17   | 16   | 13   | 10   | C |

Neue Zentren:

$z_A = \frac{1+2{,}5}{2} = \frac{3{,}5}{2} = 1{,}75$

$z_B = \frac{4}{1} = 4$

$z_C = \frac{6{,}5+7+7{,}5+8+11+11{,}5+14+16{,}5+17}{9} = \frac{99}{9} = 11$

**2. Iteration**

Alte Zentren: $z_A = 1{,}75$, $z_B = 4$ und $z_C = 11$

| Wert | $\mid x_i-z_A\mid$ | $\mid x_i-z_B\mid$ | $\mid x_i-z_C\mid$ | Cluster |
|:---:|:---:|:---:|:---:|:---:|
| 1    | 0,75  | 3    | 10   | A |
| 2,5  | 0,75  | 1,5  | 8,5  | A |
| 4    | 2,25  | 0    | 7    | B |
| 6,5  | 4,75  | 2,5  | 4,5  | B |
| 7    | 5,25  | 3    | 4    | B |
| 7,5  | 5,75  | 3,5  | 3,5  | B (Gleichstand) |
| 8    | 6,25  | 4    | 3    | C |
| 11   | 9,25  | 7    | 0    | C |
| 11,5 | 9,75  | 7,5  | 0,5  | C |
| 14   | 12,25 | 10   | 3    | C |
| 16,5 | 14,75 | 12,5 | 5,5  | C |
| 17   | 15,25 | 13   | 6    | C |

Neue Zentren:

$z_A = \frac{1+2{,}5}{2} = 1{,}75$

$z_B = \frac{4+6{,}5+7+7{,}5}{4} = \frac{25}{4} = 6{,}25$

$z_C = \frac{8+11+11{,}5+14+16{,}5+17}{6} = \frac{78}{6} = 13$

**3. Iteration**

Alte Zentren: $z_A = 1{,}75$, $z_B = 6{,}25$ und $z_C = 13$

| Wert | $\mid x_i-z_A\mid$ | $\mid x_i-z_B\mid$ | $\mid x_i-z_C\mid$ | Cluster |
|:---:|:---:|:---:|:---:|:---:|
| 1    | 0,75  | 5,25  | 12   | A |
| 2,5  | 0,75  | 3,75  | 10,5 | A |
| 4    | 2,25  | 2,25  | 9    | A (Gleichstand) |
| 6,5  | 4,75  | 0,25  | 6,5  | B |
| 7    | 5,25  | 0,75  | 6    | B |
| 7,5  | 5,75  | 1,25  | 5,5  | B |
| 8    | 6,25  | 1,75  | 5    | B |
| 11   | 9,25  | 4,75  | 2    | C |
| 11,5 | 9,75  | 5,25  | 1,5  | C |
| 14   | 12,25 | 7,75  | 1    | C |
| 16,5 | 14,75 | 10,25 | 3,5  | C |
| 17   | 15,25 | 10,75 | 4    | C |

Neue Zentren:

$z_A = \frac{1+2{,}5+4}{3} = \frac{7{,}5}{3} = 2{,}5$

$z_B = \frac{6{,}5+7+7{,}5+8}{4} = \frac{29}{4} = 7{,}25$

$z_C = \frac{11+11{,}5+14+16{,}5+17}{5} = \frac{70}{5} = 14$

**4. Iteration**

Alte Zentren: $z_A = 2{,}5$, $z_B = 7{,}25$ und $z_C = 14$

| Wert | $\mid x_i-z_A\mid$ | $\mid x_i-z_B\mid$ | $\mid x_i-z_C\mid$ | Cluster |
|:---:|:---:|:---:|:---:|:---:|
| 1    | 1,5  | 6,25 | 13   | A |
| 2,5  | 0    | 4,75 | 11,5 | A |
| 4    | 1,5  | 3,25 | 10   | A |
| 6,5  | 4    | 0,75 | 7,5  | B |
| 7    | 4,5  | 0,25 | 7    | B |
| 7,5  | 5    | 0,25 | 6,5  | B |
| 8    | 5,5  | 0,75 | 6    | B |
| 11   | 8,5  | 3,75 | 3    | C |
| 11,5 | 9    | 4,25 | 2,5  | C |
| 14   | 11,5 | 6,75 | 0    | C |
| 16,5 | 14   | 9,25 | 2,5  | C |
| 17   | 14,5 | 9,75 | 3    | C |

Die Zuordnung der Werte zu den Clustern hat sich gegenüber der vorherigen Iteration nicht verändert. Damit bleiben auch die Clusterzentren unverändert. Das Verfahren konvergiert.

Die endgültigen Clusterzentren sind:

$\boxed{z_A = 2{,}5 \qquad z_B = 7{,}25 \qquad z_C = 14}$

## Zweidimensional, 6 Werte, 2 Zentren

### Aufgabe

Gegeben sind die Punkte

$P_1(1\mid 0)$, $P_2(4\mid 0)$, $P_3(4\mid 5)$, $P_4(7\mid 3)$, $P_5(8\mid 5)$, $P_6(10\mid 7)$

und die Startzentren $z_A = (4\mid 3)$ und $z_B = (3\mid 6)$.

Führe das K-Means-Verfahren bis zur Konvergenz durch.

Es ist $d^2(P,z) = (x_P-x_z)^2 + (y_P-y_z)^2$.


### Musterlösung

**1. Iteration**

Alte Zentren: $z_A = (4\mid 3)$ und $z_B = (3\mid 6)$

| Punkt | $d^2(P,z_A)$ | $d^2(P,z_B)$ | Cluster |
|:---:|:---:|:---:|:---:|
| $P_1(1\mid 0)$  | 18 | 40 | A |
| $P_2(4\mid 0)$  | 9  | 37 | A |
| $P_3(4\mid 5)$  | 4  | 2  | B |
| $P_4(7\mid 3)$  | 9  | 25 | A |
| $P_5(8\mid 5)$  | 20 | 26 | A |
| $P_6(10\mid 7)$ | 52 | 50 | B |

Neue Zentren:

$z_A = \left(\frac{1+4+7+8}{4} \,\Big|\, \frac{0+0+3+5}{4}\right) = \left(\frac{20}{4} \,\Big|\, \frac{8}{4}\right) = (5\mid 2)$

$z_B = \left(\frac{4+10}{2} \,\Big|\, \frac{5+7}{2}\right) = \left(\frac{14}{2} \,\Big|\, \frac{12}{2}\right) = (7\mid 6)$

**2. Iteration**

Alte Zentren: $z_A = (5\mid 2)$ und $z_B = (7\mid 6)$

| Punkt | $d^2(P,z_A)$ | $d^2(P,z_B)$ | Cluster |
|:---:|:---:|:---:|:---:|
| $P_1(1\mid 0)$  | 20 | 72 | A |
| $P_2(4\mid 0)$  | 5  | 45 | A |
| $P_3(4\mid 5)$  | 10 | 10 | A (Gleichstand) |
| $P_4(7\mid 3)$  | 5  | 9  | A |
| $P_5(8\mid 5)$  | 18 | 2  | B |
| $P_6(10\mid 7)$ | 50 | 10 | B |

Neue Zentren:

$z_A = \left(\frac{1+4+4+7}{4} \,\Big|\, \frac{0+0+5+3}{4}\right) = \left(\frac{16}{4} \,\Big|\, \frac{8}{4}\right) = (4\mid 2)$

$z_B = \left(\frac{8+10}{2} \,\Big|\, \frac{5+7}{2}\right) = \left(\frac{18}{2} \,\Big|\, \frac{12}{2}\right) = (9\mid 6)$

**3. Iteration**

Alte Zentren: $z_A = (4\mid 2)$ und $z_B = (9\mid 6)$

| Punkt | $d^2(P,z_A)$ | $d^2(P,z_B)$ | Cluster |
|:---:|:---:|:---:|:---:|
| $P_1(1\mid 0)$  | 13 | 100 | A |
| $P_2(4\mid 0)$  | 4  | 61  | A |
| $P_3(4\mid 5)$  | 9  | 26  | A |
| $P_4(7\mid 3)$  | 10 | 13  | A |
| $P_5(8\mid 5)$  | 25 | 2   | B |
| $P_6(10\mid 7)$ | 61 | 2   | B |

Die Zuordnung der Punkte zu den Clustern hat sich gegenüber der vorherigen Iteration nicht verändert. Damit bleiben auch die Clusterzentren unverändert. Das Verfahren konvergiert.

Die endgültigen Clusterzentren sind:

$\boxed{z_A = (4\mid 2) \qquad z_B = (9\mid 6)}$