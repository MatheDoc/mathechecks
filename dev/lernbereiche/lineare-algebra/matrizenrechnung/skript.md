---
layout: dev-module
title: Matrizenrechnung - Skript (Dev)
description: Dev-Lernbereich Matrizenrechnung, Modul Skript.
page_context: Lernbereich
nav: dashboard
body_class: page-module-designs
module_key: skript
published: true
lernbereich: matrizenrechnung
gebiet: lineare-algebra
permalink: /dev/lernbereiche/lineare-algebra/matrizenrechnung/skript.html
---

## Was ist eine Matrix?

Eine **Matrix** ist ein rechteckiges Zahlenschema mit $m$ Zeilen und $n$ Spalten. Wir schreiben eine Matrix in der Regel mit einem Großbuchstaben und geben ihre Dimension als $m \times n$ an:

$$
A = \begin{pmatrix} a_{11} & a_{12} & \cdots & a_{1n} \\ a_{21} & a_{22} & \cdots & a_{2n} \\ \vdots & \vdots & \ddots & \vdots \\ a_{m1} & a_{m2} & \cdots & a_{mn} \end{pmatrix}
$$

Der Eintrag $a_{ij}$ steht in der $i$-ten Zeile und der $j$-ten Spalte.

### Beispiele

$$
A = \begin{pmatrix} 1 & 3 \\ 2 & 0 \end{pmatrix}, \quad
B = \begin{pmatrix} 4 & -1 & 2 \\ 0 & 5 & 3 \end{pmatrix}, \quad
C = \begin{pmatrix} 1 & 0 & 0 \\ 0 & 1 & 0 \\ 0 & 0 & 1 \end{pmatrix}
$$

$A$ ist eine $2 \times 2$-Matrix, $B$ eine $2 \times 3$-Matrix und $C$ eine $3 \times 3$-Matrix. Die Matrix $C$ wird als **Einheitsmatrix** $E_3$ bezeichnet – auf der Hauptdiagonale stehen Einsen, überall sonst Nullen.

### Besondere Matrizen

- Eine Matrix mit nur **einer Spalte** heißt **Spaltenvektor**:

  $$
  \vec{v} = \begin{pmatrix} 2 \\ -1 \\ 3 \end{pmatrix}
  $$

- Eine Matrix mit nur **einer Zeile** heißt **Zeilenvektor**:

  $$
  \vec{w}^T = \begin{pmatrix} 4 & 0 & -2 \end{pmatrix}
  $$

- Eine **quadratische Matrix** hat gleich viele Zeilen und Spalten ($m = n$).

- Die **Nullmatrix** $O$ besteht nur aus Nullen und ist das neutrale Element der Addition.

- Die **Einheitsmatrix** $E_n$ ist das neutrale Element der Multiplikation für quadratische Matrizen.


## Addition und Subtraktion

Zwei Matrizen **gleicher Dimension** können addiert oder subtrahiert werden, indem die entsprechenden Einträge elementweise addiert bzw. subtrahiert werden.

### Definition

Für $A = (a_{ij})$ und $B = (b_{ij})$, beide der Dimension $m \times n$:

$$
A + B = (a_{ij} + b_{ij}), \qquad A - B = (a_{ij} - b_{ij})
$$

### Beispiel

$$
\begin{pmatrix} 3 & -1 \\ 2 & 4 \end{pmatrix} + \begin{pmatrix} 1 & 5 \\ -2 & 0 \end{pmatrix} = \begin{pmatrix} 4 & 4 \\ 0 & 4 \end{pmatrix}
$$

$$
\begin{pmatrix} 3 & -1 \\ 2 & 4 \end{pmatrix} - \begin{pmatrix} 1 & 5 \\ -2 & 0 \end{pmatrix} = \begin{pmatrix} 2 & -6 \\ 4 & 4 \end{pmatrix}
$$

Matrizen unterschiedlicher Dimension können **nicht** addiert oder subtrahiert werden.

