---
layout: null
permalink: /lernbereiche/lineare-algebra/mehrstufige-produktionsprozesse/beispiele/01-verflechtungsdiagramm-matrizen.html
---
In einem zweistufigen Produktionsprozess werden aus den Rohstoffen R1 (Silizium), R2 (Lithium) und R3 (Glas) die Zwischenprodukte Z1 (Chip), Z2 (Akku) und Z3 (Display) hergestellt, aus denen die Endprodukte E1 (Alpha) und E2 (Beta) zusammengesetzt werden.

<div class="verflechtungsdiagramm-auto"
  data-rohstoffe='["R1","R2","R3"]'
  data-zwischenprodukte='["Z1","Z2","Z3"]'
  data-endprodukte='["E1","E2"]'
  data-stufe1='[[0,0,"5"],[0,1,"2"],[0,2,"1"],[1,1,"4"],[2,0,"1"],[2,2,"6"]]'
  data-stufe2='[[0,0,"2"],[0,1,"c"],[1,0,"1"],[1,1,"2"],[2,0,"1"],[2,1,"2"]]'>
</div>

Die gesuchten Werte sind mit $a$, $b$ und $c$ bezeichnet. Jeder gesuchte Wert ist entweder im Verflechtungsdiagramm oder in einer Produktionsmatrix ablesbar:

$$
RZ = \begin{pmatrix} 5 & a & 1 \\ 0 & 4 & 0 \\ b & 0 & 6 \end{pmatrix}, \quad
ZE = \begin{pmatrix} 2 & 3 \\ 1 & 2 \\ 1 & 2 \end{pmatrix}
$$

**Frage:** Bestimmen Sie $a$, $b$ und $c$.

**Lösung:**

**$a$:** In der Matrix $RZ$ steht $a$ in der 1. Zeile (R1 = Silizium) und 2. Spalte (Z2 = Akku). Der zugehörige Pfeil im Verflechtungsdiagramm führt von R1 nach Z2 und zeigt den Wert 2. Also ist $a = 2$.

**$b$:** In $RZ$ steht $b$ in der 3. Zeile (R3 = Glas) und 1. Spalte (Z1 = Chip). Der Pfeil von R3 nach Z1 im Diagramm zeigt den Wert 1. Also ist $b = 1$.

**$c$:** Der Pfeil mit $c$ führt im Diagramm von Z1 (Chip) nach E2 (Beta). In $ZE$ steht der zugehörige Wert in der 1. Zeile und 2. Spalte. Dort liest man 3 ab. Also ist $c = 3$.
