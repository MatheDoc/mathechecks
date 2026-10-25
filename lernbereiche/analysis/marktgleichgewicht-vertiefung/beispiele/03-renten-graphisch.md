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

Ein Kästchen ist $1$ ME breit und $2$ GE/ME hoch und steht damit für $1\cdot 2=2$ GE. Die blaue Fläche zwischen dem Graphen von $p_N$ und der Geraden $p=15$ umfasst etwa $50$ Kästchen:

$$
KR\approx 50\cdot 2=100 \text{ GE}
$$

**4. Schätzwert für die Produzentenrente**

Die rote Fläche zwischen der Geraden $p=15$ und dem Graphen von $p_A$ ist ein Dreieck mit $30$ Kästchen:

$$
PR\approx 30\cdot 2=60 \text{ GE}
$$

**5. Aussage prüfen**

Das Doppelte der Produzentenrente ist $2\cdot 60=120$ GE. Wegen $100<120$ ist die Konsumentenrente nicht mehr als doppelt so groß. Die Aussage ist **falsch**.
