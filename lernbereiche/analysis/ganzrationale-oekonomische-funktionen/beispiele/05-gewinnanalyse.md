---
layout: null
permalink: /lernbereiche/analysis/ganzrationale-oekonomische-funktionen/beispiele/05-gewinnanalyse.html
---
Velotec ist alleinige Anbieterin eines patentierten Faltanhängers. Es gilt $K(x)=0{,}5x^3-6x^2+30x+48$. Der Höchstpreis beträgt 84 GE/ME, mit jeder zusätzlich abgesetzten ME sinkt der erzielbare Preis um 6 GE/ME.

- Funktionen aufstellen

    Aus Höchstpreis und Preisrückgang ergibt sich die Preis-Absatz-Funktion, daraus Erlös und Gewinn:

    $$
    \begin{align*}
    p(x)&=-6x+84\\
    E(x)&=p(x)\cdot x=-6x^2+84x\\
    G(x)&=E(x)-K(x)=-0{,}5x^3+54x-48
    \end{align*}
    $$

- Cournotscher Punkt

    Zuerst die gewinnmaximale Menge mit $G^{\prime}(x)=-1{,}5x^2+54$ und $G^{\prime\prime}(x)=-3x$:

    $$
    \begin{align*}
    \text{Notwendige Bedingung: }& -1{,}5x^2+54=0 \Rightarrow x_1=-6,\ x_2=6\\
    \text{Hinreichende Bedingung: }& G^{\prime\prime}(6)=-18<0 \text{ (Maximum)}
    \end{align*}
    $$

    Der zugehörige Preis ist $p(6)=-6\cdot6+84=48$. Der Cournotsche Punkt ist $C(6\mid 48)$: Velotec verdient am meisten, wenn es 600 Anhänger zu je 480 € anbietet.

- Mengenbereich mit einem Gewinn von mindestens 100 GE

    $$
    \begin{align*}
    G(x)&=100\\
    -0{,}5x^3+54x-48&=100\\
    -0{,}5x^3+54x-148&=0 \Rightarrow x_1\approx-11{,}56,\ x_2\approx2{,}99,\ x_3\approx8{,}57
    \end{align*}
    $$

    $x_1$ liegt nicht im ökonomischen Definitionsbereich. Zwischen den beiden anderen Lösungen liegt der Hochpunkt von $G$, dort ist der Gewinn größer als 100 GE. Bei Absatzmengen zwischen 2,99 ME und 8,57 ME beträgt der Gewinn mindestens 100 GE.

- Patent läuft aus

    Nach Ablauf des Patents bieten weitere Unternehmen den Anhänger an, der Marktpreis liegt dann bei 32 GE/ME. Es gilt nun $G_P(x)=32x-K(x)=-0{,}5x^3+6x^2+2x-48$ mit $G_P^{\prime}(x)=-1{,}5x^2+12x+2$ und $G_P^{\prime\prime}(x)=-3x+12$:

    $$
    \begin{align*}
    -1{,}5x^2+12x+2=0 &\Rightarrow x_1\approx-0{,}16,\ x_2\approx8{,}16\\
    G_P^{\prime\prime}(8{,}16)\approx-12{,}49&<0 \text{ (Maximum)}\\
    G_P(8{,}16)&\approx96{,}16
    \end{align*}
    $$

    Die gewinnmaximale Menge steigt auf 8,16 ME, der maximale Gewinn sinkt um $168-96{,}16=71{,}84$ GE.
