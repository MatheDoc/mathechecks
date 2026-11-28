---
layout: null
permalink: /lernbereiche/analysis/ganzrationale-oekonomische-funktionen/beispiele/03-grenzfunktionen-graphisch.html
---
**Angebotspolypol:** Das Diagramm zeigt die Grenzerlösfunktion $E'$ und die Grenzkostenfunktion $K'$.

{% include graph.html
   funktionen='[
    {"name":"E′(x)", "term":"32", "beschreibung":"Grenzerlösfunktion", "color":"#2ca02c"},
    {"name":"K′(x)", "term":"1.5*x^2-12*x+30", "beschreibung":"Grenzkostenfunktion", "color":"#d62728"}
   ]'
   punkte='[
     {"x":4,"y":6,"text":"Tiefpunkt von K′: x_w = 4 ME, minimale Grenzkosten 6 GE/ME"},
     {"x":8.16,"y":32,"text":"Schnittpunkt von E′ und K′: gewinnmaximale Menge 8,16 ME"}
   ]'
   titel="Grenzfunktionen (Polypol)"
   xachse="Menge x in ME"
   yachse="GE/ME"
   xmin=0
   xmax=13
   ymin=0
   ymax=60
%}

- **Marktpreis:** $E'$ ist konstant bei 32 GE/ME, also beträgt der Marktpreis 32 GE/ME.
- **Übergang vom degressiven zum progressiven Kostenwachstum:** Tiefpunkt von $K'$ bei 4 ME. Die minimalen Grenzkosten betragen 6 GE/ME.
- **Gewinnmaximale Menge:** $K'$ läuft bei etwa 8,16 ME von unten nach oben durch $E'$.
- **Grenzgewinn bei 4 ME:** $E'(4)-K'(4)=32-6=26$ GE/ME. Der Gewinn steigt hier also.

**Angebotsmonopol:** Das Diagramm zeigt die Grenzerlösfunktion $E'$ und die Grenzkostenfunktion $K'$.

{% include graph.html
   funktionen='[
    {"name":"E′(x)", "term":"-12*x+84", "beschreibung":"Grenzerlösfunktion", "color":"#2ca02c"},
    {"name":"K′(x)", "term":"1.5*x^2-12*x+30", "beschreibung":"Grenzkostenfunktion", "color":"#d62728"}
   ]'
   punkte='[
     {"x":4,"y":6,"text":"Tiefpunkt von K′: x_w = 4 ME"},
     {"x":6,"y":12,"text":"Schnittpunkt von E′ und K′: gewinnmaximale Menge 6 ME"},
     {"x":7,"y":0,"text":"Nullstelle von E′: erlösmaximale Menge 7 ME"}
   ]'
   titel="Grenzfunktionen (Monopol)"
   xachse="Menge x in ME"
   yachse="GE/ME"
   xmin=0
   xmax=14
   ymin=-40
   ymax=90
%}

- **Übergang vom degressiven zum progressiven Kostenwachstum:** unverändert bei 4 ME, da $K'$ gleich bleibt.
- **Gewinnmaximale Menge:** $E'$ und $K'$ schneiden sich bei 6 ME.
- **Erlösmaximale Menge:** Nullstelle von $E'$ bei 7 ME.
- **Grenzgewinn bei 9 ME:** $E'(9)-K'(9)=-24-43{,}5=-67{,}5$ GE/ME. $K'$ liegt über $E'$, der Gewinn fällt hier bereits.

**Grenzgewinnfunktion:** Das Diagramm zeigt den Graphen von $G'$ für Velotec im Polypol.

{% include graph.html
   funktionen='[
    {"name":"G′(x)", "term":"-1.5*x^2+12*x+2", "beschreibung":"Grenzgewinnfunktion", "color":"#1f77b4"}
   ]'
   punkte='[
     {"x":8.16,"y":0,"text":"Nullstelle von G′ (Vorzeichenwechsel + nach −): gewinnmaximale Menge 8,16 ME"},
     {"x":4,"y":26,"text":"Hochpunkt von G′: stärkster Gewinnanstieg bei 4 ME"}
   ]'
   titel="Grenzgewinn (Polypol)"
   xachse="Menge x in ME"
   yachse="GE/ME"
   xmin=0
   xmax=13
   ymin=-40
   ymax=35
%}

- **Gewinnmaximale Menge:** $G'$ wechselt bei etwa 8,16 ME das Vorzeichen von $+$ nach $-$. Bis dahin steigt der Gewinn, danach fällt er.
- **Stärkster Gewinnanstieg:** Hochpunkt von $G'$ bei 4 ME. Der maximale Grenzgewinn beträgt 26 GE/ME.
- **Gewinnentwicklung bei 10 ME:** $G'(10)=-28<0$, der Gewinn fällt.
