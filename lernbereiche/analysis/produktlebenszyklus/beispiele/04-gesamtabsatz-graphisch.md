---
layout: null
permalink: /lernbereiche/analysis/produktlebenszyklus/beispiele/04-gesamtabsatz-graphisch.html
---
Der monatliche Absatz eines Produkts wird durch $a(t)=t^2\cdot e^{-0{,}25t}+3$ beschrieben ($t$ in Monaten, $a(t)$ in ME/Monat).

{% include graph.html
   funktionen='[
    {"name":"a(t)", "term":"x^2*exp(-0.25*x)+3", "beschreibung":"monatlicher Absatz"}
   ]'
   flaechen='[
    {"term":"x^2*exp(-0.25*x)+3", "von":6, "bis":12, "farbe":"rgba(50,120,220,0.3)", "name":"Gesamtabsatz im 2. Halbjahr"}
   ]'
   titel="Gesamtabsatz als Fläche unter dem Graphen"
   xachse="Zeit t in Monaten"
   yachse="Absatz in ME/Monat"
   xmin=0
   xmax=24
   ymin=0
   ymax=13
%}

- **Fläche deuten:** Die markierte Fläche unter dem Graphen von $a$ über $[6;12]$ entspricht

    $$
    \int_6^{12} a(t)\,dt,
    $$

    dem Gesamtabsatz (in ME) vom Ende des 6. bis zum Ende des 12. Monats, also im zweiten Halbjahr.

- **Fläche abschätzen:** Auf $[6;12]$ liegt der Graph zwischen ca. $10{,}2$ und $11{,}7$ ME/Monat. Die Fläche liegt also zwischen zwei Rechtecken der Breite $6$:

    $$
    6\cdot 10{,}2 \approx 61 \text{ ME} \quad<\quad \int_6^{12} a(t)\,dt \quad<\quad 6\cdot 11{,}7\approx 70 \text{ ME}
    $$

    Ein guter Schätzwert ist $6\cdot 11{,}2\approx 67$ ME. Der genaue Wert beträgt $\int_6^{12} a(t)\,dt\approx 67{,}36$ ME.

- **Durchschnitt deuten:** Ein Rechteck der Breite $6$ mit gleicher Fläche hat die Höhe $\frac{67{,}36}{6}\approx 11{,}23$. Im zweiten Halbjahr werden also durchschnittlich ca. $11{,}2$ ME pro Monat abgesetzt.

- **Aussage prüfen:** „Im ersten Halbjahr werden mindestens $60$ ME abgesetzt.“

    Auf $[0;6]$ steigt $a$. Jeder Monatsstreifen liegt deshalb unter dem Rechteck mit der Höhe am rechten Rand:

    $$
    \int_0^6 a(t)\,dt < a(1)+a(2)+\dots+a(6)\approx 3{,}8+5{,}4+7{,}3+8{,}9+10{,}2+11{,}0 = 46{,}6 \text{ ME}
    $$

    Die Aussage ist falsch.