### Rechenregeln

Für Matrizen $A$, $B$, $C$ gleicher Dimension gilt:

- Kommutativgesetz: $A + B = B + A$
- Assoziativgesetz: $(A + B) + C = A + (B + C)$
- Neutrales Element: $A + O = A$


## Skalarmultiplikation

Ein **Skalar** (eine reelle Zahl) wird mit einer Matrix multipliziert, indem jeder Eintrag der Matrix mit dem Skalar multipliziert wird.

### Definition

Für $\lambda \in \mathbb{R}$ und $A = (a_{ij})$:

$$
\lambda \cdot A = (\lambda \cdot a_{ij})
$$

### Beispiel

$$
3 \cdot \begin{pmatrix} 2 & -1 \\ 0 & 4 \end{pmatrix} = \begin{pmatrix} 6 & -3 \\ 0 & 12 \end{pmatrix}
$$

### Kombination mit Addition

Diese Operationen lassen sich beliebig kombinieren. Dabei gelten die üblichen Rechenregeln, insbesondere das Distributivgesetz:

$$
\lambda \cdot (A + B) = \lambda \cdot A + \lambda \cdot B
$$

$$
(\lambda + \mu) \cdot A = \lambda \cdot A + \mu \cdot A
$$

### Beispiel

Gegeben:

$$
A = \begin{pmatrix} 1 & 2 \\ 3 & 0 \end{pmatrix}, \quad B = \begin{pmatrix} -1 & 4 \\ 2 & 1 \end{pmatrix}
$$

Berechne $2 \cdot (A - 3B)$:

$$
\begin{align*}
2 \cdot (A - 3B) &= 2 \cdot \left( \begin{pmatrix} 1 & 2 \\ 3 & 0 \end{pmatrix} - 3 \cdot \begin{pmatrix} -1 & 4 \\ 2 & 1 \end{pmatrix} \right) \\
&= 2 \cdot \left( \begin{pmatrix} 1 & 2 \\ 3 & 0 \end{pmatrix} - \begin{pmatrix} -3 & 12 \\ 6 & 3 \end{pmatrix} \right) \\
&= 2 \cdot \begin{pmatrix} 4 & -10 \\ -3 & -3 \end{pmatrix} \\
&= \begin{pmatrix} 8 & -20 \\ -6 & -6 \end{pmatrix}
\end{align*}
$$

{% include dev/check-anker.html nummer="1" %}


## Matrizenmultiplikation

Die Multiplikation zweier Matrizen ist die zentrale Operation der Matrizenrechnung. Sie ist **keine** elementweise Multiplikation, sondern folgt dem **Zeile-mal-Spalte-Prinzip**.

### Voraussetzung

Zwei Matrizen $A$ ($m \times n$) und $B$ ($n \times p$) können genau dann multipliziert werden, wenn die **Spaltenanzahl von $A$** mit der **Zeilenanzahl von $B$** übereinstimmt. Das Ergebnis $C = A \cdot B$ hat die Dimension $m \times p$.

$$
\underbrace{A}_{m \times n} \cdot \underbrace{B}_{n \times p} = \underbrace{C}_{m \times p}
$$

### Berechnung

Der Eintrag $c_{ij}$ des Produkts ergibt sich als Skalarprodukt der $i$-ten Zeile von $A$ mit der $j$-ten Spalte von $B$:

$$
c_{ij} = \sum_{k=1}^{n} a_{ik} \cdot b_{kj} = a_{i1} \cdot b_{1j} + a_{i2} \cdot b_{2j} + \cdots + a_{in} \cdot b_{nj}
$$

### Beispiel

$$
\begin{pmatrix} 1 & 2 \\ 3 & 4 \end{pmatrix} \cdot \begin{pmatrix} 5 & 6 \\ 7 & 8 \end{pmatrix}
$$

Die Einträge des Ergebnisses berechnen sich wie folgt:

