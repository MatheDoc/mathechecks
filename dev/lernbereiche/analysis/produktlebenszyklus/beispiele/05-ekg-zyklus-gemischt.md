---
layout: null
---
Die Funktionen

$$
\begin{align*}
E(t)&=(-0{,}8t^3+22t^2)\cdot e^{-0{,}2t}\\
K(t)&=(-0{,}4t^3+11t^2)\cdot e^{-0{,}2t}+36{,}5
\end{align*}
$$

geben den jährlichen Erlös und die jährlichen Kosten an. Der Lebenszyklus endet nach 27,5 Jahren. Die Gewinnfunktion $G(t)=E(t)-K(t)$ hat die Form

$$
G(t)=(-0{,}4t^3+11t^2)\cdot e^{-0{,}2t} - 36{,}5.
$$



- Zeitraum der Kostendeckung: Löse $G(t)=0$:

    $$
    \begin{align*}
    (-0{,}4t^3+11t^2)\cdot e^{-0{,}2t} - 36{,}5=0
    t_1 \approx 2{,}43 \quad t_2 \approx 17{,}57 \quad t_3=-1,52
    \end{align*}
    $$

    $t_3=-1,52$ liegt außerhalb des betrachteten Zeitraums, die Kosten im Zeitraum $[2{,}43;\; 17{,}57]$ gedeckt.


- Jährliche Gewinne nach 16 Jahren:

    $$
    G(16) = (-0{,}4\cdot 16^3+11\cdot 16^2)\cdot e^{-3{,}2} - 36{,}5 \approx 11{,}50 \text{ GE}
    $$

- Gesamtgewinn:

    $$
    G_{\text{gesamt}} = \int_0^{27{,}5} G(t)\,dt \approx 305{,}76 \text{ GE (TR)}
    $$

- Maximaler Gesamtverlust: Wir vergleichen die beiden Kandidaten:

    Kandidat 1 – erste Nullstelle $t_1 \approx 2{,}43$:

    $$V
    \int_0^{2{,}43} G(t)\,dt \approx -54{,}36 \text{ GE (TR)}
    $$

    Kandidat 2 – Ende des Lebenszyklus $T = 27{,}5$:

    $$
    \int_0^{27{,}5} G(t)\,dt = \approx 305{,}76 \text{ GE}
    $$

    Da

    $$
    \int_0^{2{,}43} G(t)\,dt < \int_0^{27{,}5} G(t)\,dt
    $$

    liegt der maximale Gesamtverlust nach ca. $2{,}43$ Jahren auf und beträgt ca. $54{,}36$ GE.