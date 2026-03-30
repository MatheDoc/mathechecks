---
layout: null
---
Gegeben: Für eine ertragsgesetzliche Kostenfunktion $K(x)$ sei bekannt:

1. Die Kosten bei 2 ME betragen 88 GE.
2. Das Betriebsminimum liegt bei 6 ME.
3. Die Fixkosten betragen 48 GE.
4. Die Grenzkosten bei 1 ME betragen 19,5 GE/ME.

Gesucht: $K(x)=ax^3+bx^2+cx+d$.

Um die gegebenen Informationen verwerten zu können, werden wir noch weitere Funktionen benötigen:

- variable Stückkosten: $k_v(x)=ax^2+bx+c$
- Ableitung der variablen Stückkosten: $k_v'(x)=2ax+b$
- Grenzkosten: $K'(x)=3ax^2+2bx+c$

Nun müssen Gleichungen finden, die den Vorgaben 1 - 4 entsprechen. Erwähnenswert ist die 2. Vorgabe. Da das Betriebsminimum eine Extremstelle der variablen Stückkostenfunktion $k_v(x)$ ist, gilt $k_v'(6)=0$.

Aus den Vorgaben 1 - 4 erhalten wir folgende Gleichungen:

$$
\begin{alignat*}{5}
&K(2)=88      \;&\Rightarrow\;&\; a\cdot 2^3 + b\cdot 2^2 + c\cdot 2 + d           = 88     \;&\Rightarrow\;&\; 8a + 4b + 2c + 1d = 88 \\
&k_v'(6)=0      \;&\Rightarrow\;&\; 2a\cdot 6 + b                   = 0      \;&\Rightarrow\;&\; 12a + b +0c +0d = 0 \\
&K(0)=48      \;&\Rightarrow\;&\; a\cdot 0^3 + b\cdot 0^2 + c\cdot 0 + 1d           = 48     \;&\Rightarrow\;&\; 0a+0b+0c+1d = 48 \\
&K'(1)=19{,}5 \;&\Rightarrow\;&\; 3a\cdot 1^2 + 2b\cdot 1 + c                      = 19{,}5 \;&\Rightarrow\;&\; 3a + 2b + 1c +0d= 19{,}5
\end{alignat*}
$$

Die jeweils letzten Gleichungen bilden ein lineares Gleichungssystem mit vier Gleichungen und vier Unbekannten. Dieses kann mit Hilfe des Gauß-Algorithmus oder dem Taschenrechner eindeutig gelöst werden. Wir erhalten:

$$
a=0{,}5,\quad b=-6,\quad c=30,\quad d=48
$$

Damit ist $K(x)=0{,}5x^3-6x^2+30x+48$.