$$
\begin{align*}
c_{11} &= 1 \cdot 5 + 2 \cdot 7 = 19 \\
c_{12} &= 1 \cdot 6 + 2 \cdot 8 = 22 \\
c_{21} &= 3 \cdot 5 + 4 \cdot 7 = 43 \\
c_{22} &= 3 \cdot 6 + 4 \cdot 8 = 50
\end{align*}
$$

Also:

$$
\begin{pmatrix} 1 & 2 \\ 3 & 4 \end{pmatrix} \cdot \begin{pmatrix} 5 & 6 \\ 7 & 8 \end{pmatrix} = \begin{pmatrix} 19 & 22 \\ 43 & 50 \end{pmatrix}
$$

### Wichtig: Keine Kommutativität

Im Allgemeinen gilt $A \cdot B \neq B \cdot A$. Die Reihenfolge der Faktoren ist entscheidend – selbst wenn beide Produkte definiert sind, können die Ergebnisse unterschiedlich sein oder eines der Produkte kann undefiniert sein.

### Weitere Rechenregeln

- Assoziativgesetz: $(A \cdot B) \cdot C = A \cdot (B \cdot C)$
- Distributivgesetz: $A \cdot (B + C) = A \cdot B + A \cdot C$
- Neutrales Element: $A \cdot E_n = E_n \cdot A = A$ (für passende Einheitsmatrix)
- Es gibt **keine Division** von Matrizen. Stattdessen verwenden wir die Multiplikation mit der inversen Matrix.

{% include dev/check-anker.html nummer="2" %}


## Die inverse Matrix

### Motivation

In den reellen Zahlen lösen wir die Gleichung $a \cdot x = b$ durch Division: $x = \frac{b}{a} = a^{-1} \cdot b$, wobei $a^{-1}$ die zu $a$ inverse Zahl ist. Da es für Matrizen keine Division gibt, benötigen wir ein analoges Konzept: die **inverse Matrix**.

### Definition

Sei $A$ eine quadratische $n \times n$-Matrix. Eine Matrix $A^{-1}$ heißt **inverse Matrix** von $A$, wenn gilt:

$$
A \cdot A^{-1} = A^{-1} \cdot A = E_n
$$

Eine Matrix, die eine Inverse besitzt, heißt **invertierbar** (oder **regulär**). Nicht jede quadratische Matrix ist invertierbar – eine Matrix ohne Inverse heißt **singulär**.

### Existenz der Inversen

Ob eine Matrix invertierbar ist oder nicht, lässt sich beim Anwenden des Gauß-Jordan-Algorithmus erkennen: Lässt sich die linke Seite **nicht** in die Einheitsmatrix überführen (z. B. weil eine Nullzeile entsteht), so existiert keine Inverse. Ein systematisches Kriterium liefert die **Determinante**, die weiter unten behandelt wird.

### Berechnung mit dem Gauß-Jordan-Algorithmus

Die inverse Matrix wird mit dem **Gauß-Jordan-Algorithmus** berechnet. Dabei wird die Matrix $A$ neben die Einheitsmatrix $E$ geschrieben und durch elementare Zeilenumformungen die linke Seite in die Einheitsmatrix überführt. Auf der rechten Seite steht dann $A^{-1}$:

$$
(A \mid E_n) \sim \cdots \sim (E_n \mid A^{-1})
$$

{% include dev/check-anker.html nummer="3" %}

{% include dev/check-anker.html nummer="4" %}

{% include dev/check-anker.html nummer="5" %}


## Lineare Matrizengleichungen

Mit Hilfe der inversen Matrix können wir Gleichungen lösen, in denen Matrizen als Unbekannte auftreten.

### Prinzip

Eine Matrizengleichung wird – ähnlich wie eine gewöhnliche Gleichung – nach der unbekannten Matrix $X$ aufgelöst. Dabei ist die **Reihenfolge** der Multiplikation entscheidend, da die Matrizenmultiplikation nicht kommutativ ist.

