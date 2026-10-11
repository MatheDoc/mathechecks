---
layout: shell
title: "Check-Warm-Up (Prototyp): Rangkriterium"
description: Isolierter Prototyp eines Check-Warm-Ups zum Check „Rangkriterium“.
page_context: Prototyp
nav: dashboard
body_class: page-module page-check-warmup-prototype
noindex: true
published: true
lernbereich: lineare-gleichungssysteme
gebiet: lineare-algebra
prototype_key: check-warmup
page_css: /assets/css/check-warmup-prototype.css?v=20261011-card5
module_script: /assets/js/modules/check-warmup-prototype.js?v=20261011-card5
permalink: /prototypen/check-warmup/rangkriterium.html

warmup:
  check_id: lineare-algebra__lineare-gleichungssysteme__05
  nummer: 5
  lernbereich_name: 'Lineare Gleichungssysteme'
  titel: 'Rangkriterium'
  kompetenz: 'mit Hilfe des Rang-Kriteriums die Anzahl der Lösungen eines linearen Gleichungssystems bestimmen.'
  training_url: /lernbereiche/lineare-algebra/lineare-gleichungssysteme/training.html#check-5
  abschluss: '<p>Im Training bekommst du genau diese vier Fragen – zu immer neuen Matrizen in Stufenform.</p>'
  karten:

    # ── Phase A: Orientierung ──────────────────────────────────
    - phase: orientierung
      titel: 'Eine, keine oder unendlich viele?'
      text: '<p>Ein LGS in Stufenform verrät seine Lösungsanzahl schon in der <strong>letzten Zeile</strong>. Drei Beispiele mit den Unbekannten $x_1$ und $x_2$:</p><div class="cw-formula-row"><div>$$\text{(I)}\quad\left(\begin{array}{cc|c}1&1&3\\0&1&1\end{array}\right)$$</div><div>$$\text{(II)}\quad\left(\begin{array}{cc|c}1&1&3\\0&0&2\end{array}\right)$$</div><div>$$\text{(III)}\quad\left(\begin{array}{cc|c}1&1&3\\0&0&0\end{array}\right)$$</div></div>'
      schritte:
        - typ: aufdecken
          frage: 'Was bedeutet die letzte Zeile jeweils als Gleichung?'
          knopf: 'Übersetzen'
          text: '<ul><li>(I): $0x_1+1x_2=1$, also $x_2=1$ – passt.</li><li>(II): $0x_1+0x_2=2$, also $0=2$ – unmöglich.</li><li>(III): $0x_1+0x_2=0$, also $0=0$ – immer wahr, sagt nichts aus.</li></ul>'
        - typ: zuordnen
          frage: 'Wie viele Lösungen hat welches LGS?'
          titel_links: 'LGS'
          titel_rechts: 'Lösungen'
          paare:
            - { links: 'LGS (I)', rechts: 'genau eine Lösung' }
            - { links: 'LGS (II)', rechts: 'keine Lösung' }
            - { links: 'LGS (III)', rechts: 'unendlich viele Lösungen' }
          danach: '<p>Das Rangkriterium macht aus diesem Hinschauen ein Verfahren: Es <strong>zählt Zeilen</strong>.</p>'

    # ── Phase B: Vormachen ─────────────────────────────────────
    - phase: vormachen
      titel: 'Zeilen zählen: der Rang'
      text: '<p>Der <strong>Rang</strong> einer Matrix in Stufenform ist die Anzahl ihrer Zeilen, die nicht nur aus Nullen bestehen. Gezählt wird zweimal: für $A$ (links vom Strich) und für $(A|y)$ (mit rechter Seite).</p>'
      visual:
        typ: matrix
        name: '$(A|y)=$'
        trenn: 3
        zeilen:
          - [1, 2, -1, 4]
          - [0, 1, 3, 2]
          - [0, 0, 0, 5]
      schritte:
        - typ: aufdecken
          frage: '<strong>$rg(A)$</strong> – nur der Teil links vom Strich zählt.'
          knopf: 'Zeilen markieren'
          text: '<p>Zeile 1 und 2 enthalten links vom Strich Zahlen ungleich $0$, Zeile 3 nur Nullen. Also ist $rg(A)=2$.</p>'
          zeige: { zeilen: [0, 1], bereich: A }
        - typ: markieren
          frage: '<strong>$rg(A|y)$</strong> – jetzt zählt die ganze Zeile. Tippe alle Zeilen an, die nicht nur aus Nullen bestehen.'
          bereich: Ay
          korrekt: [0, 1, 2]
          hinweis: 'In $(A|y)$ zählt auch die Zahl rechts vom Strich.'
          danach: '<p>Zeile 3 enthält rechts eine $5$. Also ist $rg(A|y)=3$.</p>'
        - typ: aufdecken
          frage: '<strong>$n$</strong> – die Anzahl der Unbekannten.'
          knopf: 'Zeigen'
          text: '<p>$A$ hat $3$ Spalten, also gibt es $3$ Unbekannte: $n=3$.</p>'
          zeige: { spalten: [0, 1, 2], bereich: A }
        - typ: aufdecken
          frage: '<strong>Entscheidung</strong>'
          knopf: 'Rangkriterium anwenden'
          text: '<p>$rg(A)=2\neq 3=rg(A|y)$ – die Ränge sind verschieden. Das LGS hat <strong>keine Lösung</strong>. Die dritte Zeile bedeutet ja $0=5$.</p>'
          zeige: { zeilen: [2], bereich: Ay }

    - phase: vormachen
      titel: 'Das Rangkriterium auf einen Blick'
      text: '<p>Mit den drei Zahlen $rg(A)$, $rg(A|y)$ und $n$ steht sofort fest, wie viele Lösungen es gibt:</p><table class="cw-table"><tr><th>Bedingung</th><th>Lösungen</th></tr><tr><td>$rg(A)\neq rg(A|y)$</td><td>keine</td></tr><tr><td>$rg(A)=rg(A|y)=n$</td><td>genau eine</td></tr><tr><td>$rg(A)=rg(A|y)&lt;n$</td><td>unendlich viele</td></tr></table>'
      schritte:
        - typ: auswahl
          frage: 'Zurück zu LGS (III) vom Anfang: Dort ist $rg(A)=rg(A|y)=1$ und $n=2$. Was folgt?'
          optionen:
            - 'keine Lösung'
            - 'genau eine Lösung'
            - 'unendlich viele Lösungen'
          korrekt: 2
          hinweis: 'Die Ränge sind gleich. Vergleiche sie jetzt mit $n$.'
          danach: '<p>Richtig: Die Ränge sind gleich, aber kleiner als $n$. Eine Unbekannte bleibt frei wählbar.</p>'

    # ── Phase C: Mitmachen ─────────────────────────────────────
    - phase: mitmachen
      titel: 'Du zählst'
      text: '<p>Neue Matrix. Markieren und Zählen übernimmst du, die Spaltenzahl steht schon da.</p>'
      visual:
        typ: matrix
        name: '$(A|y)=$'
        trenn: 3
        zeilen:
          - [2, -1, 3, 1]
          - [0, 4, 1, 3]
          - [0, 0, 2, 6]
      schritte:
        - typ: markieren
          frage: 'Tippe die Zeilen an, die <strong>links vom Strich</strong> nicht nur aus Nullen bestehen.'
          bereich: A
          korrekt: [0, 1, 2]
          hinweis: 'Schau nur links vom Strich: Steht dort irgendwo eine Zahl ungleich $0$?'
        - typ: eingabe
          felder:
            - { label: '$rg(A)=$', loesung: 3 }
            - { label: '$rg(A|y)=$', loesung: 3 }
          hinweis: 'Zähle die Zeilen, die nicht nur aus Nullen bestehen – einmal ohne, einmal mit der rechten Seite.'
        - typ: text
          text: '<p>$n=3$, denn $A$ hat drei Spalten.</p>'
          zeige: { spalten: [0, 1, 2], bereich: A }
        - typ: auswahl
          frage: 'Was folgt?'
          optionen:
            - 'keine Lösung'
            - 'genau eine Lösung'
            - 'unendlich viele Lösungen'
          korrekt: 1
          hinweis: 'Vergleiche zuerst die beiden Ränge miteinander, dann mit $n$.'
          danach: '<p>$rg(A)=rg(A|y)=n=3$ – genau eine Lösung.</p>'

    - phase: mitmachen
      titel: 'Fast wie im Training'
      text: '<p>Jetzt ohne Markierhilfe. Achtung: Diese Matrix hat mehr Spalten als Zeilen.</p>'
      visual:
        typ: matrix
        name: '$(A|y)=$'
        trenn: 4
        zeilen:
          - [1, 3, -2, 0, 5]
          - [0, 0, 1, 4, 2]
      schritte:
        - typ: eingabe
          felder:
            - { label: '$rg(A)=$', loesung: 2 }
            - { label: '$rg(A|y)=$', loesung: 2 }
            - { label: '$n=$', loesung: 4 }
          hinweis: '$n$ ist die Anzahl der Spalten von $A$ – nicht die Anzahl der Zeilen.'
        - typ: auswahl
          frage: 'Folgerung zur Lösungsmenge:'
          optionen:
            - 'keine Lösung'
            - 'genau eine Lösung'
            - 'unendlich viele Lösungen'
          korrekt: 2
          hinweis: 'Die Ränge sind gleich – vergleiche sie mit $n$.'
          danach: '<p>$rg(A)=rg(A|y)=2&lt;4=n$ – unendlich viele Lösungen. Zwei Unbekannte bleiben frei wählbar.</p>'
---

<div class="page-shell w-wide">
  <section id="check-warmup-root" class="cw-root">
    <p class="module-status">Das Warm-Up wird geladen …</p>
  </section>
</div>

<script type="application/json" id="check-warmup-data">{{ page.warmup | jsonify }}</script>
