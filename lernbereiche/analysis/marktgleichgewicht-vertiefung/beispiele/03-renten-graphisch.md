---
layout: null
permalink: /lernbereiche/analysis/marktgleichgewicht-vertiefung/beispiele/03-renten-graphisch.html
---
Das Diagramm zeigt die Graphen der Nachfragefunktion $p_N$ und der Angebotsfunktion $p_A$ eines Marktes ($x$ in ME, $p$ in GE/ME). Bestimmen Sie anhand des Diagramms

1. den Ausdruck, der die Konsumentenrente angibt,
2. die ökonomische Bedeutung von $10\cdot 15-\int_0^{10}p_A(x)\,dx$,
3. einen Schätzwert für die Konsumentenrente,
4. einen Schätzwert für die Produzentenrente,
5. ob die Aussage „Die Konsumentenrente ist mehr als doppelt so groß wie die Produzentenrente.“ wahr oder falsch ist.

{% include graph.html
   funktionen='[
    {"name":"p<sub>N</sub>(x)", "term":"30-0.15*x^2", "beschreibung":"Nachfragefunktion", "color":"#1f77b4"},
    {"name":"p<sub>A</sub>(x)", "term":"3+1.2*x", "beschreibung":"Angebotsfunktion", "color":"#d62728"}
   ]'
   flaechen='[
    {"term":"30-0.15*x^2", "von":0, "bis":10, "basis":15, "farbe":"rgba(31,119,180,0.3)", "name":"Konsumentenrente (KR)"},
    {"term":"3+1.2*x", "von":0, "bis":10, "basis":15, "farbe":"rgba(214,39,40,0.3)", "name":"Produzentenrente (PR)"}
   ]'
   hilfslinien='[
    {"x":10,"y":15}
   ]'
   titel="Konsumenten- und Produzentenrente"
   xachse="Menge x in ME"
   yachse="Preis p in GE/ME"
   xmin=0
   xmax=16
   ymin=0
   ymax=32
   xdtick=1
   ydtick=2
%}

Das Marktgleichgewicht liegt im Schnittpunkt der Graphen bei $(10\mid 15)$, also $x_G=10$ ME und $p_G=15$ GE/ME.

**1. Ausdruck für die Konsumentenrente**

Die Konsumentenrente ist die Zahlungsbereitschaft (Fläche unter $p_N$) minus den Umsatz (Rechteck $x_G\cdot p_G$):

$$
KR=\int_0^{10}p_N(x)\,dx-10\cdot 15
$$

**2. Bedeutung von $10\cdot 15-\int_0^{10}p_A(x)\,dx$**

$10\cdot 15$ ist der Umsatz im Marktgleichgewicht, $\int_0^{10}p_A(x)\,dx$ die Angebotsbereitschaft der Produzenten. Die Differenz ist die **Produzentenrente**.

**3. Schätzwert für die Konsumentenrente**

Die blaue Fläche ist fast ein Dreieck: Es ist $x_G=10$ ME breit und reicht vom Höchstpreis bis zum Gleichgewichtspreis, ist also $30-15=15$ GE/ME hoch:

$$
\frac{1}{2}\cdot 10\cdot 15=75 \text{ GE}
$$

Der Graph von $p_N$ liegt über der schrägen Dreieckskante – in der Mitte bei $x=5$ bei $26{,}25$ statt bei $22{,}5$ –, die Fläche ist also größer. Mit den Höhen $h_0=15$ und $h_m=11{,}25$ ergibt sich

$$
KR\approx\frac{10}{4}\left(15+2\cdot 11{,}25\right)\approx 94 \text{ GE}.
$$

Die Konsumentenrente beträgt also etwa $95$ GE (exakt $100$ GE).

**4. Schätzwert für die Produzentenrente**

Hier ist $p_A$ eine Gerade, das Dreieck passt deshalb genau. Es ist $x_G=10$ ME breit und $15-3=12$ GE/ME hoch:

$$
PR=\frac{1}{2}\cdot 10\cdot 12=60 \text{ GE}
$$

**5. Aussage prüfen**

Das Doppelte der Produzentenrente ist $2\cdot 60=120$ GE. Wegen $95<120$ ist die Konsumentenrente nicht mehr als doppelt so groß. Die Aussage ist **falsch**.
