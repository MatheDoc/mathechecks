---
layout: null
permalink: /lernbereiche/analysis/differentialrechnung-ganzrationaler-funktionen/beispiele/08-extremstellen-monotonie-spezialfaelle.html
---

Untersuche die Funktion $f(x)=x^4-6x^2+8x$ auf Hochpunkt, Tiefpunkt, Sattelpunkt und Monotonie.

**Erste und zweite Ableitung berechnen**

$$\begin{aligned}
f'(x) &= 4x^3-12x+8 = 4(x+2)(x-1)^2 \\
f''(x) &= 12x^2-12 = 12(x+1)(x-1)
\end{aligned}$$

**Kandidatenstellen bestimmen**

$$f'(x)=0 \quad\Rightarrow\quad 4(x+2)(x-1)^2=0 \quad\Rightarrow\quad x=-2 \text{ oder } x=1$$

**Einfache Extremstelle prüfen**

$$f''(-2)=36>0$$

Also liegt bei $x=-2$ ein Tiefpunkt vor.

**Spezialfall bei $x=1$ untersuchen**

$$f''(1)=0$$

Der Test mit der zweiten Ableitung entscheidet hier also nicht. Deshalb betrachten wir den Vorzeichenwechsel von $f'$.

**Graph von $f'$ und Vorzeichentabelle**

<div class="diagramm-row">
    <div style="flex: 1 1 420px; min-width: 0;">
        {% include graph.html
                         funktionen='[{"name":"f\u2032", "term":"4*(x+2)*(x-1)^2", "color":"#4363d8"}]'
             titel="Graph der ersten Ableitung f′"
                             xmin=-2.5 xmax=2.5 ymin=-5 ymax=20
        %}
    </div>
    <div style="flex: 1 1 320px; min-width: 0;">
        <table>
            <thead>
                <tr>
                    <th>Bereich</th>
                    <th>$(-\infty;-2)$</th>
                    <th>$x=-2$</th>
                    <th>$(-2;1)$</th>
                    <th>$x=1$</th>
                    <th>$(1;\infty)$</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Vorzeichen von $f'$</td>
                    <td>$-$</td>
                    <td>$0$</td>
                    <td>$+$</td>
                    <td>$0$</td>
                    <td>$+$</td>
                </tr>
                <tr>
                    <td>Folgerung</td>
                    <td>fallend</td>
                    <td>Tiefpunkt</td>
                    <td>wachsend</td>
                    <td>waagrechte Tangente</td>
                    <td>wachsend</td>
                </tr>
            </tbody>
        </table>
    </div>
</div>

Bei $x=1$ gibt es **keinen Vorzeichenwechsel**. Also liegt dort kein Hochpunkt und kein Tiefpunkt vor.

Da die Tangente dort waagrecht ist, handelt es sich bei $x=1$ um einen **Sattelpunkt**.

**Punkte berechnen**

$$\begin{aligned}
f(-2) &= (-2)^4-6\cdot(-2)^2+8\cdot(-2) = 16-24-16 = -24 \\
f(1) &= 1^4-6\cdot 1^2+8\cdot 1 = 1-6+8 = 3
\end{aligned}$$

Also gilt

$$T(-2\mid -24), \qquad S(1\mid 3).$$

**Monotonie angeben**

Aus der Vorzeichentabelle folgt:

$f$ ist auf $(-\infty;-2]$ streng monoton fallend und auf $[-2;\infty)$ streng monoton wachsend.