### Grundtypen

| Gleichung | Lösung |
|---|---|
| $A \cdot X = B$ | $X = A^{-1} \cdot B$ |
| $X \cdot A = B$ | $X = B \cdot A^{-1}$ |

In beiden Fällen muss $A$ invertierbar sein.

### Beispiel

Löse die Gleichung $A \cdot X + B = C$ mit

$$
A = \begin{pmatrix} 2 & 1 \\ 5 & 3 \end{pmatrix}, \quad B = \begin{pmatrix} 1 & 0 \\ -1 & 2 \end{pmatrix}, \quad C = \begin{pmatrix} 5 & 3 \\ 9 & 11 \end{pmatrix}
$$

**Schritt 1:** Umstellen nach $A \cdot X$:

$$
A \cdot X = C - B = \begin{pmatrix} 5 & 3 \\ 9 & 11 \end{pmatrix} - \begin{pmatrix} 1 & 0 \\ -1 & 2 \end{pmatrix} = \begin{pmatrix} 4 & 3 \\ 10 & 9 \end{pmatrix}
$$

**Schritt 2:** Von links mit $A^{-1}$ multiplizieren. Es ist $A^{-1} = \begin{pmatrix} 3 & -1 \\ -5 & 2 \end{pmatrix}$ (vgl. oben).

$$
X = A^{-1} \cdot (C - B) = \begin{pmatrix} 3 & -1 \\ -5 & 2 \end{pmatrix} \cdot \begin{pmatrix} 4 & 3 \\ 10 & 9 \end{pmatrix} = \begin{pmatrix} 2 & 0 \\ 0 & 3 \end{pmatrix}
$$

### Achtung bei der Reihenfolge

Steht $X$ rechts vom Faktor, muss $A^{-1}$ von **rechts** multipliziert werden:

$$
X \cdot A + B = C \implies X = (C - B) \cdot A^{-1}
$$

{% include dev/check-anker.html nummer="6" %}


## Die Transponierte

### Definition

Die **Transponierte** $A^T$ einer $m \times n$-Matrix $A$ entsteht durch Vertauschen von Zeilen und Spalten. Der Eintrag $a_{ij}$ von $A$ wird zum Eintrag $a_{ji}$ von $A^T$. Die Dimension von $A^T$ ist $n \times m$.

### Beispiel

$$
A = \begin{pmatrix} 1 & 2 & 3 \\ 4 & 5 & 6 \end{pmatrix} \implies A^T = \begin{pmatrix} 1 & 4 \\ 2 & 5 \\ 3 & 6 \end{pmatrix}
$$

Die $2 \times 3$-Matrix wird zur $3 \times 2$-Matrix.

### Rechenregeln

- $(A^T)^T = A$
- $(A + B)^T = A^T + B^T$
- $(\lambda \cdot A)^T = \lambda \cdot A^T$
- $(A \cdot B)^T = B^T \cdot A^T$ (Reihenfolge dreht sich um!)

### Symmetrische Matrizen

Eine quadratische Matrix $A$ heißt **symmetrisch**, wenn $A^T = A$ gilt, d. h. die Matrix ist spiegelsymmetrisch zur Hauptdiagonale:

$$
\begin{pmatrix} 1 & 3 & 5 \\ 3 & 2 & 7 \\ 5 & 7 & 4 \end{pmatrix}^T = \begin{pmatrix} 1 & 3 & 5 \\ 3 & 2 & 7 \\ 5 & 7 & 4 \end{pmatrix}
$$

{% include dev/check-anker.html nummer="7" %}


## Die Determinante

### Motivation

Die Determinante ist eine Kennzahl einer quadratischen Matrix, die unter anderem Auskunft darüber gibt, ob die Matrix invertierbar ist. Sie spielt in vielen Bereichen der linearen Algebra eine zentrale Rolle.

### Determinante einer 2x2-Matrix

