---
layout: null
---
Welche Funktionen haben einen ertragsgesetzlichen Verkauf?

- $K_1(x)=3x^2+4x+2$

    $K_1(x)$ ist keine Funktion dritten Grades. 👉 nicht-ertragsgesetzlich ❌

- $K_2(x)=0{,}5x^3-6x^2+30x-50$

    $K_2(x)$ besitzt einen negativen y-Abschnitt $y=-50$. 👉 nicht-ertragsgesetzlich ❌

- $K_3(x)=0{,}5x^3-6x^2+15x+48$

    Um zu prüfen, ob $K_3(x)=0{,}5x^3-6x^2+15x+48$ monoton wachsend ist, können wir versuchen Extremstellen zu bestimmen. **Wenn es Extremstellen gibt, dann ist die Funktion nicht monoton wachsend.** Wir berechnen $K_3'(x)=1{,}5x^2-12x^2+15$. Die notwendige Bedignung für Extrema lautet:

    $$
    \begin{align*}
    1{,}5x^2-12x^2+15&=0\quad |:(1{,}5)\\
    5x^2-8x^2+10&=0\quad |\text{ pq-Formel}\\
    x_{1,2}=-\frac{-8}{2}\pm\sqrt{\left(\frac{-8}{2}\right)^2-10}\\
    x_{1,2}=4\pm\sqrt{6}
    \end{align*}
    $$

    Da der Term unter Wurzel positiv ist, existieren die einfachen Nullstellen $x_1$ und $x_2$. Es liegen also Extrema vor. 👉 nicht-ertragsgesetzlich ❌

    (Wären beide Extremstellen negativ, so könnte durchaus im ökonomischen Definitionsbereich ein monotones Wachstum vorliegen. Da aber die Wendestelle positiv sein muss, können wir annehmen, dass zumindest die größere Extremstelle positiv ist.)

- $K_4(x)=0{,}5x^3+1{,}5x^2+7{,}5x+90$

    Wir bestimmen die Wendestelle von $K_4(x)$. Wir haben $K_4^{\prime\prime}(x)=3x+3$ und $K_4^{\prime\prime\prime}(x)=3$. Die notwendige Bedingung lautet:

    $$
    \begin{align*}
    3x+3&=0\\
    x&=-1
    \end{align*}
    $$

    Die hinreichende Bedingung:

    $$
    K_4'''(-1)=3>0\text{ (minimale Steigung)}
    $$

    Die Wendestelle ist also negativ. 👉 nicht-ertragsgesetzlich ❌

- $K_5(x)=0{,}5x^3-6x^2+30x+48$

    - Die Funktion ist ganzrational dritten Grades. ✔️
    - Der y-Achsenabschnitt ist positiv. ✔️
    - Wir versuchen die Extremstellen zu berechnen: Es ist $K_5'(x)=1{,}5x^2-12x+30$. Die notwendige Bedingung lautet

    $$
    \begin{align*}
    1{,}5x^2-12x^2+30&=0\quad |:(1{,}5)\\
    x^2-8x^2+20&=0\quad |\text{ pq-Formel}\\
    x_{1,2}=-\frac{-8}{2}\pm\sqrt{\left(\frac{-8}{2}\right)^2-20}\\
    x_{1,2}=4\pm\sqrt{-4}
    \end{align*}
    $$

    Da der Term unter Wurzel negativ ist, existieren keine Extremstellen. Die Funktion $K_5(x)$ ist also monoton, und zwar monoton wachsend, weil z.B. der Leitkoeffizient $0{,}5>0$ ist. ✔️

    - Wir berechnen die Wendestelle: Es ist $K_5^{\prime\prime}(x)=3x-12$. Die notwendige Bedingung lautet:

    $$
    \begin{align*}
    3x-12&=0\\
    x&=4
    \end{align*}
    $$

    Die hinreichende Bedingung:

    $$
    K_5'''(4)=3>0\text{ (minimale Steigung)}
    $$

    Die Wendestelle $x_w$ ist also positiv. ✔️

    Damit sind alle Kriterien erfüllt. 👉 ertragsgesetzlich ✅
