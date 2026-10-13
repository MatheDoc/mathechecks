---
layout: shell
title: "Warm-Up (Prototyp): Baumdiagramm bei Unabhängigkeit"
description: Isolierter Prototyp eines Warm-Ups zum Check „Baumdiagramm vervollständigen bei Unabhängigkeit“.
page_context: Prototyp
nav: dashboard
body_class: page-module page-check-warmup-prototype
noindex: true
published: true
lernbereich: bedingte-wahrscheinlichkeiten
gebiet: stochastik
prototype_key: check-warmup
page_css: /assets/css/check-warmup-prototype.css?v=20261012-mobile4
module_script: /assets/js/modules/check-warmup-prototype.js?v=20261012-mobile4
permalink: /prototypen/check-warmup/baumdiagramm-unabhaengigkeit.html

warmup:
  check_id: stochastik__bedingte-wahrscheinlichkeiten__02
  nummer: 2
  lernbereich_name: 'Bedingte Wahrscheinlichkeiten'
  titel: 'Baumdiagramm vervollständigen bei Unabhängigkeit'
  kompetenz: 'Baumdiagramme unter Verwendung stochastischer Unabhängigkeit vervollständigen.'
  training_url: /lernbereiche/stochastik/bedingte-wahrscheinlichkeiten/training.html#check-2
  abschluss: '<p>Im Training stehen die Bäume in einem Sachkontext. Achte im Text auf den Satz zur Unabhängigkeit, runde wie angegeben und trag die Werte in die Felder ① bis ⑩ ein.</p>'
  karten:

    # ── Phase A: Orientierung ──────────────────────────────────
    - phase: orientierung
      titel: 'Ein Baum mit zwei gleichen Ästen'
      text: '<p>In einem Café zahlen $40\,\%$ der Gäste mit Karte ($A$), und $30\,\%$ bestellen einen Kaffee ($B$). <strong>Die Zahlungsart hat keinen Einfluss darauf, ob jemand Kaffee bestellt.</strong></p>'
      visual:
        typ: baum
        modus: numeric
        pa: 0.4
        pba: 0.3
        pbna: 0.3
        dezimal: 2
      schritte:
        - typ: auswahl
          frage: 'Vergleiche die zweite Stufe (rechts). Was fällt dir auf?'
          optionen:
            - 'Oben und unten stehen dieselben Wahrscheinlichkeiten für $B$ und $\overline{B}$.'
            - 'Alle Wahrscheinlichkeiten im Baum sind gleich groß.'
            - 'Die vier Endwahrscheinlichkeiten ergeben zusammen $2$.'
          korrekt: 0
          hinweis: 'Schau nur auf die vier Äste der zweiten Stufe.'
          danach: '<p>Genau: $P_A(B)=P_{\overline{A}}(B)=0{,}3$. Ob $A$ eintritt oder nicht, ändert nichts an der Wahrscheinlichkeit für $B$. $A$ und $B$ heißen dann <strong>stochastisch unabhängig</strong>.</p>'
        - typ: auswahl
          frage: 'Woran erkennst du Unabhängigkeit in einer Aufgabe?'
          optionen:
            - 'An einem Satz wie „… hat keinen Einfluss auf …“'
            - 'Daran, dass $P(A)$ kleiner als $0{,}5$ ist'
            - 'Daran, dass das Baumdiagramm zwei Stufen hat'
          korrekt: 0
          hinweis: 'Lies den Aufgabentext oben noch einmal.'
          danach: '<p>Richtig. Steht so ein Satz im Text, darfst du die Wahrscheinlichkeiten der zweiten Stufe von einem Ast auf den anderen übertragen. Genau darum geht es in diesem Check.</p>'

    # ── Phase B: Vormachen ─────────────────────────────────────
    - phase: vormachen
      titel: 'Vervollständigen – Schritt für Schritt'
      text: '<p>$A$ und $B$ sind unabhängig. Gegeben sind nur zwei Endwahrscheinlichkeiten: $⑦=0{,}12$ und $⑧=0{,}28$. Gesucht sind alle übrigen Werte.</p>'
      visual:
        typ: baum
        pa: 0.4
        pba: 0.3
        pbna: 0.3
        gegeben: [7, 8]
        dezimal: 2
      schritte:
        - typ: aufdecken
          frage: '<strong>①</strong> – Pfadadditionsregel: Die beiden Pfade über $A$ ergeben zusammen $P(A)$.'
          knopf: 'Rechnung zeigen'
          text: '$$①=0{,}12+0{,}28=0{,}4$$'
          zeige: { slots: [1] }
        - typ: aufdecken
          frage: '<strong>③</strong> – Pfadmultiplikationsregel rückwärts: $①\cdot ③=⑦$.'
          knopf: 'Rechnung zeigen'
          text: '$$③=\frac{0{,}12}{0{,}4}=0{,}3$$'
          zeige: { slots: [3] }
        - typ: aufdecken
          frage: '<strong>④</strong> – An jedem Knoten ergeben die Äste zusammen $1$.'
          knopf: 'Rechnung zeigen'
          text: '$$④=1-0{,}3=0{,}7$$'
          zeige: { slots: [4] }
        - typ: auswahl
          frage: '<strong>⑤</strong> – Jetzt kommt die Unabhängigkeit ins Spiel. Was gilt?'
          optionen:
            - '$⑤=④=0{,}7$'
            - '$⑤=①=0{,}4$'
            - '$⑤=③=0{,}3$'
          korrekt: 2
          hinweis: 'Bei Unabhängigkeit sieht die zweite Stufe oben und unten gleich aus.'
          danach: '<p>Genau: $P_{\overline{A}}(B)=P_A(B)=0{,}3$ und damit auch $⑥=0{,}7$.</p>'
          zeige: { slots: [5, 6] }
        - typ: aufdecken
          frage: 'Der Rest geht wie gewohnt.'
          knopf: 'Rest zeigen'
          text: '$$\begin{align*}②&=1-0{,}4=0{,}6\\ ⑨&=0{,}6\cdot 0{,}3=0{,}18\\ ⑩&=0{,}6\cdot 0{,}7=0{,}42\end{align*}$$'
          zeige: { slots: [2, 9, 10] }

    # ── Phase C: Mitmachen ─────────────────────────────────────
    - phase: mitmachen
      titel: 'Du füllst den Baum'
      text: '<p>Neuer Baum, wieder sind $A$ und $B$ unabhängig. Gegeben sind $①=0{,}6$ und $⑤=0{,}25$.</p>'
      visual:
        typ: baum
        pa: 0.6
        pba: 0.25
        pbna: 0.25
        gegeben: [1, 5]
        dezimal: 2
      schritte:
        - typ: eingabe
          frage: 'Zuerst die Gegenwahrscheinlichkeiten.'
          felder:
            - { label: '$②=1-0{,}6=$', loesung: 0.4, zeige: { slots: [2] } }
            - { label: '$⑥=1-0{,}25=$', loesung: 0.75, zeige: { slots: [6] } }
          hinweis: 'Rechne jeweils $1$ minus den gegebenen Wert am selben Knoten.'
        - typ: auswahl
          frage: 'Wie kommst du an ③?'
          optionen:
            - '$③=⑥$'
            - '$③=⑤$ wegen Unabhängigkeit'
            - '$③=1-①$'
          korrekt: 1
          hinweis: '③ gehört zu $B$ – welcher Ast im unteren Teil gehört auch zu $B$?'
          danach: '<p>Also $③=0{,}25$ und damit $④=0{,}75$.</p>'
          zeige: { slots: [3, 4] }
        - typ: eingabe
          frage: 'Jetzt die Endwahrscheinlichkeiten – Pfadmultiplikationsregel. Der erste Ansatz steht da.'
          felder:
            - { label: '$⑦=0{,}6\cdot 0{,}25=$', loesung: 0.15, zeige: { slots: [7] } }
            - { label: '$⑧=$', loesung: 0.45, zeige: { slots: [8] } }
            - { label: '$⑨=$', loesung: 0.1, zeige: { slots: [9] } }
            - { label: '$⑩=$', loesung: 0.3, zeige: { slots: [10] } }
          hinweis: 'Multipliziere entlang des Pfades: Wert der ersten Stufe mal Wert der zweiten Stufe.'
          danach: '<p>Zur Kontrolle: $0{,}15+0{,}45+0{,}1+0{,}3=1$ ✓</p>'

    - phase: mitmachen
      titel: 'Der knifflige Fall'
      text: '<p>So sehen viele Trainingsaufgaben aus: Gegeben sind ein Ast unten und ein Pfadende oben. $A$ und $B$ sind unabhängig, gegeben sind $⑤=0{,}6$ und $⑧=0{,}12$.</p>'
      visual:
        typ: baum
        pa: 0.3
        pba: 0.6
        pbna: 0.6
        gegeben: [5, 8]
        dezimal: 2
      schritte:
        - typ: auswahl
          frage: 'Womit fängst du an?'
          optionen:
            - '$①=1-⑧$'
            - '$③=⑤=0{,}6$ wegen Unabhängigkeit'
            - '$⑦=⑤\cdot ⑧$'
          korrekt: 1
          hinweis: 'Nutze zuerst die Unabhängigkeit.'
          zeige: { slots: [3] }
        - typ: eingabe
          frage: '<strong>④</strong> – Gegenwahrscheinlichkeit am Knoten $A$.'
          felder:
            - { label: '$④=$', loesung: 0.4, zeige: { slots: [4] } }
          hinweis: '③ und ④ ergeben zusammen $1$.'
        - typ: eingabe
          frage: '<strong>①</strong> – Pfadmultiplikationsregel rückwärts: $①\cdot ④=⑧$.'
          felder:
            - { label: '$①=$', loesung: 0.3, zeige: { slots: [1] } }
          hinweis: 'Teile $⑧=0{,}12$ durch $④=0{,}4$.'
        - typ: eingabe
          frage: 'Den Rest schaffst du allein.'
          felder:
            - { label: '$②=$', loesung: 0.7, zeige: { slots: [2] } }
            - { label: '$⑥=$', loesung: 0.4, zeige: { slots: [6] } }
            - { label: '$⑦=$', loesung: 0.18, zeige: { slots: [7] } }
            - { label: '$⑨=$', loesung: 0.42, zeige: { slots: [9] } }
            - { label: '$⑩=$', loesung: 0.28, zeige: { slots: [10] } }
          hinweis: 'Erst die Gegenwahrscheinlichkeiten an den Knoten, dann die Pfadmultiplikationsregel.'
          danach: '<p>Geschafft – genau dieser Weg führt auch durch die Trainingsaufgaben.</p>'
---

<div class="page-shell w-wide">
  <section id="check-warmup-root" class="cw-root">
    <p class="module-status">Das Warm-Up wird geladen …</p>
  </section>
</div>

<script type="application/json" id="check-warmup-data">{{ page.warmup | jsonify }}</script>
