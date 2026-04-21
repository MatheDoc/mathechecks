---
layout: null
---
Gegeben sei die Umsatzfunktion

$$
u(t)=(-2t^2+24t)\cdot e^{-0{,}2t}
$$

mit den Ableitungen:

$$
\begin{align*}
u^{\prime}(t) &= (0{,}4t^2-8{,}8t+24)\cdot e^{-0{,}2t}\\
u^{\prime\prime}(t) &= (-0{,}08t^2+2{,}56t-13{,}6)\cdot e^{-0{,}2t}\\
u^{\prime\prime\prime}(t) &= (0{,}016t^2-0{,}64t+2{,}56)\cdot e^{-0{,}2t}
\end{align*}
$$

- Umsatz bei Produkteinführung

    $$
    u(0)=(-2\cdot 0^2+24\cdot 0)\cdot e^{0}=0 \text{ GE}
    $$

- Marktaustritt und langfristiger Umsatz

    Für den Marktaustritt lösen wir $u(t)=0$ mit $t > 0$. Da $e^{-0{,}2t}\neq 0$:

    $$
    \begin{align*}
    -2t^2+24t &= 0\\
    t(-2t+24) &= 0\\
    t_1 = 0 \quad&\quad t_2 = 12
    \end{align*}
    $$

    Das Produkt wird nach $12$ Jahren vom Markt genommen.

    Hinweis: Bei Funktionen der Form $u(t)=p(t)\cdot e^{-ct}+d$ mit $d>0$ gibt es keinen Marktaustritt. Stattdessen gilt $\lim\limits_{t\to\infty} u(t)=d$ (langfristiger Umsatz).

- Maximaler jährlicher Umsatz

    Notwendige Bedingung $u^{\prime}(t)=0$:

    $$
    \begin{align*}
    0{,}4t^2-8{,}8t+24 &= 0 \quad |:0{,}4\\
    t^2-22t+60 &= 0 \quad |\text{ pq-Formel}\\
    t_{1{,}2} &= 11\pm\sqrt{121-60}\\
    t_1 &\approx 3{,}19 \quad t_2 \approx 18{,}81
    \end{align*}
    $$

    Nur $t_1 \approx 3{,}19$ liegt im Produktlebenszyklus $[0;\,12]$.

    Hinreichende Bedingung: $u^{\prime\prime}(3{,}19) \approx -3{,}3< 0$ ✓ (Maximum)

    $$u(3{,}19) \approx (-2\cdot 3{,}19^2+24\cdot 3{,}19)\cdot e^{-0{,}2\cdot 3{,}19} \approx 29{,}64 \text{ GE}$$

    Der höchste jährliche Umsatz beträgt ca. $29{,}64$ GE nach ca. $3{,}19$ Jahren.

- Stärkster Umsatzanstieg und -rückgang

    Notwendige Bedingung: $u^{\prime\prime}(t)=0$:

    $$
    \begin{align*}
    -0{,}08t^2+2{,}56t-13{,}6 &= 0 \quad |:(-0{,}08)\\
    t^2-32t+170 &= 0 \quad |\text{ pq-Formel}\\
    t_{1{,}2} &= 16 \pm\sqrt{256-170}\\
    t_1 &\approx 6{,}73 \quad t_2 \approx 25{,}27
    \end{align*}
    $$

    Nur $t_1 \approx 6{,}73$ liegt im Produktlebenszyklus.
    
    Hinreichende Bedingung: $u^{\prime\prime\prime}(6{,}73) \approx 0{,}39 < 0$ ✓ (minimale Steigung)

    Es gilt $u^{\prime}(6{,}73) \approx -4{,}45 < 0$, also handelt es sich tatsächlich um einen Umsatzrückgang.

    Für den stärksten Umsatzanstieg prüfen wir den Rand: $u^{\prime}(0)=24 > 0$. Der stärkste Anstieg liegt bei $t=0$, da der Graph degressiv wächst.
