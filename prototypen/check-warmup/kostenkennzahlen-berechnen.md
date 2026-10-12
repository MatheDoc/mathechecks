---
layout: shell
title: "Check-Warm-Up (Prototyp): Kostenkennzahlen berechnen"
description: Isolierter Prototyp eines Check-Warm-Ups zum Check „Kostenkennzahlen berechnen“.
page_context: Prototyp
nav: dashboard
body_class: page-module page-check-warmup-prototype
noindex: true
published: true
lernbereich: ertragsgesetzliche-kostenfunktionen
gebiet: analysis
prototype_key: check-warmup
page_css: /assets/css/check-warmup-prototype.css?v=20261012-mobile4
module_script: /assets/js/modules/check-warmup-prototype.js?v=20261012-mobile4
permalink: /prototypen/check-warmup/kostenkennzahlen-berechnen.html

# Hinweis YAML: In einfachen Anführungszeichen wird ' verdoppelt: 'K''(x)' ergibt K'(x).
# Höhere Ableitungen daher als K^{\prime\prime} schreiben.
warmup:
  check_id: analysis__ertragsgesetzliche-kostenfunktionen__05
  nummer: 5
  lernbereich_name: 'Ertragsgesetzliche Kostenfunktionen'
  titel: 'Kostenkennzahlen berechnen'
  kompetenz: 'Kennzahlen ertragsgesetzlicher Kostenfunktionen berechnen.'
  training_url: /lernbereiche/analysis/ertragsgesetzliche-kostenfunktionen/training.html#check-5
  abschluss: '<p>Im Training bekommst du eine Kostenfunktion und bestimmst genau diese fünf Kennzahlen, auf 2 Nachkommastellen gerundet. Für Betriebsminimum und Betriebsoptimum wählst du den Weg selbst: Extremstelle oder Schnittstelle mit $K''$.</p>'
  karten:

    # ── Phase A: Orientierung ──────────────────────────────────
    - phase: orientierung
      titel: 'Drei Kurven, fünf Kennzahlen'
      text: '<p>Aus der Kostenfunktion</p>$$K(x)=0{,}5x^3-6x^2+30x+48$$<p>entstehen drei weitere Funktionen: die Grenzkosten $K''$, die variablen Stückkosten $k_v$ und die Stückkosten $k$. Fast alle Kennzahlen sind besondere Punkte dieser Kurven.</p>'
      visual:
        typ: graph
        funktionen:
          - { term: '1.5x^2-12x+30', name: 'K′(x)', xmin: 0, xmax: 12 }
          - { term: '0.5x^2-6x+30', name: 'k<sub>v</sub>(x)', xmin: 0, xmax: 12 }
          - { term: '0.5x^2-6x+30+48/x', name: 'k(x)', xmin: 1, xmax: 12 }
        xMin: -0.3
        xMax: 12
        yMin: 0
        yMax: 50
        xAchse: 'x in ME'
        yAchse: 'GE bzw. GE/ME'
        punkte:
          - { id: w, x: 4, y: 6, label: 'Übergang degr./progr.', ax: -70, ay: 10 }
          - { id: bm, x: 6, y: 12, label: 'Betriebsminimum', ax: 70, ay: 26 }
          - { id: bo, x: 6.98, y: 19.36, label: 'Betriebsoptimum', ax: 66, ay: -30 }
      schritte:
        - typ: aufdecken
          knopf: 'Zeig mir die Tiefpunkte'
          text: '<p>Der Tiefpunkt von $k_v$ liegt beim <strong>Betriebsminimum</strong>, der Tiefpunkt von $k$ beim <strong>Betriebsoptimum</strong>. Die $y$-Werte dieser Tiefpunkte sind die <strong>kurzfristige</strong> bzw. <strong>langfristige Preisuntergrenze</strong>.</p>'
          zeige: { punkte: [bm, bo] }
        - typ: auswahl
          frage: 'Schau dir die Grenzkostenkurve $K''$ an. Was fällt dir auf?'
          optionen:
            - 'Sie geht genau durch beide Tiefpunkte.'
            - 'Sie hat ihren Tiefpunkt beim Betriebsminimum.'
            - 'Sie schneidet $k_v$ und $k$ überhaupt nicht.'
          korrekt: 0
          hinweis: 'Verfolge die Kurve $K''$ und achte auf die beiden markierten Punkte.'
          danach: '<p>Genau – und das ist kein Zufall. Deshalb gibt es für Betriebsminimum und Betriebsoptimum <strong>zwei Wege</strong>: als Extremstelle (Tiefpunkt) von $k_v$ bzw. $k$ oder als Schnittstelle mit $K''$.</p>'
        - typ: auswahl
          frage: 'Der Tiefpunkt von $K''$ liegt bei $x=4$. Welche Kennzahl ist das?'
          optionen:
            - 'Übergang vom degressiven zum progressiven Kostenwachstum'
            - 'Betriebsminimum'
            - 'Kurzfristige Preisuntergrenze'
          korrekt: 0
          hinweis: 'Bis dahin steigen die Kosten immer langsamer, danach immer schneller.'
          danach: '<p>Richtig: Dort ist die Steigung von $K$ am kleinsten – das ist die Wendestelle von $K$.</p>'
          zeige: { punkte: [w] }

    # ── Phase B: Vormachen ─────────────────────────────────────
    - phase: vormachen
      titel: 'Funktionen und Wendestelle'
      text: '<p>Für alle Kennzahlen brauchst du zuerst die passenden Funktionen.</p>'
      schritte:
        - typ: aufdecken
          frage: 'Aus $$K(x)=0{,}5x^3-6x^2+30x+48$$ ergeben sich:'
          knopf: 'Funktionen bilden'
          text: '$$\begin{align*}K''(x)&=1{,}5x^2-12x+30\\ k_v(x)&=0{,}5x^2-6x+30\\ k(x)&=0{,}5x^2-6x+30+\frac{48}{x}\end{align*}$$<p>Grenzkosten $K''$: ableiten. Variable Stückkosten $k_v$: Fixkosten weglassen und durch $x$ teilen. Stückkosten $k$: alles durch $x$ teilen.</p>'
        - typ: auswahl
          frage: '<strong>Übergang degressiv → progressiv</strong> – das ist die Wendestelle von $K$. Welcher Ansatz passt?'
          optionen:
            - '$K''(x)=0$'
            - '$K^{\prime\prime}(x)=0$'
            - '$k_v''(x)=0$'
          korrekt: 1
          hinweis: 'Wendestellen sind Nullstellen der zweiten Ableitung.'
          danach: '$$\begin{align*}K^{\prime\prime}(x)=3x-12&=0\;\Rightarrow\; x=4\\ K^{\prime\prime\prime}(4)&=3>0\end{align*}$$<p>Der Übergang vom degressiven zum progressiven Kostenwachstum liegt bei $4$ ME.</p>'

    - phase: vormachen
      titel: 'Betriebsminimum – zwei Wege'
      text: '<p>Das Betriebsminimum ist die Menge mit den geringsten variablen Stückkosten.</p>'
      visual:
        typ: graph
        funktionen:
          - { term: '1.5x^2-12x+30', name: 'K′(x)', xmin: 0, xmax: 12 }
          - { term: '0.5x^2-6x+30', name: 'k<sub>v</sub>(x)', xmin: 0, xmax: 12 }
        xMin: -0.3
        xMax: 12
        yMin: 0
        yMax: 50
        xAchse: 'x in ME'
        yAchse: 'GE/ME'
        punkte:
          - { id: bm, x: 6, y: 12, label: 'Betriebsminimum', hilfslinie: true, ax: 70, ay: 26 }
      schritte:
        - typ: aufdecken
          frage: '<strong>Weg 1: Extremstelle von $k_v$</strong> – Ableitung null setzen.'
          knopf: 'Rechnung zeigen'
          text: '$$\begin{align*}k_v''(x)=x-6&=0\\ x&=6\\ k_v^{\prime\prime}(6)=1&>0\;(\text{Minimum})\end{align*}$$'
        - typ: aufdecken
          frage: '<strong>Weg 2: Schnittstelle von $K''$ und $k_v$</strong> – gleichsetzen.'
          knopf: 'Rechnung zeigen'
          text: '<p>$K''(x)=k_v(x)$ setzen:</p>$$\begin{align*}1{,}5x^2-12x+30&=0{,}5x^2-6x+30\\ x^2-6x&=0\\ x(x-6)&=0\end{align*}$$<p>Dafür auf beiden Seiten $0{,}5x^2$ abziehen, $6x$ addieren und $30$ abziehen. Also $x=0$ oder $x=6$.</p>'
          zeige: { punkte: [bm] }
        - typ: auswahl
          frage: 'Welche Lösung ist das Betriebsminimum?'
          optionen:
            - '$x=0$'
            - '$x=6$'
          korrekt: 1
          hinweis: 'Bei $0$ ME gibt es keine Stückkosten – $k_v(x)=\frac{K_v(x)}{x}$ ist dort nicht definiert.'
          danach: '<p>Beide Wege liefern $x_{BM}=6$ ME. Beim Schnittstellen-Weg brauchst du weder die Ableitung von $k_v$ noch die Prüfung mit der zweiten Ableitung.</p>'
        - typ: eingabe
          frage: '<strong>Kurzfristige Preisuntergrenze</strong> – der Wert von $k_v$ im Betriebsminimum: $$k_v(6)=0{,}5\cdot 36-6\cdot 6+30$$'
          felder:
            - { label: '$k_v(6)=$', loesung: 12, einheit: 'GE/ME' }
          hinweis: 'Rechne $18-36+30$.'
          danach: '<p>Zur Kontrolle: Auch $K''(6)=12$ – der Schnittpunkt liegt genau im Tiefpunkt.</p>'

    - phase: vormachen
      titel: 'Betriebsoptimum – zwei Wege'
      text: '<p>Das Betriebsoptimum ist die Menge mit den geringsten Stückkosten. Hier steckt $\frac{48}{x}$ in der Funktion.</p>'
      visual:
        typ: graph
        funktionen:
          - { term: '1.5x^2-12x+30', name: 'K′(x)', xmin: 0, xmax: 12 }
          - { term: '0.5x^2-6x+30+48/x', name: 'k(x)', xmin: 1, xmax: 12 }
        xMin: -0.3
        xMax: 12
        yMin: 0
        yMax: 50
        xAchse: 'x in ME'
        yAchse: 'GE/ME'
        punkte:
          - { id: bo, x: 6.98, y: 19.36, label: 'Betriebsoptimum', hilfslinie: true, ax: 66, ay: -30 }
      schritte:
        - typ: auswahl
          frage: '<strong>Weg 1: Extremstelle von $k$</strong> – zuerst ableiten. Was ist die Ableitung von $\frac{48}{x}$?'
          optionen:
            - '$-\frac{48}{x^2}$'
            - '$\frac{48}{x^2}$'
            - '$48$'
          korrekt: 0
          hinweis: 'Schreibe $\frac{48}{x}=48x^{-1}$ und wende die Potenzregel an.'
          danach: '$$\begin{align*}k''(x)=x-6-\frac{48}{x^2}&=0 \quad|\cdot x^2\\ x^3-6x^2-48&=0\end{align*}$$'
        - typ: aufdecken
          frage: '<strong>Weg 2: Schnittstelle von $K''$ und $k$</strong> – gleichsetzen.'
          knopf: 'Rechnung zeigen'
          text: '<p>$K''(x)=k(x)$ setzen:</p>$$\begin{align*}1{,}5x^2-12x+30&=0{,}5x^2-6x+30+\tfrac{48}{x}\\ x^2-6x-\tfrac{48}{x}&=0 \quad|\cdot x\\ x^3-6x^2-48&=0\end{align*}$$<p>Im ersten Schritt wie beim Betriebsminimum: $0{,}5x^2$ abziehen, $6x$ addieren, $30$ abziehen.</p>'
        - typ: auswahl
          frage: 'Vergleiche die beiden Wege. Was fällt dir auf?'
          optionen:
            - 'Beide führen auf dieselbe Gleichung.'
            - 'Weg 2 liefert ein anderes Ergebnis.'
            - 'Weg 1 kommt ohne Ableitung aus.'
          korrekt: 0
          hinweis: 'Vergleiche jeweils die letzte Zeile.'
          danach: '<p>Genau. Du kannst also den Weg wählen, der dir leichter fällt.</p>'
        - typ: aufdecken
          frage: 'Die Gleichung $x^3-6x^2-48=0$ löst du mit dem Taschenrechner.'
          knopf: 'Lösen'
          text: '<p>$x_{BO}\approx 6{,}98$ ME. Beim Weg über die Extremstelle prüfst du noch $k^{\prime\prime}(6{,}98)\approx 1{,}28>0$ (Minimum).</p><p><strong>Langfristige Preisuntergrenze:</strong> $k(6{,}98)\approx 19{,}36$ GE/ME.</p>'
          zeige: { punkte: [bo] }

    # ── Phase C: Mitmachen ─────────────────────────────────────
    - phase: mitmachen
      titel: 'Welcher Ansatz gehört wozu?'
      text: '<p>Fünf Kennzahlen – ordne jeder ihren Ansatz zu.</p>'
      schritte:
        - typ: zuordnen
          titel_links: 'Kennzahl'
          titel_rechts: 'Ansatz'
          paare:
            - { links: 'Übergang degressiv → progressiv', rechts: '$K^{\prime\prime}(x)=0$' }
            - { links: 'Betriebsminimum', rechts: '$k_v''(x)=0$ oder $K''(x)=k_v(x)$' }
            - { links: 'kurzfristige Preisuntergrenze', rechts: '$k_v(x_{BM})$' }
            - { links: 'Betriebsoptimum', rechts: '$k''(x)=0$ oder $K''(x)=k(x)$' }
            - { links: 'langfristige Preisuntergrenze', rechts: '$k(x_{BO})$' }
          danach: '<p>Betriebsminimum und kurzfristige Preisuntergrenze gehören zu $k_v$: Kurzfristig müssen nur die variablen Kosten gedeckt sein. Betriebsoptimum und langfristige Preisuntergrenze gehören zu $k$: Langfristig müssen auch die Fixkosten gedeckt sein.</p>'

    - phase: mitmachen
      titel: 'Neue Funktion – Betriebsminimum'
      text: '<p>Jetzt gilt</p>$$K(x)=0{,}5x^3-9x^2+60x+100$$<p>mit</p>$$\begin{align*}K''(x)&=1{,}5x^2-18x+60\\ k_v(x)&=0{,}5x^2-9x+60\end{align*}$$'
      visual:
        typ: graph
        funktionen:
          - { term: '1.5x^2-18x+60', name: 'K′(x)', xmin: 0, xmax: 16 }
          - { term: '0.5x^2-9x+60', name: 'k<sub>v</sub>(x)', xmin: 0, xmax: 16 }
          - { term: '0.5x^2-9x+60+100/x', name: 'k(x)', xmin: 1.5, xmax: 16 }
        xMin: -0.3
        xMax: 16
        yMin: 0
        yMax: 80
        xAchse: 'x in ME'
        yAchse: 'GE bzw. GE/ME'
        punkte:
          - { id: w, x: 6, y: 6, label: 'Übergang', ax: -50, ay: 12 }
          - { id: bm, x: 9, y: 19.5, label: 'Betriebsminimum', ax: 36, ay: 40 }
      schritte:
        - typ: eingabe
          frage: '<strong>Übergang degressiv → progressiv</strong> – der Ansatz steht da: $K^{\prime\prime}(x)=3x-18=0$'
          felder:
            - { label: '$x=$', loesung: 6, einheit: 'ME', zeige: { punkte: [w] } }
          hinweis: 'Löse $3x=18$.'
        - typ: eingabe
          frage: '<strong>Betriebsminimum, Weg 1:</strong> $k_v''(x)=x-9=0$'
          felder:
            - { label: '$x_{BM}=$', loesung: 9, einheit: 'ME', zeige: { punkte: [bm] } }
          hinweis: 'Bring die $9$ auf die andere Seite.'
        - typ: eingabe
          frage: '<strong>Betriebsminimum, Weg 2:</strong> Setze $K''(x)=k_v(x)$ und bring alles auf eine Seite.'
          layout: zeile
          felder:
            - { einheit: '$x^2\;+$', loesung: 1 }
            - { einheit: '$x\;=\;0$', loesung: -9 }
          hinweis: '$1{,}5x^2-0{,}5x^2=x^2$ und $-18x+9x=-9x$. Die $60$ fällt weg.'
          danach: '<p>$x(x-9)=0$ – also wieder $x_{BM}=9$, denn $x=0$ entfällt.</p>'
        - typ: eingabe
          frage: '<strong>Kurzfristige Preisuntergrenze</strong> – jetzt ohne Vorgabe.'
          felder:
            - { label: '$k_v(9)=$', loesung: 19.5, einheit: 'GE/ME' }
          hinweis: 'Rechne $0{,}5\cdot 81-9\cdot 9+60$.'

    - phase: mitmachen
      titel: 'Betriebsoptimum – mit weniger Hilfe'
      text: '<p>Gleiche Funktion, jetzt mit den Stückkosten:</p>$$\begin{align*}K''(x)&=1{,}5x^2-18x+60\\ k(x)&=0{,}5x^2-9x+60+\frac{100}{x}\end{align*}$$'
      visual:
        typ: graph
        funktionen:
          - { term: '1.5x^2-18x+60', name: 'K′(x)', xmin: 0, xmax: 16 }
          - { term: '0.5x^2-9x+60', name: 'k<sub>v</sub>(x)', xmin: 0, xmax: 16 }
          - { term: '0.5x^2-9x+60+100/x', name: 'k(x)', xmin: 1.5, xmax: 16 }
        xMin: -0.3
        xMax: 16
        yMin: 0
        yMax: 80
        xAchse: 'x in ME'
        yAchse: 'GE bzw. GE/ME'
        punkte:
          - { id: w, x: 6, y: 6, label: 'Übergang', ax: -50, ay: 12, sichtbar: true }
          - { id: bm, x: 9, y: 19.5, label: 'Betriebsminimum', ax: 36, ay: 40, sichtbar: true }
          - { id: bo, x: 10, y: 30, label: 'Betriebsoptimum', hilfslinie: true, ax: 50, ay: -34 }
      schritte:
        - typ: auswahl
          frage: 'Welche Ansätze führen zum <strong>Betriebsoptimum</strong>?'
          optionen:
            - '$k''(x)=0$ oder $K''(x)=k(x)$'
            - '$k_v''(x)=0$ oder $K''(x)=k_v(x)$'
            - '$K^{\prime\prime}(x)=0$'
          korrekt: 0
          hinweis: 'Das Betriebsoptimum gehört zu den Stückkosten $k$.'
        - typ: eingabe
          frage: 'Nimm Weg 2: $K''(x)=k(x)$ setzen, alles auf eine Seite bringen und mit $x$ multiplizieren. Trag die Vorfaktoren ein.'
          layout: zeile
          felder:
            - { einheit: '$x^3\;+$', loesung: 1 }
            - { einheit: '$x^2\;+$', loesung: -9 }
            - { einheit: '$=\;0$', loesung: -100 }
          hinweis: 'Nach dem Gleichsetzen bleibt $x^2-9x-\frac{100}{x}=0$. Multipliziere mit $x$.'
          danach: '<p>Weg 1 führt auf dieselbe Gleichung:</p>$$\begin{align*}k''(x)=x-9-\frac{100}{x^2}&=0 \quad|\cdot x^2\\ x^3-9x^2-100&=0\end{align*}$$'
        - typ: eingabe
          frage: 'Löse $x^3-9x^2-100=0$ mit dem Taschenrechner.'
          felder:
            - { label: '$x_{BO}=$', loesung: 10, einheit: 'ME', zeige: { punkte: [bo] } }
          hinweis: 'Das Betriebsoptimum liegt immer rechts vom Betriebsminimum. Probiere ganze Zahlen ab $x=10$.'
        - typ: eingabe
          frage: '<strong>Langfristige Preisuntergrenze</strong> – jetzt ohne Vorgabe.'
          felder:
            - { label: '$k(10)=$', loesung: 30, einheit: 'GE/ME' }
          hinweis: 'Rechne $50-90+60+10$.'
          danach: '<p>Probe über den Schnittpunkt: $K''(10)=150-180+60=30$ ✓</p>'
---

<div class="page-shell w-wide">
  <section id="check-warmup-root" class="cw-root">
    <p class="module-status">Das Warm-Up wird geladen …</p>
  </section>
</div>

<script type="application/json" id="check-warmup-data">{{ page.warmup | jsonify }}</script>
