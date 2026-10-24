---
layout: null
permalink: /lernbereiche/analysis/produktlebenszyklus/beispiele/01-kennzahlen-graphisch-umsatz.html
---
Das Diagramm zeigt den monatlichen Absatz zweier Produkte in ME/Monat ($t$ in Monaten seit der Markteinführung):

{% include graph.html
   funktionen='[
    {"name":"a₁(t)", "term":"(-0.1*x^3+2*x^2)*exp(-0.2*x)", "beschreibung":"mit Marktaustritt", "xmin":0, "xmax":20},
    {"name":"a₂(t)", "term":"x^2*exp(-0.25*x)+3", "beschreibung":"mit langfristigem Absatz", "xmin":0},
    {"name":"y = 3", "term":"3+0*x", "beschreibung":"waagrechte Asymptote von a₂", "dash":"dash", "color":"#888888"}
   ]'
   punkte='[
     {"x":2.26,"y":5.77,"text":"stärkster Anstieg a₁"},
     {"x":7.19,"y":15.72,"text":"höchster Absatz a₁"},
     {"x":12.57,"y":9.51,"text":"stärkster Rückgang a₁"},
     {"x":20,"y":0,"text":"Marktaustritt a₁"},
     {"x":0,"y":3,"text":"a₂(0)=3"},
     {"x":2.34,"y":6.06,"text":"stärkster Anstieg a₂"},
     {"x":8,"y":11.66,"text":"höchster Absatz a₂"},
     {"x":13.66,"y":9.14,"text":"stärkster Rückgang a₂"}
   ]'
   titel="Zwei typische Produktlebenszyklen"
   xachse="Zeit t in Monaten"
   yachse="Absatz in ME/Monat"
   xmin=0
   xmax=40
   ymin=0
   ymax=18
%}

Aus den Graphen lesen wir ab:

| Kennzahl | $a_1$ | $a_2$ |
|---|---|---|
| Absatz bei Markteinführung ($y$-Achsenabschnitt) | $0$ ME/Monat | $3$ ME/Monat |
| höchster Absatz (Hochpunkt) | ca. $15{,}7$ ME/Monat nach ca. $7{,}2$ Monaten | ca. $11{,}7$ ME/Monat nach $8$ Monaten |
| stärkster Anstieg (1. Wendepunkt) | nach ca. $2{,}3$ Monaten | nach ca. $2{,}3$ Monaten |
| stärkster Rückgang (2. Wendepunkt) | nach ca. $12{,}6$ Monaten | nach ca. $13{,}7$ Monaten |
| Ende des Zyklus | Marktaustritt nach $20$ Monaten (Nullstelle) | langfristig ca. $3$ ME/Monat (Asymptote $y=3$) |

Bis zum ersten Wendepunkt sind beide Graphen linksgekrümmt: Der Absatz steigt **progressiv**. Danach steigt er bis zum Hochpunkt nur noch **degressiv**. Der Graph von $a_2$ nähert sich für große $t$ der gestrichelten Geraden $y=3$ an, erreicht sie aber nie.
