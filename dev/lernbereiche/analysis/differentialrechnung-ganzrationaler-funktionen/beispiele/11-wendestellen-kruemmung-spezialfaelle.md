---
layout: null
---

Untersuche die Funktion $f(x)=3x^5+5x^4-10x^3-30x^2$ auf Wendestellen und Krümmung.

**Zweite und dritte Ableitung berechnen**

$$\begin{aligned}
f''(x) &= 60x^3+60x^2-60x-60 = 60(x+1)^2(x-1) \\
f'''(x) &= 180x^2+120x-60
\end{aligned}$$

**Kandidatenstellen über $f''(x)=0$ finden**

$$60(x+1)^2(x-1)=0 \quad\Rightarrow\quad x=-1 \text{ oder } x=1$$

Dabei ist $x=-1$ eine doppelte Nullstelle von $f''$ und $x=1$ eine einfache Nullstelle.

**Üblichen Test prüfen**

$$\begin{aligned}
f'''(-1) &= 180\cdot(-1)^2+120\cdot(-1)-60 = 0 \\
f'''(1) &= 180+120-60 = 240 \neq 0
\end{aligned}$$

Also ist $x=1$ sicher eine Wendestelle. Bei $x=-1$ entscheidet der schnelle Test nicht; dort braucht man zusätzlich das Vorzeichen von $f''$.

**Graph von $f''$ und Vorzeichentabelle**

<div class="diagramm-row">
    <div style="flex: 1 1 420px; min-width: 0;">
        {% include dev/graph.html
             funktionen='[{"name":"f\u2032\u2032", "term":"60*(x+1)^2*(x-1)", "color":"#4363d8"}]'
             titel="Graph der zweiten Ableitung f″"
               xmin=-1.5 xmax=1.3 ymin=-60 ymax=20
        %}
    </div>
    <div style="flex: 1 1 320px; min-width: 0;">
        <table>
            <thead>
                <tr>
                    <th>Bereich</th>
                    <th>$(-\infty;-1)$</th>
                    <th>$x=-1$</th>
                    <th>$(-1;1)$</th>
                    <th>$x=1$</th>
                    <th>$(1;\infty)$</th>
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

Bei $x=1$ wechselt das Vorzeichen von $f''$ von $-$ nach $+$. Also liegt dort eine Wendestelle vor.

**Punkt und Krümmungsintervalle angeben**

$$f(1)=3+5-10-30=-32$$

Damit gilt

$$W(1\mid -32).$$

Außerdem ist $f$ auf $(-\infty;1]$ rechtsgekrümmt bzw. konkav und auf $[1;\infty)$ linksgekrümmt bzw. konvex.
