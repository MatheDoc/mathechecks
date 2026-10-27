# Warm-Up pro Check

Kurzer, interaktiver Einstieg in **einen** Check, so kurz wie möglich, so lang wie nötig. Es übernimmt die Rolle eines Erklärvideos:

- **Idee:** Erst wird der Kern zum Durchklicken erklärt.
- **Zuschauen:** Dann wird ein Beispiel vorgerechnet.
- **Mitmachen:** Danach rechnen die Lernenden mit abnehmender Hilfe mit und wechseln ins Training.

**Status:** Das Warm-Up ist nicht verlinkt (kein Feed, kein Reiter in `_includes/module/nav.html`, `noindex`, nicht in der Sitemap, kein Fortschritt-Speichern) und nur über die URL erreichbar: `…/<lb>/warmup.html#check-<Nummer>`. Die Übersicht `/warmup.html` (`warmup.md` im Wurzelverzeichnis) wird automatisch erzeugt.

**Gute Vorlagen:**
- `analysis/ertragsgesetzliche-kostenfunktionen/05-…`: Idee am Graphen, zwei Lösungswege
- `analysis/differentialrechnung-ganzrationaler-funktionen/05-…`: $f$ und $f'$ gemeinsam im Bild, Flächen
- `finanzmathematik/zinseszinsrechnung/01-…`: Spickzettel-Liste, Zuordnen als Brücke


## Leitlinien

| Phase (`phase`) | Anzeige | Inhalt | Umfang |
|---|---|---|---|
| `orientierung` | Idee | Worum geht es, Kernidee, nötige Begriffe/Formeln; am Ende ein bis drei Merksätze | 1–2 Karten, 2–4 Schritte |
| `vormachen` | Zuschauen | Musterbeispiel aus `beispiele/<NN>-<sammlung>.md`, Schritt für Schritt mit kleinen Begleitfragen | 1–3 Karten |
| `mitmachen` | Mitmachen | Neue Zahlen, Hilfe nimmt ab bis kurz vor die Trainingsaufgabe | 1–3 Karten, meist Zuordnung + eine Rechenkarte |

Insgesamt 3–8 Karten, bei kurzen Checks ist auch 1 Karte pro Phase angebracht.Richtwert höchstens etwa 15 Schritte. Checks mit vielen Kennzahlen oder Lösungswegen dürfen begründet darüber liegen.

1. **Idee: erst erklären, dann fragen.**
   - Jede Idee-Karte beginnt mit einer Erklärung (`aufdecken`/`text`).
   - Ein Gedanke pro Klick; das Bild baut sich über `zeige` mit auf. Es darf mehr zeigen als im Training, z. B. $f$ zusätzlich zu $f'$.
   - Höchstens ein bis zwei **Beobachtungsfragen**. Erlaubt ist eine Frage nur, wenn man sie ohne Vorwissen zum Check allein aus Text und Bild beantworten kann und dafür trotzdem kurz hinschauen muss. Beispiel: „Schau dir $K'$ an. Was fällt dir auf?“
   - Nicht erlaubt sind Fragen, deren Antwort gerade dasteht, und Fragen, deren Antwort erst später erklärt wird.
   - Die Leitidee ist der fachliche Kern (z. B. „Merkmal des Graphen → Gleichung“), kein Rechentrick. Rechentipps (z. B. $e^{-ct}\neq 0$, also genügt die Klammer) gehören an die passende Stelle beim Zuschauen.
2. **Jeder Klick bringt einen neuen Gedanken oder eine echte Entscheidung.**
   - Aufdecken-Schritte ohne Denkpause dazwischen zusammenfassen.
   - Keine Plausibilitäts- oder Pflichtfragen ohne echte Hürde.
   - Dasselbe Rechenmuster nicht öfter als nötig üben.
3. **Fading nach Rechenmuster, nicht nach Teilaufgaben.**
   - Beim Mitmachen nimmt die Hilfe in drei Stufen ab:
     1. Der Ansatz ist vorgegeben.
     2. Der Ansatz wird ausgewählt oder zugeordnet.
     3. Ein Teilschritt wird ohne Vorgabe gerechnet.
   - Unabhängige Teilaufgaben mit gleichem Muster z.B. einmal mit und einmal ohne Vorgabe.
   - Eine Zuordnung „Situation → Ansatz“ ist ein guter Start ins Mitmachen.
4. **Kein Doppel zum Training.**
   - Es gibt keine Karte, die einer Trainingsaufgabe entspricht. Das Fading endet kurz davor.
   - Mitmachen lieber knapp halten: Was nur noch ein weiteres Ablesen oder Einsetzen wie im Training wäre, fällt weg. Eine Rechenkarte übt vor allem die wichtigste Falle bzw. den neuen Schritt.
   - Bis zum Ende kommt möglichst jedes Eingabeformat des Trainings einmal vor.
   - Der `abschluss` ist **kurz** (ein bis drei Sätze): Prägnant das Wichtigste zusammengefasst (keine Erläuterungen zu Rundnungen o.Ä.). 
