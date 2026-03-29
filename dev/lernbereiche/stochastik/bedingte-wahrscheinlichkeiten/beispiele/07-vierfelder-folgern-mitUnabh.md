---
layout: null
---

Wir betrachten die Ereignisse

- $A$: Eine Person putzt sich regelmäßig die Zähne.
- $B$: Eine Person hat gesunde Zähne.

und die zugehörige Vier-Felder-Tafel

|                | $B$      | $\overline{B}$ | $\Sigma$ |
| -------------- | -------- | -------------- | -------- |
| $A$            | $0{,}08$ | $0{,}52$       | $0{,}6$  |
| $\overline{A}$ | $0{,}12$  | $0{,}28$       | $0{,}4$  |
| $\Sigma$       | $0{,}2$  | $0{,}8$        | $1$      |

Zusätzlich zu den früheren Interpretation gilt:

- Bedingte Wahrscheinlichkeiten können nicht direkt aus der Vier-Felder-Tafel abgelesen werden. Stattdessen verwenden wir die Formel $P_A(B)=\frac{P(A\cap B)}{P(A)}$. Die Wahrscheinlichkeit, dass eine Person, die sich regelmäßig die Zähne putzt, gesunde Zähne hat (symbolisch: $P_A(B)$), beträgt z.B. also $\frac{0{,}08}{0{,}6}\approx 0{,}133$.

Anhand einer vollständig ausgefüllten Vier-Felder-Tafel können wir ermitteln, ob die Ereignisse $A$ und $B$ stochastisch unabhängig sind oder nicht: Dazu prüfen wir die Bedingung $
P(A)\cdot P(B)=P(A\cap B)$. In unserem Beispiel gilt

$$
P(A)\cdot P(B)=0{,}6\cdot 0{,}2=0{,}12\neq 0{,}08=P(A\cap B).
$$

Die Ereignisse $A$ und $B$ sind also nicht stochastisch unabhängig.

