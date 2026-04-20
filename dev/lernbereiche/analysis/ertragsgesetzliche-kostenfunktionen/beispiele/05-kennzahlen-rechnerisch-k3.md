---
layout: null
---
Berechnung Kostenkennzahlen für $K(x)=0{,}5x^3 - 6x^2 + 30x + 48$:

Wir bestimmen zunächst:

- Grenzkosten: $K'(x) = 1{,}5x^2-12x+30$
- variablen Stückkosten: $k_v(x)=0{,}5x^2 - 6x + 30 $
- Stückkosten: $k(x)=0{,}5x^2 - 6x + 30 + \frac{48}{x}$

- Übergang vom degressiven zum progressiven Kostenwachstum: Wendestelle von $K(x)=0{,}5x^3-6x^2+30x+48$

    Bestimme $K^{\prime\prime}(x)=3x-12$ und $K^{\prime\prime\prime}(x)=3$.

    $$
    \begin{align*}
    3x - 12 &=  0 \Rightarrow x = 4\\
    K^{\prime\prime\prime}(4)&=3 > 0 \text{ (minimale Steigung)}
    \end{align*}
    $$

    Der Übergang vom degressiven zum progressiven Kostenwachstum findet bei 4 ME statt.

- Betriebsminimum: Extremstelle von $k_v(x)=0{,}5x^2 - 6x + 30$

    Bestimme $k_v'(x)=x-6$ und $k_v^{\prime\prime}(x)=1$.

    $$
    \begin{align*}
    x-6&=0 \Rightarrow x = 6\\
    k_v^{\prime\prime}(6)&=1 > 0 (\text{ Minimum})
    \end{align*}
    $$

    Das Betriebsminimum beträgt 6 ME.

- Kurzfristige Preisuntergrenze: Minimum von $k_v(x)$.

    Einsetzen des Betriebsminimums in $k_v(x)$:

    $$
    k_v(6) =  12
    $$

    Die kurzristige Preisuntergrenze beträgt 12 GE / ME.

- Betriebsoptimum: Extremstelle von $k(x)=0{,}5x^2 - 6x + 30 + \frac{48}{x}$

    Bestimme $k'(x)=x-6-\frac{48}{x^2}$ und $k^{\prime\prime}(x)=1+\frac{96}{x^3}$.

    $$
    \begin{align*}
    x-6-\frac{48}{x^2} &= 0\quad |\cdot(x^2)\\
    x^3-6x^2-48&0 \Rightarrow x = 6{,}98\\
    k^{\prime\prime}(6{,}98)&=1{,}8 > 0 (\text{ Minimum})
    \end{align*}
    $$

    Das Betriebsoptimum beträgt 6,98 ME.

- Langfristige Preisuntergrenze: Minimum von $k(x)$.

    Einsetzen des Betriebsoptimums in $k(x)$:

    $$
    k(6{,}98) =  19{,}36
    $$

    Die langfristige Preisuntergrenze beträgt 19,36 GE / ME.
