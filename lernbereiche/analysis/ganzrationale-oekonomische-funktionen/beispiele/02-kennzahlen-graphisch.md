---
layout: null
permalink: /lernbereiche/analysis/ganzrationale-oekonomische-funktionen/beispiele/02-kennzahlen-graphisch.html
---
**Angebotspolypol** mit Kapazitätsgrenze bei 13 ME: Der Marktpreis ist die konstante Höhe von $p$, der maximale Erlös wird an der Kapazitätsgrenze erreicht.

{% include graph.html
   funktionen='[
    {"name":"E(x)", "term":"32*x", "beschreibung":"Erlösfunktion", "color":"#2ca02c"},
    {"name":"K(x)", "term":"0.5*x^3-6*x^2+30*x+48", "beschreibung":"Kostenfunktion", "color":"#d62728"},
    {"name":"G(x)", "term":"-0.5*x^3+6*x^2+2*x-48", "beschreibung":"Gewinnfunktion", "color":"#1f77b4"},
    {"name":"p(x)", "term":"32", "beschreibung":"Preis-Absatz-Funktion", "color":"#ff7f0e"}
   ]'
   punkte='[
     {"x":0,"y":32,"text":"Marktpreis 32 GE"},
     {"x":13,"y":416,"text":"maximaler Erlös 416 GE an der Kapazitätsgrenze 13 ME"},
     {"x":4,"y":104,"text":"Übergang vom degressiven zum progressiven Kostenwachstum bei 4 ME"},
     {"x":3.06,"y":0,"text":"Gewinnschwelle 3,06 ME"},
     {"x":11.63,"y":0,"text":"Gewinngrenze 11,63 ME"},
     {"x":8.16,"y":96.16,"text":"gewinnmaximale Menge 8,16 ME, maximaler Gewinn 96,16 GE"}
   ]'
   titel="Ökonomische Funktionen (Polypol)"
   xachse="Menge x in ME"
   yachse="Betrag y in GE"
   xmin=0
   xmax=14
   ymin=-100
   ymax=450
%}

**Angebotsmonopol:** Höchstpreis und Sättigungsmenge liest man an $p$ ab, erlösmaximale Menge und maximalen Erlös am Hochpunkt von $E$. Die übrigen Kennzahlen werden wie im Polypol abgelesen.

{% include graph.html
   funktionen='[
    {"name":"E(x)", "term":"-6*x^2+84*x", "beschreibung":"Erlösfunktion", "color":"#2ca02c"},
    {"name":"K(x)", "term":"0.5*x^3-6*x^2+30*x+48", "beschreibung":"Kostenfunktion", "color":"#d62728"},
    {"name":"G(x)", "term":"-0.5*x^3+54*x-48", "beschreibung":"Gewinnfunktion", "color":"#1f77b4"},
    {"name":"p(x)", "term":"-6*x+84", "beschreibung":"Preis-Absatz-Funktion", "color":"#ff7f0e"}
   ]'
   punkte='[
     {"x":0,"y":84,"text":"Höchstpreis 84 GE"},
     {"x":14,"y":0,"text":"Sättigungsmenge 14 ME"},
     {"x":7,"y":294,"text":"erlösmaximale Menge 7 ME, maximaler Erlös 294 GE"},
     {"x":4,"y":104,"text":"Übergang vom degressiven zum progressiven Kostenwachstum bei 4 ME"},
     {"x":0.9,"y":0,"text":"Gewinnschwelle 0,90 ME"},
     {"x":9.92,"y":0,"text":"Gewinngrenze 9,92 ME"},
     {"x":6,"y":168,"text":"gewinnmaximale Menge 6 ME, maximaler Gewinn 168 GE"}
   ]'
   titel="Ökonomische Funktionen (Monopol)"
   xachse="Menge x in ME"
   yachse="Betrag y in GE"
   xmin=0
   xmax=14.5
   ymin=-100
   ymax=350
%}
