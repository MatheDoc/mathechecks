---
layout: null
---

Wir betrachten die Ereignisse

- $A$: Eine Person putzt sich regelmäßig die Zähne.
- $B$: Eine Person hat gesunde Zähne.

und das zugehörige Baumdiagramm

{% include dev/baumdiagramm.html
    pa="0.5"
    pba="0.4"
    pbna="0.1"
    titel="Zahnreinigung und -gesundheit"
%}

Zusätzlich zu den früheren Interpretation gilt:

- $A$-Bedingungen: Auf der zweiten Stufe stehen die bedingten Wahrscheinlichkeiten $P_A(B)$, $P_A(\overline{B})$, $P_{\overline{A}}(B)$ und $P_{\overline{A}}(\overline{B})$. Die Wahrscheinlichkeit, dass eine Person, die sich regelmäßig die Zähne putzt, gesunde Zähne hat (symbolisch: $P_A(B)$), beträgt z.B. also 40&nbsp;%.
- $B$-Bedingungen: Die Wahrscheinlichkeiten $P_B(A)$, $P_B(\overline{A})$, $P_{\overline{B}}(A)$ und $P_{\overline{B}}(\overline{A})$ können wir **nicht direkt** aus dem Baumdiagramm ablesen. Stattdessen verwenden wir die Formel $P_B(A)=\frac{P(A\cap B)}{P(B)}$. Die Wahrscheinlichkeit, dass eine Person, die gesunde Zähne hat, sich regelmäßig die Zähne putzt (symbolisch: $P_B(A)$), beträgt z.B. also $\frac{0{,}2}{0{,}2+0{,}05}=0{,}8$.

Anhand eines vollständig ausgefüllten Baumdiagramms können wir unmittelbar erkennen, ob die Ereignisse $A$ und $B$ stochastisch unabhängig sind oder nicht: Es muss $P_A(B)=P_{\overline{A}}(B)$ und $P_A(\overline{B})=P_{\overline{A}}(\overline{B})$ gelten. In unserem Beispiel ist dies nicht der Fall, da $P_A(B)=0{,}4$ und $P_{\overline{A}}(B)=0{,}1$ gilt. Die Ereignisse $A$ und $B$ sind also nicht stochastisch unabhängig.
