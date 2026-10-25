---
layout: null
permalink: /lernbereiche/analysis/marktgleichgewicht-vertiefung/beispiele/04-renten-bestimmung-prkr.html
---
Gegeben sind die Nachfragefunktion $p_N$ und die Angebotsfunktion $p_A$ mit

$$
\begin{align*}
p_N(x)&=60e^{-0{,}05x}\\
p_A(x)&=0{,}05x^2+x+10.
\end{align*}
$$

Berechnen Sie die Konsumenten- und die Produzentenrente und deuten Sie die Ergebnisse im Sachzusammenhang.

**Marktgleichgewicht**

$$
\begin{align*}
60e^{-0{,}05x}&=0{,}05x^2+x+10 \quad |\text{ CAS}\\
x_G&\approx 12{,}97\\
p_G&=p_N(12{,}97)\approx 31{,}37
\end{align*}
$$

Der Umsatz im Marktgleichgewicht beträgt $x_G\cdot p_G\approx 406{,}83$ GE.

**Konsumentenrente**

$$
\begin{align*}
KR&=\int_0^{x_G}p_N(x)\,dx-x_G\cdot p_G\\
  &=\int_0^{12{,}97}60e^{-0{,}05x}\,dx-12{,}97\cdot 31{,}37\\
  &\approx 572{,}51-406{,}83\\
  &=165{,}68
\end{align*}
$$

**Produzentenrente**

$$
\begin{align*}
PR&=x_G\cdot p_G-\int_0^{x_G}p_A(x)\,dx\\
  &=12{,}97\cdot 31{,}37-\int_0^{12{,}97}(0{,}05x^2+x+10)\,dx\\
  &\approx 406{,}83-250{,}08\\
  &=156{,}75
\end{align*}
$$

Die Integrale und Produkte sind mit den ungerundeten Werten von $x_G$ und $p_G$ berechnet.

**Deutung**

Die Konsumentenrente beträgt etwa $165{,}68$ GE. Um diesen Betrag sparen die Konsumenten, die bereit gewesen wären, mehr als den Gleichgewichtspreis von $31{,}37$ GE/ME zu zahlen. Die Produzentenrente beträgt etwa $156{,}75$ GE. Diesen Betrag nehmen die Produzenten zusätzlich ein, die auch zu einem niedrigeren Preis angeboten hätten. Die Konsumentenrente ist etwas größer als die Produzentenrente.
