---
layout: null
---
Gegeben seien zwei Ereignisse $A$ und $B$ mit $P(A) = 0{,}5$, $P(B) = 0,2$ und $P(A \cap B) = 0,05$. Dann ist z.B.

$$
\begin{align*}
P(\overline{A})& =1-P(A)=1-0{,}5=0{,}5\\
P(A\cup B) & = P(A)+P(B)-P(A\cap B)=0{,}5+0{,}2-0{,}05=0{,}65\\
P(\overline{A}\cap \overline{B}) & = 1-P(A\cup B)=1-0{,}65=0{,}35\\
P_{\overline{A}}(\overline{B}) & = \frac{P(\overline{A}\cap \overline{B})}{P(\overline{A})}=\frac{0{,}35}{0{,}5}=0{,}7\\
P_B(A) & = \frac{P(A\cap B)}{P(B)}=\frac{0{,}05}{0{,}2}=0{,}25
\end{align*}
$$

Um zu prüfen, ob die Ereignisse $A$ und $B$ unabhängig sind, können wir $P(A)=0{,}5$ mit $P_B(A)=0{,}25$ vergleichen. Da diese Werte nicht übereinstimmen, sind die Ereignisse $A$ und $B$ nicht unabhängig.