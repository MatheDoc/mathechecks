---
layout: null
---

Untersuche die Funktion $f(x)=\frac{3}{4}x^5-\frac{15}{2}x^3-15x^2$ auf Wendestellen und Krümmung.

**Zweite und dritte Ableitung berechnen**

$$\begin{aligned}
f''(x) &= 15x^3-45x-30 = 15(x+1)^2(x-2) \\
f'''(x) &= 45x^2-45
\end{aligned}$$

**Kandidatenstellen über $f''(x)=0$ finden**

$$15(x+1)^2(x-2)=0 \quad\Rightarrow\quad x=-1 \text{ oder } x=2$$

Dabei ist $x=-1$ eine doppelte Nullstelle von $f''$ und $x=2$ eine einfache Nullstelle.

**Üblichen Test prüfen**

$$\begin{aligned}
f'''(-1) &= 45\cdot(-1)^2-45 = 0 \\
f'''(2) &= 45\cdot 2^2-45 = 180-45 = 135 \neq 0
\end{aligned}$$

Also ist $x=2$ sicher eine Wendestelle. Bei $x=-1$ entscheidet der schnelle Test nicht; dort braucht man zusätzlich das Vorzeichen von $f''$.

**Graph von $f''$ und Vorzeichentabelle**

<div class="diagramm-row">
    <div style="flex: 1 1 420px; min-width: 0;">
        {% include dev/graph.html
                         funktionen='[{"name":"f\u2032\u2032", "term":"15*(x+1)^2*(x-2)", "color":"#4363d8"}]'
             titel="Graph der zweiten Ableitung f″"
                             xmin=-2 xmax=3 ymin=-80 ymax=40
        %}
    </div>
    <div style="flex: 1 1 320px; min-width: 0;">
        <table>
            <thead>
                <tr>
                    <th>Bereich</th>
                    <th>$(-\infty;-1)$</th>
                    <th>$x=-1$</th>
                    <th>$(-1;2)$</th>
                    <th>$x=2$</th>
                    <th>$(2;\infty)$</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Vorzeichen von $f''$</td>
                    <td>$-$</td>
                    <td>$0$</td>
                    <td>$-$</td>
                    <td>$0$</td>
                    <td>$+$</td>
                </tr>
                <tr>
                    <td>Folgerung</td>
                    <td>rechtsgekrümmt</td>
                    <td>kein Wechsel</td>
                    <td>rechtsgekrümmt</td>
                    <td>Wendestelle</td>
                    <td>linksgekrümmt</td>
                </tr>
            </tbody>
        </table>
    </div>
</div>

Bei $x=-1$ gibt es **keinen Vorzeichenwechsel** von $f''$. Also ist $x=-1$ trotz $f''(-1)=0$ **keine** Wendestelle.

Bei $x=2$ wechselt das Vorzeichen von $f''$ von $-$ nach $+$. Also liegt dort eine Wendestelle vor.

**Punkt und Krümmungsintervalle angeben**

$$f(2)=\frac{3}{4}\cdot 2^5-\frac{15}{2}\cdot 2^3-15\cdot 2^2=24-60-60=-96$$

Damit gilt

$$W(2\mid -96).$$

Außerdem ist $f$ auf $(-\infty;2]$ rechtsgekrümmt bzw. konkav und auf $[2;\infty)$ linksgekrümmt bzw. konvex.