Für eine $2 \times 2$-Matrix ist die Determinante definiert als:

$$
\det \begin{pmatrix} a & b \\ c & d \end{pmatrix} = a \cdot d - b \cdot c
$$

Man bildet also das Produkt der **Hauptdiagonale** minus das Produkt der **Nebendiagonale**.

### Beispiel

$$
\det \begin{pmatrix} 3 & 2 \\ 1 & 5 \end{pmatrix} = 3 \cdot 5 - 2 \cdot 1 = 13
$$

### Determinante einer 3x3-Matrix: Regel von Sarrus

Für eine $3 \times 3$-Matrix verwenden wir die **Regel von Sarrus**. Dabei werden die ersten beiden Spalten rechts neben die Matrix geschrieben und dann die Produkte entlang der Diagonalen gebildet:

$$
\det \begin{pmatrix} a_{11} & a_{12} & a_{13} \\ a_{21} & a_{22} & a_{23} \\ a_{31} & a_{32} & a_{33} \end{pmatrix} = a_{11} a_{22} a_{33} + a_{12} a_{23} a_{31} + a_{13} a_{21} a_{32} - a_{13} a_{22} a_{31} - a_{11} a_{23} a_{32} - a_{12} a_{21} a_{33}
$$

Die drei Produkte von links oben nach rechts unten werden addiert, die drei Produkte von rechts oben nach links unten werden subtrahiert.

### Beispiel

$$
\det \begin{pmatrix} 1 & 2 & 3 \\ 4 & 5 & 6 \\ 7 & 8 & 0 \end{pmatrix}
$$

$$
\begin{align*}
&= 1 \cdot 5 \cdot 0 + 2 \cdot 6 \cdot 7 + 3 \cdot 4 \cdot 8 - 3 \cdot 5 \cdot 7 - 1 \cdot 6 \cdot 8 - 2 \cdot 4 \cdot 0 \\
&= 0 + 84 + 96 - 105 - 48 - 0 \\
&= 27
\end{align*}
$$

{% include dev/check-anker.html nummer="8" %}

{% include dev/check-anker.html nummer="9" %}

### Determinante einer 4x4-Matrix: Laplace-Entwicklung

Für $4 \times 4$-Matrizen (und größere) verwenden wir die **Laplace-Entwicklung**. Dabei wird die Determinante nach einer Zeile oder Spalte entwickelt und auf kleinere Determinanten zurückgeführt. Entwicklung nach der ersten Zeile:

$$
\det(A) = \sum_{j=1}^{4} (-1)^{1+j} \cdot a_{1j} \cdot \det(A_{1j})
$$

Dabei ist $A_{1j}$ die $3 \times 3$-Matrix, die durch Streichen der 1. Zeile und $j$-ten Spalte entsteht. Es empfiehlt sich, nach einer Zeile oder Spalte mit möglichst vielen Nullen zu entwickeln.

{% include dev/check-anker.html nummer="10" %}

### Zusammenhang mit der Invertierbarkeit

Die Determinante entscheidet, ob eine Matrix invertierbar ist:

$$
\det(A) \neq 0 \iff A \text{ ist invertierbar}
$$

$$
\det(A) = 0 \iff A \text{ ist singulär (nicht invertierbar)}
$$

### Ganzzahlige Invertierbarkeit

Eine Matrix $A$ mit ganzzahligen Einträgen ist genau dann über $\mathbb{Z}$ invertierbar (d. h. auch $A^{-1}$ hat ausschließlich ganzzahlige Einträge), wenn $\det(A) = \pm 1$.

### Weitere Eigenschaften

- $\det(A \cdot B) = \det(A) \cdot \det(B)$
- $\det(A^T) = \det(A)$
- $\det(\lambda \cdot A) = \lambda^n \cdot \det(A)$ für eine $n \times n$-Matrix
- $\det(E_n) = 1$
- $\det(A^{-1}) = \frac{1}{\det(A)}$, falls $A$ invertierbar