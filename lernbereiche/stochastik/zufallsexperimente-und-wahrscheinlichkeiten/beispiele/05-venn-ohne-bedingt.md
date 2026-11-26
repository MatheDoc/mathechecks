---
layout: null
permalink: /lernbereiche/stochastik/zufallsexperimente-und-wahrscheinlichkeiten/beispiele/05-venn-ohne-bedingt.html
---
Geben Sie jeweils an, welche Wahrscheinlichkeit durch den Inhalt der markierten Fläche dargestellt wird.

**a)**

{% include venn.html markiert="a,b,n" %}

Das Rechteck $X$ zerfällt in vier Teilflächen:

| Teilfläche | Ereignis | markiert? |
| --- | --- | --- |
| in $A$, nicht in $B$ | $A\cap\overline{B}$ | ja |
| in $A$ und in $B$ (Überlappung) | $A\cap B$ | nein |
| in $B$, nicht in $A$ | $\overline{A}\cap B$ | ja |
| außerhalb beider Kreise | $\overline{A}\cap\overline{B}$ | ja |

Markiert ist alles außer der Überlappung, also das Gegenereignis von $A\cap B$. Mit dem Gesetz von de Morgan gilt $\overline{A\cap B}=\overline{A}\cup\overline{B}$: Markiert ist alles, was nicht in $A$ **oder** nicht in $B$ liegt. Die Fläche stellt also

$$
P(\overline{A}\cup\overline{B})=1-P(A\cap B)
$$

dar.

**b)**

{% include venn.html markiert="a,b" %}

Markiert sind $A\cap\overline{B}$ und $\overline{A}\cap B$, also genau eines der beiden Ereignisse. Die Fläche stellt

$$
P(A\cap\overline{B})+P(\overline{A}\cap B)=P(A\cup B)-P(A\cap B)
$$

dar: Von der Vereinigung $A\cup B$ wird die Überlappung $A\cap B$ abgezogen.
