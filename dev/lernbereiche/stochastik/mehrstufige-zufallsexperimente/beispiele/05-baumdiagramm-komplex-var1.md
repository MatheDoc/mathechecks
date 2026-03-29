---
layout: null
---

Für eine statistische Untersuchung wurden in einem großen Elektronikfachmarkt Aufzeichnungen über die Verkäufe von Laptops mit Windows (W)- bzw. macOS (m)-Betriebssystem geführt. Zusätzlich wurden drei Gerätekategorien erfasst: Einsteigergeräte (E), Mittelklassegeräte (M) und Premiumgeräte (P). Von den Einsteigergeräten liefen ein Fünftel und von den Mittelklassegeräten die Hälfe mit Windows. Von den insgesamt 80.000 erfassten Laptops waren 45 % mit Windows ausgestattet, es wurden 16.000 Einsteigergeräte und 8.000 Premiumgeräte verkauft. Wie sieht das vollständig ausgefüllte Baumdiagramm aus?

Zunächst erstellen wir das Baumdiagramm und tragen die gegebenen Wahrscheinlichkeiten ein:

<figure>
<img src='Elektronikfachmarkt.png'>
</figure>

- Welchen Wert hat $y$ ?

    Da insgesamt 45 % der Laptops mit Windows ausgestattet sind, gilt
    $$
    0{,}04+0{,}35+y=0{,}45 \Rightarrow y=0{,}06.
    $$

- Welchen Wert hat $x$ ?

    Die Multiplikationsregel auf den $PW$-Pfad angewendet ergibt
    $$
    0{,}1\cdot x = 0{,}06 \Rightarrow x=0{,}6.
    $$

- Welchen Wert hat $z$ ?

    Die Multiplikationsregel auf den $Pm$-Pfad angewendet ergibt
    $$
    z=0{,}1\cdot (1-0{,}6)=0{,}04.
    $$
            
Nun könnten wir Wahrscheinlichkeiten im Sachzusammenhang berechnen. Zum Beispiel die Wahrscheinlichkeit, des Ereignisses $E$, dass ein zufällig ausgewählter Laptop mit Windows läuft:
  
$$
\begin{align*}
  P(E)&=P(\{EW\})+P(\{Em\})+P(\{Mm\})+P(\{Pm\})\\
  &=0{,}04+0{,}16+0{,}35+0{,}04\\
  &=0{,}59
\end{align*}
$$