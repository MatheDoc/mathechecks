---
layout: null
---

Was halten Jugendliche von Lern-Apps? Zu dieser Frage wurde eine Befragung unter 2.000 Schülerinnen und Schülern durchgeführt. 35,7&nbsp;% der Befragten nutzen kostenlose Starter-Versionen (S) von Lern-Apps zur Unterhaltung (U), beispielsweise für Quizspiele. 24,3&nbsp;% verwenden Starter-Versionen gezielt zur Vorbereitung auf Prüfungen (V). 224 Jugendliche nutzen kostenpflichtige Pro-Versionen (P) zur gezielten Vorbereitung auf Prüfungen. Darüber hinaus gibt es auch einige Jugendliche mit Pro-Versionen, die die App lediglich zur Unterhaltung nutzen. 480 Befragten haben bislang noch keine Lern-App (k) verwendet. Wie sieht das vollständig ausgefüllte Baumdiagramm aus?

Zunächst erstellen wir das Baumdiagramm und tragen die gegebenen Wahrscheinlichkeiten ein:

<figure>
    <img src='Lernapp.png'>
</figure>

- Welchen Wert hat $d$ ?

    Da die Summe aller Pfadenwahrscheinlichkeiten 1 ergeben muss, haben wir
    $$
    d=1-0{,}357-0{,}243-0{,}112-0{,}24=0{,}048.
    $$

- Welchen Wert hat $a$ ?

    Die Pfadadditionsregel auf den $SU$- und  $SV$-Pfad angewendet ergibt
    $$
    a=0{,}357+0{,}243=0{,}6. 
    $$

- Welchen Wert hat $b$ ?

    Die Multiplikationsregel auf den $SU$-Pfad angewendet ergibt
    $$
    0{,}6\cdot b=0{,}357 \Rightarrow b=0{,}595.
    $$

- Welchen Wert hat $c$ ?

    Die Multiplikationsregel auf den $PU$-Pfad angewendet ergibt
    $$
    (0{,}76-0{,}6)\cdot c=0{,}048 \Rightarrow c=0{,}3.
    $$
  
Nun könnten wir Wahrscheinlichkeiten im Sachzusammenhang berechnen. Zum Beispiel die Wahrscheinlichkeit, des Ereignisses $E$, dass ein zufällig ausgewählter Schüler eine Lern-App zur Unterhaltung nutzt:

$$
\begin{align*}
  P(F)&=P(\{SU\})+P(\{PU\})\\
  &=0{,}357+0{,}048\\
  &=0{,}405
\end{align*}
$$