---
layout: null
permalink: /lernbereiche/analysis/marktgleichgewicht-vertiefung/beispiele/05-abschoepfung-kr.html
---
Gegeben sind die Nachfragefunktion $p_N$ und die Angebotsfunktion $p_A$ mit

$$
\begin{align*}
p_N(x)&=-0{,}02x^2-0{,}5x+60\\
p_A(x)&=0{,}5x+10.
\end{align*}
$$

Durch einen Teilmarkt soll ein Teil der Konsumentenrente abgeschöpft werden. Auf dem ersten Teilmarkt gilt der Gleichgewichtspreis $p_G$.

1. Bestimmen Sie den abgeschöpften Teil der Konsumentenrente, wenn auf dem Teilmarkt ein Preis von $40$ GE/ME verlangt wird.
2. Bestimmen Sie die Teilmarktmenge $x_2$ und den Teilmarktpreis $p_2$, bei denen die Konsumentenrente maximal abgeschöpft wird.

{% include graph.html
   funktionen='[
    {"name":"p<sub>N</sub>(x)", "term":"-0.02*x^2-0.5*x+60", "beschreibung":"Nachfragefunktion", "color":"#1f77b4"},
    {"name":"p<sub>A</sub>(x)", "term":"0.5*x+10", "beschreibung":"Angebotsfunktion", "color":"#d62728"}
   ]'
   flaechen='[
    {"term":"-0.02*x^2-0.5*x+60", "von":0, "bis":21.5037, "basis":40, "farbe":"rgba(59,130,246,0.25)", "name":"KR<sub>2</sub>"},
    {"term":"-0.02*x^2-0.5*x+60", "von":21.5037, "bis":30.9017, "basis":25.4508, "farbe":"rgba(16,185,129,0.25)", "name":"KR<sub>1</sub>"},
    {"term":"40", "von":0, "bis":21.5037, "basis":25.4508, "farbe":"rgba(120,120,120,0.6)", "schraffur":true, "name":"abgeschöpfter Betrag"}
   ]'
   hilfslinien='[
    {"x":21.5037,"y":40,"xLabel":"21,50"},
    {"x":30.9017,"y":25.4508,"xLabel":"x<sub>G</sub>","yLabel":"p<sub>G</sub>"}
   ]'
   titel="Abschöpfung bei einem Teilmarktpreis von 40 GE/ME"
   xachse="Menge x in ME"
   yachse="Preis p in GE/ME"
   xmin=0
   xmax=45
   ymin=0
   ymax=65
%}

**Marktgleichgewicht**

$$
\begin{align*}
-0{,}02x^2-0{,}5x+60&=0{,}5x+10\\
x^2+50x-2500&=0\\
x&=-25\pm\sqrt{625+2500}\\
x_G&\approx 30{,}90 \quad (x\approx -80{,}90 \text{ entfällt})\\
p_G&=p_A(30{,}90)\approx 25{,}45
\end{align*}
$$

**1. Abschöpfung bei einem Teilmarktpreis von 40 GE/ME**

Auf dem Teilmarkt kaufen alle, die mindestens $40$ GE/ME zu zahlen bereit sind:

$$
\begin{align*}
-0{,}02x^2-0{,}5x+60&=40\\
x^2+25x-1000&=0\\
x&\approx 21{,}50 \quad (x\approx -46{,}50 \text{ entfällt})
\end{align*}
$$

Für diese $21{,}50$ ME wird $40-p_G$ mehr gezahlt. Der abgeschöpfte Betrag ist die Fläche des schraffierten Rechtecks:

$$
21{,}5037\cdot(40-25{,}4508)\approx 312{,}86
$$

Es werden etwa $312{,}86$ GE der Konsumentenrente abgeschöpft.

**2. Maximale Abschöpfung**

Der abgeschöpfte Betrag in Abhängigkeit von der Teilmarktmenge $x_2$ ist

$$
\begin{align*}
A(x_2)&=x_2\cdot(p_N(x_2)-p_G)\\
      &=x_2\cdot(-0{,}02x_2^2-0{,}5x_2+60-25{,}45)\\
      &=-0{,}02x_2^3-0{,}5x_2^2+34{,}55x_2.
\end{align*}
$$

Notwendige Bedingung:

$$
\begin{align*}
A'(x_2)=-0{,}06x_2^2-x_2+34{,}55&=0\\
x_2&\approx 17{,}07 \quad (x_2\approx -33{,}74 \text{ entfällt})
\end{align*}
$$

Hinreichende Bedingung: $A''(x_2)=-0{,}12x_2-1$, also $A''(17{,}07)\approx -3{,}05<0$. Es liegt ein Maximum vor.

Teilmarktpreis:

$$
p_2=p_N(17{,}07)\approx 45{,}64
$$

Bei einer Teilmarktmenge von $x_2\approx 17{,}07$ ME und einem Teilmarktpreis von $p_2\approx 45{,}64$ GE/ME wird die Konsumentenrente maximal abgeschöpft, und zwar um $A(17{,}07)\approx 344{,}58$ GE.
