---
layout: null
permalink: /lernbereiche/analysis/produktlebenszyklus/beispiele/03-kennzahlen-rechnerisch-gesamt.html
---
Der monatliche Absatz eines Produkts wird beschrieben durch

$$
a(t)=(4t+2)\cdot e^{-0{,}2t}+3 \qquad (t \text{ in Monaten},\ a(t) \text{ in ME/Monat})
$$

mit den Ableitungen

$$
\begin{align*}
a'(t) &= (-0{,}8t+3{,}6)\cdot e^{-0{,}2t}\\
a''(t) &= (0{,}16t-1{,}52)\cdot e^{-0{,}2t}
\end{align*}
$$

- **Absatz bei Markteinführung**

    $$
    a(0)=(4\cdot 0+2)\cdot e^{0}+3=5 \text{ ME/Monat}
    $$

- **Zeitpunkt und Höhe des höchsten Absatzes**

    Notwendige Bedingung $a'(t)=0$. Da $e^{-0{,}2t}\neq 0$, genügt es, den Klammerterm null zu setzen:

    $$
    -0{,}8t+3{,}6=0 \quad\Leftrightarrow\quad t=4{,}5
    $$

    Hinreichende Bedingung: Der Klammerterm $-0{,}8t+3{,}6$ wechselt bei $t=4{,}5$ das Vorzeichen von $+$ nach $-$ (alternativ: $a''(4{,}5)\approx-0{,}33<0$). Also liegt ein Maximum vor:

    $$
    a(4{,}5)=20\cdot e^{-0{,}9}+3\approx 11{,}13 \text{ ME/Monat}
    $$

    Nach $4{,}5$ Monaten wird mit ca. $11{,}13$ ME/Monat der höchste Absatz erreicht.

- **Stärkster Rückgang und stärkster Anstieg**

    Notwendige Bedingung $a''(t)=0$:

    $$
    0{,}16t-1{,}52=0 \quad\Leftrightarrow\quad t=9{,}5
    $$

    Der Klammerterm wechselt bei $t=9{,}5$ das Vorzeichen von $-$ nach $+$, also hat $a'$ dort ein Minimum. Mit $a'(9{,}5)=-4\cdot e^{-1{,}9}\approx-0{,}60<0$ geht der Absatz nach $9{,}5$ Monaten am stärksten zurück, um ca. $0{,}60$ ME/Monat pro Monat.

    Einen weiteren Wendepunkt gibt es nicht. Für $0\le t<9{,}5$ ist $a''(t)<0$, d. h. $a'$ fällt dort. Der stärkste Anstieg liegt deshalb am Rand, bei der Markteinführung: $a'(0)=3{,}6$ ME/Monat pro Monat.

- **Langfristiger Absatz**

    Für $t\to\infty$ gilt $(4t+2)\cdot e^{-0{,}2t}\to 0$, weil die $e$-Funktion schneller gegen $0$ geht, als der lineare Term wächst:

    $$
    \lim_{t\to\infty} a(t)=0+3=3 \text{ ME/Monat}
    $$

    Das Produkt wird nicht vom Markt genommen, langfristig werden ca. $3$ ME pro Monat abgesetzt.

- **Zeitraum mit einem Absatz von mehr als $10$ ME/Monat** (mit Rechner)

    $$
    a(t)=10 \quad\Rightarrow\quad t_1\approx 2{,}24 \qquad t_2\approx 7{,}76
    $$

    Da das Maximum $a(4{,}5)\approx 11{,}13>10$ dazwischen liegt, beträgt der Absatz für $2{,}24<t<7{,}76$, also gut $5{,}5$ Monate lang, mehr als $10$ ME/Monat.
