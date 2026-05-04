---
layout: null
---

Untersuche die Funktion $f(x)=3x^4+4x^3$ auf Hochpunkt, Tiefpunkt, Sattelpunkt und Monotonie.

**Erste und zweite Ableitung berechnen**

$$\begin{aligned}
f'(x) &= 12x^3+12x^2 = 12x^2(x+1) \\
f''(x) &= 36x^2+24x = 12x(3x+2)
\end{aligned}$$

**Kandidatenstellen bestimmen**

$$f'(x)=0 \quad\Rightarrow\quad 12x^2(x+1)=0 \quad\Rightarrow\quad x=-1 \text{ oder } x=0$$

**Einfache Extremstelle prüfen**

$$f''(-1)=12>0$$

Also liegt bei $x=-1$ ein Tiefpunkt vor.

**Spezialfall bei $x=0$ untersuchen**

$$f''(0)=0$$

Der Test mit der zweiten Ableitung entscheidet hier also nicht. Deshalb betrachten wir den Vorzeichenwechsel von $f'$.

**Graph von $f'$ und Vorzeichentabelle**

<div class="diagramm-row">
    <div style="flex: 1 1 420px; min-width: 0;">
        {% include dev/graph.html
             funktionen='[{"name":"f\u2032", "term":"12*x^2*(x+1)", "color":"#4363d8"}]'
             titel="Graph der ersten Ableitung f′"
               xmin=-1.5 xmax=0.8 ymin=-5 ymax=15
        %}
    </div>
    <div style="flex: 1 1 320px; min-width: 0;">
        <table>
            <thead>
                <tr>
                    <th>Bereich</th>
                    <th>$(-\infty;-1)$</th>
                    <th>$x=-1$</th>
                    <th>$(-1;0)$</th>
                    <th>$x=0$</th>
                    <th>$(0;\infty)$</th>
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

Bei $x=0$ gibt es **keinen Vorzeichenwechsel**. Also liegt dort kein Hochpunkt und kein Tiefpunkt vor.

Da die Tangente dort waagrecht ist, handelt es sich bei $x=0$ um einen **Sattelpunkt**.

**Punkte berechnen**

$$\begin{aligned}
f(-1) &= 3\cdot(-1)^4+4\cdot(-1)^3 = 3-4 = -1 \\
f(0) &= 0
\end{aligned}$$

Also gilt

$$T(-1\mid -1), \qquad S(0\mid 0).$$

**Monotonie angeben**

Aus der Vorzeichentabelle folgt:

$f$ ist auf $(-\infty;-1]$ streng monoton fallend und auf $[-1;\infty)$ streng monoton wachsend.
