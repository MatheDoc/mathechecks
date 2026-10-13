# Warm-Up – Prototypen

Geführter, interaktiver Einstieg in **einen einzelnen Check**. Lernende sehen ein vorgerechnetes Beispiel, rechnen dann mit schrittweise weniger Hilfe mit und wechseln anschließend ins Training.

> **Status:** isolierter Prototyp. Nicht im Feed, nicht in `checks.json`, nicht verlinkt, `noindex`, nicht in der Sitemap. Die Seiten sind lokal und nach einem Deploy unter `/prototypen/check-warmup/…` direkt aufrufbar.

**Begriffe:** Die Aktivität heißt **„Warm-Up“**, technisch `module_key: warmup` (Kartenkopf „WARM-UP NN | Schlagwort“). Das frühere Warm-Up pro Lernbereich (Neugier-Karten aus `_data/warmup/<slug>.yml`) ist vollständig entfernt. Der Name ist damit frei. Das Präfix `check-warmup` in Ordner- und Dateinamen der Prototypen ist nur ein Überbleibsel aus der Prototyp-Phase und entfällt bei der Verzahnung.

## Vorhandene Prototypen

| Seite | Check | Erprobter Schwerpunkt |
|---|---|---|
| [marktgleichgewicht-berechnen.md](./marktgleichgewicht-berechnen.md) | `analysis__marktgleichgewicht-grundlagen__02` | Mehrere unabhängige Teilaufgaben; Fading nach Rechenmuster; Graph wächst mit |
| [kostenkennzahlen-berechnen.md](./kostenkennzahlen-berechnen.md) | `analysis__ertragsgesetzliche-kostenfunktionen__05` | Zwei gleichwertige Lösungswege (Extremstelle oder Schnittstelle mit $K'$); Erkenntnis am Graphen, dann beide Wege vorgemacht und geübt |
| [kostenfunktion-aufstellen.md](./kostenfunktion-aufstellen.md) | `analysis__ertragsgesetzliche-kostenfunktionen__06` | Informationen in Gleichungen übersetzen; Steckbrief wird abgehakt; Gleichungszeile |
| [baumdiagramm-unabhaengigkeit.md](./baumdiagramm-unabhaengigkeit.md) | `stochastik__bedingte-wahrscheinlichkeiten__02` | Ein Lösungsweg mit Schlüsselschritt; Baum füllt sich |
| [rangkriterium.md](./rangkriterium.md) | `lineare-algebra__lineare-gleichungssysteme__05` | Begriff und Verfahren; Zeilen in der Matrix antippen |

Übersicht: [index.md](./index.md) → `/prototypen/check-warmup/index.html`


## Entscheidungen (mit Begründung)

Festgehalten, damit spätere Arbeit nicht hinter diese Punkte zurückfällt.

| Entscheidung | Begründung |
|---|---|
| **Warm-Up pro Check, vor dem Training** | Wer neu in einem Thema ist, lernt mehr aus vorgerechneten Beispielen als aus selbst gelösten Aufgaben. Bisher startete die Check-Kette direkt mit dem Training, also mit dem selbstständigen Lösen. |
| **Das alte Warm-Up pro Lernbereich ist entfernt** | Neugier-Karten pro Lernbereich wurden nicht mehr benötigt. Name, Modulfarbe (`--mt-warmup`, `check-card--warmup`) und `module_key: warmup` gehen an das neue Warm-Up. |
| **Drei Phasen: Worum geht's? → Zuschauen → Mitmachen** | Eine vierte Phase „Jetzt du“ mit echter Trainingsaufgabe wurde gebaut und wieder entfernt. Sie war ein Doppel zum Training, das direkt danach kommt. |
| **Keine Karte, die einer Trainingsaufgabe entspricht** | Aus demselben Grund. Das Fading endet kurz davor, Hinweise fürs Training stehen im `abschluss`. |
| **Phasen statt fester Kartenzahl** | Checks sind unterschiedlich groß. Insgesamt 5–8 Karten. |
| **Fading nach Rechenmuster, nicht nach Teilaufgaben** | Teilaufgaben sind oft unabhängig voneinander. Die letzte Teilaufgabe einfach wegzulassen, wäre kein Fading. |
| **Scheinverständnis wird in Kauf genommen** | Der Einstieg soll leicht sein. Leichte Kontrollfragen (Auswahl, Zahl, Zuordnen) sorgen nur dafür, dass man nicht bloß durchklickt. |
| **„Zum Training →“ immer sichtbar** | Wer den Stoff schon kann, überspringt das Warm-Up. |
| **Gleichwertige Lösungswege beide zeigen** | z. B. Betriebsminimum als Extremstelle von $k_v$ oder als Schnittstelle von $K'$ und $k_v$. |
| **Kartendesign wie bei den anderen Modulen** | `check-card` mit Standard-Kartenkopf, feste Kartenhöhe, Scrollen nur im Kartenkörper, „Zurück/Weiter“ an festem Platz unter der Karte. Farbe: Warm-Up-Farbe (Terrakotta). |
| **Kein Phasen-Label vor dem Kartentitel** | Die Phasenleiste zeigt die Phase bereits an. Auf dem Handy war das Label zu viel. |
| **Ein gemeinsames Skript, Inhalte als Daten** | Wie beim Training: Ein Abspieler für alle Checks. Neue Interaktionen nur als allgemeine Schritt- oder Bildtypen. |
| **Daten im Front Matter nur für den Prototyp** | Bei der Verzahnung kommen sie in eigene Datendateien (siehe offene Punkte). |
| **Nicht verlinkt, nur über URL erreichbar** | Gilt auch nach der Verzahnung, bis ausdrücklich anders entschieden wird: kein Link aus Navigation, Skript, Training oder Feed, `noindex`, nicht in der Sitemap. Der Reiter in `_includes/module/nav.html` bleibt ausgeblendet. |


## Didaktische Leitlinien

1. **Leicht hinein, motivierender Einstieg.** Die erste Karte macht in wenigen Klicks klar, worum es geht. Sie ist kein Test.
2. **Lernen am vorgerechneten Beispiel, dann Fading.** Zuerst wird vorgemacht, dann übernehmen die Lernenden schrittweise selbst. Das Fading endet **kurz vor** der Trainingsaufgabe: Die letzte Mitmachen-Karte gibt noch eine kleine Hilfe oder übt einen Teilschritt.
3. **Ausgeblendet werden Lösungsschritte, nicht Teilaufgaben.** Bei unabhängigen Teilaufgaben richtet sich das Fading nach dem **Rechenmuster**. Beispiel Marktgleichgewicht: Höchstpreis und Mindestangebotspreis haben dasselbe Muster ($p(0)$). Den einen rechnet man mit Vorgabe, den anderen allein.
4. **Leichte Kontrollfragen statt bloßem Durchklicken.** Fast jeder Schritt verlangt eine kleine, aber echte Entscheidung: eine Auswahl, eine Zahl oder eine Zuordnung. Dass am Ende nicht alles verstanden ist, nehmen wir in Kauf.
5. **Kein Doppel zum Training.** Das Warm-Up endet mit „Weiter zum Training“ und enthält keine echte Trainingsaufgabe. Es gibt auch **keine Karte, die einer Trainingsaufgabe entspricht** (gleiche Fragen, keine Hilfe, z. B. „Fast wie im Training“). Wichtige Hinweise für das Training, etwa auf Fallen, gehören in den Abschlusstext `abschluss`.
6. **Übersprungen werden kann immer.** „Zum Training →“ steht im Kartenkopf.
7. **Lücken zum Training schließen.** Kommen in der Aufgabensammlung Informationstypen vor, die im Musterbeispiel fehlen, bekommen sie eine eigene kurze Vormachen-Karte. Beispiel Kostenfunktion: Stückkosten und Betriebsoptimum.
8. **Gleichwertige Lösungswege nebeneinander zeigen.** Gibt es zwei übliche Wege (z. B. Betriebsminimum als Extremstelle von $k_v$ oder als Schnittstelle von $K'$ und $k_v$), werden beide vorgemacht und in einer Kontrollfrage verglichen („Beide führen auf dieselbe Gleichung“). Beim Mitmachen wird mindestens einmal jeder Weg geübt, auf der letzten Karte ist der Weg frei wählbar. Am besten macht man die Gleichwertigkeit schon in der Orientierung am Graphen sichtbar.

### Phasen

| Phase (`phase`) | Anzeige | Zweck | Typischer Umfang |
|---|---|---|---|
| `orientierung` | Idee | Thema, Nutzen, ein Aha-Moment | 1 Karte, 1–3 Schritte |
| `vormachen` | Zuschauen | Musterbeispiel Schritt für Schritt, mit leichten Kontrollfragen | 1–3 Karten |
| `mitmachen` | Mitmachen | Neue Zahlen, Hilfe nimmt ab bis fast zur Trainingsaufgabe | 2–4 Karten |

Insgesamt 5–8 Karten. Die Zahl der Karten pro Phase ist frei.


## Technische Architektur

| Datei | Rolle |
|---|---|
| `prototypen/check-warmup/<name>.md` | Eine Seite pro Check. Alle Inhalte stehen im Front Matter unter `warmup:`. Liquid schreibt sie als JSON in `<script id="check-warmup-data">`. |
| `assets/js/modules/check-warmup-prototype.js` | **Ein** gemeinsames Skript, das das Datenformat für alle Checks abspielt. Es nutzt die vorhandenen Bausteine `visuals/graph.js`, `visuals/baumdiagramm.js`, `visuals/plotly-defaults.js` und `ui/check-meta.js`. |
| `assets/css/check-warmup-prototype.css` | Eigenes Stylesheet (Präfix `cw-`). Es wird über `page_css` nur auf diesen Seiten geladen. |

Layout: `layout: shell` mit `body_class: page-module page-check-warmup-prototype`. Die Karte ist eine echte `check-card check-card--warmup` mit dem Standard-Kartenkopf aus `renderCheckMetaRowMarkup`.

**Feste Kartenhöhe:** Die Karte füllt die Höhe zwischen Kopfleiste und Navigation. Nur der Kartenkörper (`.cw-body`) scrollt. Kartenkopf, Phasenleiste und „Zurück/Weiter“ bleiben an ihrem Platz. Ab 960 px stehen Bild und Schritte nebeneinander, und das Bild bleibt beim Scrollen stehen.

**Kartentitel ohne Phasen-Label:** Die aktuelle Phase zeigt allein die Phasenleiste. Vor dem Kartentitel steht kein eigenes Phasen-Label.

**Breitenbegrenzung:** Alle Rasterspalten im Warm-Up sind `minmax(0, 1fr)`. Sonst würde eine breite Formel die ganze Spalte und damit die Karte verbreitern. Abgesetzte Formeln (`mjx-container[display="true"]`) scrollen bei Bedarf in ihrem eigenen Kasten.

**Ablauf im Skript:**
- Die Schritte einer Karte erscheinen nacheinander.
- Ein Schritt gilt als erledigt, wenn er richtig gelöst oder aufgedeckt ist. Erst dann erscheint der nächste.
- „Weiter“ wird aktiv, sobald alle Schritte der Karte erledigt sind.
- Nach der letzten Karte erscheint der Abschlusskasten, und „Weiter zum Training“ wird aktiv.


## Datenformat (Front Matter)

Die Seite selbst ist immer gleich, nur das Front Matter unterscheidet sich:

```markdown
---
layout: shell
title: "Warm-Up (Prototyp): <Schlagwort>"
description: …
page_context: Prototyp
nav: dashboard
body_class: page-module page-check-warmup-prototype
noindex: true
published: true
lernbereich: <lernbereich-slug>
gebiet: <gebiet>
prototype_key: check-warmup
page_css: /assets/css/check-warmup-prototype.css?v=<version>
module_script: /assets/js/modules/check-warmup-prototype.js?v=<version>
permalink: /prototypen/check-warmup/<name>.html

warmup:
  check_id: <gebiet>__<lernbereich>__<NN>
  nummer: <NN>
  lernbereich_name: '<Anzeigename>'
  titel: '<Schlagwort aus checks.json>'
  kompetenz: '<"Ich kann"-Text aus checks.json, ohne "Ich kann">'
  training_url: /lernbereiche/<gebiet>/<lernbereich>/training.html#check-<Nummer>
  abschluss: '<p>Was im Training anders/gleich ist …</p>'
  karten:
    - phase: orientierung | vormachen | mitmachen
      titel: '…'
      text: '<p>Einleitung (HTML + LaTeX)</p>'
      visual: { … }        # optional
      schritte: [ … ]
---

<div class="page-shell w-wide">
  <section id="check-warmup-root" class="cw-root">
    <p class="module-status">Das Warm-Up wird geladen …</p>
  </section>
</div>

<script type="application/json" id="check-warmup-data">{{ page.warmup | jsonify }}</script>
```

### Schritttypen (`schritte[].typ`)

Gemeinsame Felder aller Schritte:

| Feld | Bedeutung |
|---|---|
| `frage` | Kopfzeile des Schritts (HTML und LaTeX) |
| `hinweis` | Hinweis bei falscher Antwort |
| `danach` | Text, der nach Erledigung erscheint, z. B. die vorgeführte Rechnung oder eine Bestätigung |
| `zeige` | Ändert nach Erledigung das Bild der Karte (siehe Abschnitt „Bilder“) |

| Typ | Zusätzliche Felder | Verhalten |
|---|---|---|
| `text` | `text` | Ist sofort erledigt. Für kurze Brücken. |
| `aufdecken` | `knopf`, `text` | Ein Knopf deckt den Inhalt auf, z. B. einen vorgemachten Rechenschritt. |
| `auswahl` | `optionen[]`, `korrekt` (Index ab 0) | Eine falsche Antwort wird gesperrt und `hinweis` erscheint. Erledigt, sobald die richtige Antwort gewählt ist. |
| `eingabe` | `felder[]`, `layout: zeile` (optional) | Zahlen eingeben und prüfen. Nach dem ersten Fehlversuch erscheint `hinweis`, ab dem zweiten zusätzlich „Lösung zeigen“. Komma und Punkt werden akzeptiert. |
| `zuordnen` | `paare[] {links, rechts}`, `titel_links`, `titel_rechts`, `hilfe` | Erst links, dann rechts tippen (kein Drag & Drop, damit es auf dem Handy funktioniert). Die rechte Spalte wird gemischt. Auf dem Handy stehen die Spalten untereinander. |
| `markieren` | `korrekt[]` (Zeilenindizes), `bereich` (`A` oder `Ay`), `hilfe` | Zeilen in einer Matrix antippen. Braucht `visual.typ: matrix`. Nach zwei Fehlversuchen wird die Lösung markiert. |

Felder einer Eingabe (`felder[]`):

| Feld | Bedeutung |
|---|---|
| `label` | steht vor dem Eingabefeld |
| `einheit` | steht nach dem Eingabefeld |
| `loesung` | erwartete Zahl |
| `toleranz` | erlaubte Abweichung, Standard `0.0001` |
| `zeige` | Bildänderung, sobald dieses Feld richtig ist |
| `aria` | Bezeichnung für Screenreader |

Mit `layout: zeile` stehen die Felder nebeneinander, z. B. als Gleichung `[16] a + [4] b + [1] c = 21` mit `einheit: '$a\;+$'` usw. Hat ein Feld eines Schritts eine negative Lösung, bekommen alle Felder dieses Schritts die normale Tastatur, weil Ziffernblöcke auf iOS kein Minuszeichen haben.

### Bilder (`visual`) und ihre Änderungen (`zeige`)

| `typ` | Felder | Mögliche Änderungen über `zeige` |
|---|---|---|
| `graph` | `funktionen[] {term, name, xmin, xmax}`, `xMin`, `xMax`, `yMin`, `yMax`, `xAchse`, `yAchse`, `punkte[] {id, x, y, label, ax, ay, hilfslinie, sichtbar}` | `{ punkte: [id, …] }` blendet Punkte samt Beschriftung ein |
| `baum` | `pa`, `pba`, `pbna`, `gegeben[]` (Felder 1–10), `modus` (`slots`/`numeric`), `dezimal`, `dezimal_blatt` | `{ slots: [n, …] }` ersetzt die Platzhalter ① … ⑩ durch Werte |
| `matrix` | `name`, `trenn` (Spalte des senkrechten Strichs), `zeilen[][]` | `{ zeilen: [], spalten: [], bereich: A\|Ay }` hebt Zeilen oder Spalten hervor |
| `liste` (Steckbrief) | `titel`, `eintraege[] {id, text, gleichung, erledigt}` | `{ eintraege: [id, …] }` hakt Einträge ab und blendet die Gleichung ein |

Graph-Terme werden mit math.js ausgewertet, also z. B. `0.5x^3-6x^2+30x+48` mit Dezimalpunkt.


## Workflow: neues Warm-Up erstellen

1. **Quellen lesen**
   - `_data/checks.json`: `Ich kann`, `Schlagwort`, `Nummer`, `Sammlung`, `Tipps`
   - Musterbeispiel `lernbereiche/<gebiet>/<lb>/beispiele/<NN>-<sammlung>.md`
   - passender Abschnitt im `skript.md`, für Bezeichnungen und Notation
2. **Aufgabensammlung auswerten** (`aufgaben/exports/json/<gebiet>/<lb>/<sammlung>.json`): Welche Teilfragen und Informationstypen kommen wie oft vor? Am besten zählen, z. B. per PowerShell oder Python über alle `einleitung`- und `fragen`-Texte. Häufige Typen, die im Musterbeispiel fehlen, bekommen eine eigene Vormachen-Karte.
3. **Kern des Checks bestimmen:** Was ist die eigentliche Hürde, und welche Lösungsmuster gibt es? Beispiele: „Information → Gleichung“, „Rang = Zahl der Zeilen, die nicht nur aus Nullen bestehen“, „Unabhängigkeit → gleiche Äste“.
4. **Ablauf skizzieren:** Orientierung (Aha-Moment), Vormachen mit dem Musterbeispiel, Mitmachen mit **neuen Zahlen** und abnehmender Hilfe:
   1. Ansatz vorgegeben, nur das Ergebnis eintragen
   2. Ansatz auswählen, dann rechnen
   3. einzelne Teilschritte ohne Vorgabe
   Das Fading richtet sich nach dem Rechenmuster, nicht nach der Reihenfolge der Teilaufgaben. Es endet, bevor eine komplette Trainingsaufgabe ohne Hilfe entsteht.
5. **Passendes Bild wählen:** Graph, Baum, Matrix, Steckbrief oder keins. Es soll sich mit den Antworten der Lernenden füllen (`zeige`).
6. **Zahlen konstruieren und nachrechnen.** Glatte Werte wählen und alles per Skript prüfen. Fachliche Nebenbedingungen beachten, z. B. ob eine Kostenfunktion ertragsgesetzlich ist ($a>0$, $b<0$, $d>0$, $b^2\le 3ac$) oder ob Betriebsminimum < Betriebsoptimum gilt. Zuordnungsaufgaben müssen in sich stimmig sein.
7. **Front Matter schreiben.** Am besten eine bestehende Seite kopieren. `titel` ist das `Schlagwort` aus `checks.json`. Einen Eintrag in [index.md](./index.md) ergänzen.
8. **Testen** (siehe Checkliste).

### Fallstricke beim Schreiben

- **Formeln auf dem Handy (Pflicht):** Jede Formel muss bei ~360 px Breite in die Karte passen.
  - **Lange Formeln als abgesetzte Formel** (`$$…$$`), nie inline. Das gilt z. B. für Funktionen dritten Grades, Gleichungen mit Brüchen und Rechnungen mit mehreren Gliedern. Inline-Formeln können nicht umbrechen und nicht scrollen und drücken dann die Karte auseinander. Inline nur für kurze Ausdrücke wie $K'$, $k_v(6)$ oder $x=4$.
  - **Abgesetzte Formeln schmal halten:** mehrere Funktionen untereinander in `align*` statt nebeneinander mit `\quad`. Rechnung und Ergebnis auf eigene Zeilen statt `…=48\;\Rightarrow\;d=48`. Keine `\text{…}`-Erklärungen hinter den Zeilen, die gehören in den Fließtext.
  - **Umformungsangaben mit `\quad|`** schreiben, nicht mit `&&|`: `&&` erzeugt in `align*` eine sehr breite Lücke. Bei langen Umformungen (z. B. `|-0{,}5x^2+6x-30`) die Angabe ganz weglassen und im Text erklären.
  - Ist eine abgesetzte Formel trotzdem zu breit, scrollt sie in ihrem eigenen Kasten (CSS-Absicherung). Das soll aber die Ausnahme bleiben.
- **YAML in einfachen Anführungszeichen:** Ein Apostroph wird verdoppelt (`'K''(1)=19{,}5'`). Backslashes bleiben einfach (`'\frac{d}{x}'`). Das ist deutlich angenehmer als JSON. Für höhere Ableitungen daher `K^{\prime\prime}` statt `K''''` schreiben, das ist besser lesbar.
- **Dezimalkomma in LaTeX:** `0{,}5`. In `loesung:` dagegen mit Punkt: `0.5`.
- **`<` in HTML-Texten** als `&lt;` schreiben, z. B. `$2&lt;4$`.
- **Lange Kartentitel** werden im Kartenkopf abgeschnitten (wie in den anderen Modulen). Das `Schlagwort` sollte daher kurz sein.
- **Cache:** Nach Änderungen an JS oder CSS die `?v=`-Parameter in **allen** Prototyp-Seiten hochzählen, sonst lädt der Browser die alte Version.
- **Jekyll braucht nach dem Speichern einige Sekunden**, bevor die neue Version ausgeliefert wird.

### Test-Checkliste

- [ ] Alle Karten lassen sich bis „Weiter zum Training“ durchspielen, ohne JavaScript-Fehler.
- [ ] Jede Auswahl einmal falsch und dann richtig, jede Eingabe einmal falsch, mit Dezimalkomma und negativen Zahlen.
- [ ] Bildänderungen (`zeige`) passieren an der richtigen Stelle.
- [ ] Keine MathJax-Fehler (`mjx-merror`), keine Formel überläuft die Karte.
- [ ] Desktop (≥ 960 px, Bild neben den Schritten) und Handy (360–390 px): kein seitliches Scrollen, nichts ragt über den Kartenrand, Navigation bleibt an ihrem Platz, Zuordnen steht untereinander. Möglichst keine abgesetzte Formel scrollt im eigenen Kasten.
- [ ] Hell- und Dunkelmodus.
- [ ] Fachlich: alle Zahlen und Gleichungen nachgerechnet, Begriffe wie im Skript.

**Automatisierter Durchlauf:** Ein Playwright-Skript liest die Daten aus `#check-warmup-data` und löst jeden Schritt anhand von `korrekt`, `loesung` bzw. `paare`. **Hinweis:** In einem verborgenen Browser-Tab zeichnet der Browser keine neuen Bilder (kein `requestAnimationFrame`). Dann hängen normale Playwright-Klicks, und Bildschirmfotos zeigen veraltete Zustände. Dort Klicks mit `locator.dispatchEvent('click')` auslösen und Bildschirmfotos nur im sichtbaren Tab machen.


## Bekannte Grenzen und offene Punkte

- **Handy:** Bei schmalem Bildschirm steht das Bild über den Schritten. Wer unten etwas einträgt, sieht die Änderung oben nicht sofort.
- **Daten im Front Matter** sind nur für den Prototyp gedacht. Nächster Schritt ist die **Verzahnung ins Projekt, weiterhin ohne Verlinkung**:
  - eine YAML-Datei pro Check, z. B. `_data/warmup/<lernbereich>/<NN>-<sammlung>.yml` (der Ordner `_data/warmup/` ist durch das Entfernen des alten Warm-Ups frei)
  - `titel`, `kompetenz`, `nummer` und `training_url` aus `checks.json` ableiten statt doppelt pflegen
  - eine Modulseite pro Lernbereich: `lernbereiche/<gebiet>/<lb>/warmup.md` mit `module_key: warmup`, URL `…/<lb>/warmup.html#check-<NN>`. Die URL ist frei, weil die alten `warmup.md`-Seiten entfernt sind. Seite mit `noindex`, nicht in der Navigation.
  - Skript und CSS umbenennen: `assets/js/modules/warmup.js` und `assets/css/warmup.css`, Einbindung über den Modulzweig in `assets/js/app.js`. Der alte Zweig ist entfernt.
  - Auslieferung als JSON nach dem Muster von `checks.json` (`{{ site.data… | jsonify }}`)
  - ein Prüfskript für alle Datendateien: unbekannter `typ`, `korrekt` außerhalb der Optionen, fehlende `loesung`, `zeige` verweist auf eine nicht vorhandene `id`, `check_id` fehlt in `checks.json`
  - die fünf Prototypen übernehmen, danach `prototypen/check-warmup/` und diese README an den neuen Ort verschieben bzw. entfernen
- **Noch nicht verdrahtet (bewusst):** Feed, Speicherung des Fortschritts, Verlinkung aus Skript, Kompetenzliste, Training oder Navigation.
- **Wachstum:** Neue Interaktionen als allgemeine Schritt- oder Bildtypen im gemeinsamen Skript ergänzen, nie Code für einen einzelnen Check. Wird das Skript zu groß, aufteilen in `steps/` und `visuals/`.
