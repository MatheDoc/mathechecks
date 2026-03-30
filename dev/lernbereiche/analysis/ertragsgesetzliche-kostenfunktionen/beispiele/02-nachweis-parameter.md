---
layout: null
---
Für welche Parameter ist $K_a(x)=x^3-9x^2+ax+60$ ertragsgesetzlich?

- Da $K_a(0)=60$ für alle $a$ liegt immer ein positiver y-Abschnitt vor.
- Da $K_a^{\prime\prime}(x)=6x-18$ und $6x-18=0$ falls $x=3$ ist die Wendestelle immer positiv.
- Zur Monotonie: Wir berechnen die Nullstellen von $K_a'(x)=3x^2-18x+a$.

$$
\begin{align*}
3x^2-18x+a&=0\quad |:(3)\\
x^2-6x+\frac{a}{3}&=0\quad |\text{ pq-Formel}\\
x_{1,2}&=-\frac{-6}{2}\pm\sqrt{\left(\frac{-6}{2}\right)^2-\frac{a}{3}}\\
x_{1,2}&=3\pm\sqrt{9-\frac{a}{3}}
\end{align*}
$$

Die Funktion $K_a$ ist genau dann monoton wachsend, wenn der Leitkoeffizient positiv ist und keine Extremstellen existieren. Dies ist genau dann der Fall, falls der Term unter der Wurzel nicht positiv ist, d.h. falls

$$
\begin{align*}
9-\frac{a}{3}&\leq 0\quad |+\frac{a}{3}\\
9&\leq \frac{a}{3}\quad |\cdot 3\\
27&\leq a
\end{align*}
$$

Also hat $K_a(x)$ einen ertragsgesetzlichen Verlauf, falls $a\geq 27$ ist.