5. **Kern vor Vollständigkeit.**
   - Der häufigste Aufgabentyp und die wichtigste Falle bekommen eigene Karten. Das gilt auch für häufige Informationstypen der Aufgabensammlung, die im Musterbeispiel fehlen.
   - Seltene Sonderfälle höchstens mit einem Halbsatz im `abschluss`.
6. **Gleichwertige Lösungswege möglichst beide zeigen** (z. B. Betriebsminimum als Extremstelle von $k_v$ oder als Schnittstelle mit $K'$). Beim Mitmachen wird jeder Weg einmal geübt.
7. **Bezeichnungen wie im Skript.**
8. **Für welche Checks?** Ein Warm-Up lohnt sich bei einer neuen Idee, einem neuen Verfahren oder einer typischen Fehlvorstellung, kaum bei Routine-Varianten.


## Technik

| Datei | Rolle |
|---|---|
| `_data/warmup/<gebiet>/<lernbereich>/<NN>-<sammlung>.yml` | Eine Datendatei pro Check; Namen wie in `checks.json` (`Gebiet`, `Lernbereich`, `Nummer`, `Sammlung`) |
| `lernbereiche/<gebiet>/<lb>/warmup.md` | Modulseite pro Lernbereich (`module_key: warmup`, `noindex: true`, `page_css: /assets/css/warmup.css?v=…`); für einen neuen Lernbereich eine vorhandene kopieren |
| `_includes/module/warmup-content.html` | Check-Navigation und eingebettete Daten (`#warmup-data`) |
| `assets/js/modules/warmup.js` | Gemeinsamer Abspieler für alle Warm-Ups; neue Interaktionen nur als allgemeine Schritt- oder Bildtypen (auch im Prüfskript eintragen) |
| `assets/css/warmup.css` | Styling (Präfix `cw-`) |
| `_data/warmup/validate_warmup.py` | Prüfskript |

- **Metadaten:** `titel`, `kompetenz`, `nummer` und `training_url` ergänzt der Abspieler aus `checks.json` über `check_id`. Sie gehören nicht in die Datendatei; das Prüfskript lehnt sie ab.
- **Ablauf:** Die Schritte einer Karte erscheinen nacheinander. Der nächste erscheint erst, wenn der vorige gelöst oder aufgedeckt ist. „Weiter“ wird aktiv, wenn alle Schritte der Karte erledigt sind.


## Datenformat

```yaml
check_id: <gebiet>__<lernbereich>__<NN>
abschluss: '<p>Hinweise fürs Training …</p>'
karten:
  - phase: orientierung | vormachen | mitmachen
    titel: '…'
    text: '<p>Einleitung (HTML + LaTeX)</p>'
    visual: { … }        # optional
    schritte: [ … ]
```

### Schritte

Gemeinsame Felder: `frage` (Kopfzeile), `hinweis` (bei falscher Antwort), `danach` (erscheint nach Erledigung), `zeige` (Bildänderung nach Erledigung).

| `typ` | Felder | Verhalten |
|---|---|---|
| `text` | `text` | sofort erledigt |
| `aufdecken` | `knopf`, `text` | Knopf deckt `text` auf |
| `auswahl` | `optionen[]`, `korrekt` (Index ab 0), `mischen` (Standard `true`) | falsche Antwort wird gesperrt, `hinweis` erscheint |
| `eingabe` | `felder[] {label, einheit, loesung, toleranz (Standard 0.0001), zeige, aria}`, `layout: zeile` | nach dem 1. Fehlversuch `hinweis`, ab dem 2. „Lösung zeigen“; Komma und Punkt erlaubt |
| `zuordnen` | `paare[] {links, rechts}`, `titel_links`, `titel_rechts`, `hilfe` | erst links, dann rechts tippen; rechte Spalte gemischt |
| `markieren` | `korrekt[]` (Zeilen), `bereich` (`A`/`Ay`), `hilfe` | Zeilen einer Matrix antippen; braucht `visual.typ: matrix` |

`layout: zeile` setzt die Felder nebeneinander, z. B. als Gleichung (`einheit: '$a\;+$'`).

### Bilder (`visual`) und `zeige`

| `typ` | Felder | `zeige` |
|---|---|---|
| `graph` | `funktionen[] {term, name, xmin, xmax, color}`, `xMin`, `xMax`, `yMin`, `yMax`, `xSchritt`, `ySchritt` (Abstand der Achsenbeschriftung; `1`, wenn ganzzahlige Stellen abgelesen werden), `xAchse`, `yAchse`, `punkte[] {id, x, y, label, ax, ay, hilfslinie, sichtbar}`, `flaechen[] {id, term, von, bis, farbe, sichtbar}` (zwischen `term` und $x$-Achse) | `punkte: [id…]` blendet ein; `flaechen: [id…]` **ersetzt** die sichtbaren Flächen (`[]` = keine) |
| `baum` | `pa`, `pba`, `pbna`, `gegeben[]` (Felder 1–10), `modus` (`slots`/`numeric`), `dezimal`, `dezimal_blatt` | `slots: [n…]` füllt Platzhalter |
| `histogramm` | `n`, `p`, `kumuliert`, `bereiche[]` (je `[a, b]`), `gegen[]` (orange), `werte[]`, `kMin`, `kMax` | `bereiche`/`gegen` **ersetzen**, `werte: [k…]` beschriftet Balken |
| `zahlenstrahl` | `n`, `p` (dann automatisch $Bcd$-Zeile), `bereiche[]`, `marke` | `bereiche` ersetzt, `marke` setzt (`null` entfernt), `p` ändert |
| `matrix` | `name`, `trenn`, `zeilen[][]` | `zeilen`, `spalten`, `bereich` (`A`/`Ay`) heben hervor |
| `liste` | `titel`, `eintraege[] {id, text, gleichung, erledigt}` | `eintraege: [id…]` hakt ab, zeigt Gleichung |

Graph-Terme werden mit math.js ausgewertet (Dezimalpunkt, z. B. `0.5x^3-6x^2`).


## Ablauf beim Erstellen

1. **Quellen lesen:**
   - `checks.json` (`Ich kann`, `Tipps`)
   - das Musterbeispiel in `beispiele/`
   - den Skript-Abschnitt zum Check
   - die Aufgabensammlung `aufgaben/exports/json/<gebiet>/<lb>/<sammlung>.json`: Welche Fragetypen kommen wie oft vor? Am besten per Skript zählen.
2. **Kern** in ein bis drei Merksätzen festlegen, dann die Karten nach den Leitlinien skizzieren.
3. **Zahlen** glatt wählen und alles per Skript nachrechnen. Fachliche Nebenbedingungen beachten, z. B. für eine ertragsgesetzliche Kostenfunktion $a>0$, $b<0$, $d>0$ und $b^2\le 3ac$.
4. **Datei schreiben**, dann `python _data/warmup/validate_warmup.py` ausführen: keine Fehler, Warnungen prüfen.
5. **Testen** (Checkliste unten).

### Fallstricke

- **Handy (~360 px):**
  - Lange Formeln abgesetzt (`$$…$$`), inline nur kurze Ausdrücke.
  - Abgesetzte Formeln schmal halten: `align*` untereinander, keine `\text{…}`-Erklärungen.
  - Umformungsangaben mit `\quad|` statt `&&|`.
  - Antwortoptionen und Zuordnungen können nicht scrollen: Lange Gleichungen dort nach dem `=` mit `<br>` umbrechen (`'$600=$<br>$2\,600\cdot 1{,}04^n$'`).
- **YAML in einfachen Anführungszeichen:** Apostroph verdoppeln (`'K''(1)'`), für zweite Ableitungen `K^{\prime\prime}` schreiben.
- **Dezimalzahlen:** LaTeX `0{,}5`, aber `loesung: 0.5`. `<` in HTML-Texten als `&lt;` schreiben.
- **Negative Lösung in einem Feld:** Alle Felder des Schritts bekommen dann die normale Tastatur (auf iOS haben Ziffernblöcke kein Minus).
- **Cache:**
  - nach Änderungen an `warmup.js`: den `?v=` des Imports in `assets/js/app.js` **und** den von `app.js` in `_layouts/module.html` erhöhen
  - nach Änderungen an `warmup.css`: `page_css` in allen `warmup.md` erhöhen

### Test-Checkliste

- [ ] Prüfskript ohne Fehler, Warnungen geprüft
- [ ] Alles bis „Weiter zum Training“ durchspielbar, keine JS-Fehler; „Zum Training“ und Check-Wechsel per `#check-<Nummer>` funktionieren
- [ ] Jede Auswahl einmal falsch, jede Eingabe einmal falsch (Dezimalkomma, negative Zahlen); `zeige` an der richtigen Stelle
- [ ] Keine MathJax-Fehler; Desktop (≥ 960 px) und Handy (360–390 px) ohne seitliches Scrollen; Hell- und Dunkelmodus
- [ ] Fachlich nachgerechnet, Begriffe wie im Skript

**Playwright:** In verborgenen Tabs läuft kein `requestAnimationFrame`. Dann hängen Klicks, und Bildschirmfotos sind veraltet. Klicks dort mit `locator.dispatchEvent('click')` auslösen, Bildschirmfotos nur im sichtbaren Tab.


## Offene Punkte

- **Handy:** Das Bild steht über den Schritten; Änderungen sieht man beim Eintragen nicht sofort.
- **Freischaltung** (Feed, Fortschritt, Verlinkung) steht aus. Dann auch den Hinweis „Prototyp“ in `buildCardHeader` (`warmup.js`) entfernen.
