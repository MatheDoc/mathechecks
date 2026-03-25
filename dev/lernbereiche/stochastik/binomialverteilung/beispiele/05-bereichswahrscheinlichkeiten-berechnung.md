Wir suchen die Wahrscheinlichkeiten der angegebnen Ereignisse

1. mit Hilfe kumulierter Wahrscheinlichkeiten,
2. mit Hilfe des Taschenrechners.

Die Basketballspielerin erzielt (weiterhin ist $n=20$ und $p=0{,}1$)


#### genau 6 Treffer. 

$$
\begin{align*}
P(X=6) &= P(X\leq 6) - P(X\leq 5) = 0{,}9976 - 0{,}9887 = 0{,}0089 \\
P(X=6) &= Bcd(6;6;20;0{,}1) = 0{,}0089
\end{align*}
$$

#### höchstens 4 Treffer.

$$
\begin{align*}
P(X\leq 4) &= 0{,}9568 \\
P(X\leq 4) &= Bcd(0;4;20;0{,}1) = 0{,}9568
\end{align*}
$$

#### mindestens 6 Treffer.

$$
\begin{align*}
P(X\geq 6) &= 1 - P(X\leq 5)=1-0{,}9887= 0{,}0113 \\
P(X\geq 6) &= Bcd(6;20;20;0{,}1) = 0{,}0113
\end{align*}
$$


#### weniger als 3 Treffer.

$$
\begin{align*}
P(X<3) &= P(X\leq 2)=0{,}6769 \\
P(X<3) &= Bcd(0;2;20;0{,}1) = 0{,}6769
\end{align*}
$$

#### mehr als 3 Treffer.

$$
\begin{align*}
P(X>3) &= 1 - P(X\leq 3)=1-0{,}8670=0{,}1330 \\
P(X>3) &= Bcd(4;20;20;0{,}1) = 0{,}1330
\end{align*}
$$

#### mehr als 1 und höchstens 5 Treffer.

$$
\begin{align*}
P(1 < X \leq 5) &= P(X\leq 5) - P(X\leq 1)=0{,}9887-0{,}3917=0{,}5970 \\
P(1 < X \leq 5) &= Bcd(2;5;20;0{,}1) = 0{,}5970
\end{align*}
$$

#### einschließlich 3 und ausschließlich 9 Treffer.

$$
\begin{align*}
P(3 \leq X < 9) &= P(X\leq 8) - P(X\leq 2)=0{,}9999-0{,}6769 = 0{,}3230 \\
P(3 \leq X < 9) &= Bcd(3;8;20;0{,}1) = 0{,}3230
\end{align*}
$$

#### weniger als 4 oder mehr als 7 Treffer.
Das gegebene Ereignis setzt sich aus den beiden Ereignisse $X<4$ und $X>7$ zusammen:

$$
\begin{align*}
P(X<4 \text{ oder } X>7) &= P(X\leq 3) + (1 - P(X\leq 7))=0{,}8670 + 0{,}0004=0{,}8674 \\
P(X<4 \text{ oder } X>7) &= Bcd(0;3;20;0{,}1) + Bcd(8;20;20;0{,}1) =0{,}8670 + 0{,}0004=0{,}8674
\end{align*}
$$

#### in höchstens 13% der Würfe Treffer."
Hier berechnen wir zunächst die Intervallgrenzen: $0,13\cdot 20=2,6$. Dann haben wir:

$$
\begin{align*}
P(X \leq 2{,}6) &= P(X \leq 2) = 0{,}6769\\
P(X \leq 2{,}6) &= Bcd(0;2;20;0{,}1) = 0{,}6769
\end{align*}
$$

#### in mehr als einem Drittel der Würfe Treffer.
Hier berechnen wir zunächst die Intervallgrenzen: $\frac{20}{3} \approx 6{,}7$. Dann haben wir:

$$
\begin{align*}
P(X > 6{,}7) &= P(X > 7) = 1 - P(X \leq 6) = 1 - 0{,}9986 = 0{,}0024 \\
P(X > 6{,}7) &= P(X > 7)= Bcd(7;20;20;0{,}1) = 0{,}0024
\end{align*}
$$


#### höchstens 15 Fehlwürfe.

Hier geht es um die Fehlwürfe und nicht um die Treffer. Daher ist hier $p=0{,}9$.

$$
\begin{align*}
P(X \leq 15)&=0{,}0432\\
P(X \leq 15)&=Bcd(0;15;20;0{,}9)=0{,}0432
\end{align*}
$$


#### nur im ersten und letzten Wurf ein Treffer.
Es liegt keine binomialverteilte Zufallsgröße vor, da es nicht um die Anzahl der Treffer von 20 Würfen geht, sondern um eine konkrete Wurffolge: 1. Treffer, 2. Fehlwurf, 2. Fehlwurf,..., 19. Fehlwurf, 20. Treffer. Das Ereignis entpricht also genau einem Pfad im Baumdiagramm.

$$
P(\text{1. und 20. Treffer, Rest Fehlwurf})=0{,}1^2 \cdot 0{,}9^{18}=0{,}0015
$$


#### im 3. und 14. Wurf einen Treffer.
Hier geht es nur um den 3. und 14. Wurf, alles andere ist irrelevant. Daher ist

$$
P(\text{ 3. und 14. Treffer})=0{,}1\cdot 0{,}1=0{,}01
$$
