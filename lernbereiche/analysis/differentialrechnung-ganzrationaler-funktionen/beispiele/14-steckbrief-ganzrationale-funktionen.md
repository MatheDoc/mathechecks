---
layout: null
permalink: /lernbereiche/analysis/differentialrechnung-ganzrationaler-funktionen/beispiele/14-steckbrief-ganzrationale-funktionen.html
---

Stelle eine ganzrationale Funktion dritten Grades auf, die bei $E(0\mid 3)$ einen Hochpunkt und bei $W(1\mid 1)$ eine Wendestelle hat.

- Allgemeinen Funktionsterm ansetzen

    $$f(x)=ax^3+bx^2+cx+d$$

- Bedingungen aus den Angaben formulieren

    Aus $E(0\mid 3)$ folgt:

    $$f(0)=3 \quad\text{und}\quad f'(0)=0$$

    Aus $W(1\mid 1)$ folgt:

    $$f(1)=1 \quad\text{und}\quad f''(1)=0$$

- Ableitungen bilden

    $$\begin{aligned}
    f'(x) &= 3ax^2+2bx+c \\
    f''(x) &= 6ax+2b
    \end{aligned}$$

- Bedingungen in Gleichungen übersetzen

    $$\begin{aligned}
    f(0)=3 &\Rightarrow d=3 \\
    f'(0)=0 &\Rightarrow c=0 \\
    f(1)=1 &\Rightarrow a+b+c+d=1 \\
    f''(1)=0 &\Rightarrow 6a+2b=0
    \end{aligned}$$

    Mit $c=0$ und $d=3$ wird daraus das LGS

    $$\begin{aligned}
    a+b &= -2 \\
    3a+b &= 0
    \end{aligned}$$

- LGS lösen

    Das Auflösen ist hier nicht der Kern der Aufgabe. Mit Gauß-Verfahren oder dem Taschenrechner erhält man

    $$a=1, \qquad b=-3, \qquad c=0, \qquad d=3.$$

- Funktion angeben und Hochpunkt kurz prüfen

    $$f(x)=x^3-3x^2+3$$

    Zur Kontrolle:

    $$f''(0)=6\cdot 0+2\cdot(-3)=-6<0,$$

    also liegt bei $E(0\mid 3)$ tatsächlich ein Hochpunkt vor.
