---
layout: null
---
In einem zweistufigen Produktionsprozess werden aus den Rohstoffen R1 (Silizium), R2 (Lithium) und R3 (Glas) die Zwischenprodukte Z1 (Chip), Z2 (Akku) und Z3 (Display) hergestellt, aus denen die Endprodukte E1 (Alpha) und E2 (Beta) zusammengesetzt werden.

Im Verflechtungsdiagramm sind einige Pfeile mit Zahlenwerten beschriftet, andere mit eingekreisten Nummern markiert. In den Produktionsmatrizen sind die zugehörigen Stellen jeweils vertauscht:

$$
RZ = \begin{pmatrix} 5 & \text{①} & 1 \\ 0 & 4 & 0 \\ \text{②} & 0 & 6 \end{pmatrix}, \quad
ZE = \begin{pmatrix} 2 & \text{③} \\ 1 & 2 \\ 1 & 2 \end{pmatrix}
$$

Im Verflechtungsdiagramm liest man auf den entsprechenden Pfeilen folgende Werte ab:
- Pfeil R1 → Z2 zeigt den Wert 2 (für ①)
- Pfeil R3 → Z1 zeigt den Wert 1 (für ②)
- Pfeil Z1 → E2 zeigt den Wert 3 (für ③)

**Frage:** Bestimmen Sie ①, ② und ③.

**Lösung:**

**①:** In der Matrix $RZ$ steht ① in der 1. Zeile (R1 = Silizium) und 2. Spalte (Z2 = Akku). Der zugehörige Pfeil im Verflechtungsdiagramm führt von R1 nach Z2 und zeigt den Wert 2. Also ist **① = 2**.

**②:** In $RZ$ steht ② in der 3. Zeile (R3 = Glas) und 1. Spalte (Z1 = Chip). Der Pfeil von R3 nach Z1 im Diagramm zeigt den Wert 1. Also ist **② = 1**.

**③:** In $ZE$ steht ③ in der 1. Zeile (Z1 = Chip) und 2. Spalte (E2 = Beta). Der Pfeil von Z1 nach E2 im Diagramm zeigt den Wert 3. Also ist **③ = 3**.
