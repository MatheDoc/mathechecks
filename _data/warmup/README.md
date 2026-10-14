# Warm-Up pro Check

Geführter, interaktiver Einstieg in **einen einzelnen Check**. Lernende sehen ein vorgerechnetes Beispiel, rechnen dann mit schrittweise weniger Hilfe mit und wechseln anschließend ins Training.

> **Status:** ins Projekt verzahnt (eigene Datendateien, Modulseite pro Lernbereich, Modulzweig in `app.js`, Prüfskript), aber **weiterhin nicht verlinkt**: nicht im Feed, kein Reiter in der Modulnavigation, kein Link aus Skript, Kompetenzliste oder Training, `noindex`, nicht in der Sitemap, kein Fortschritt-Speichern. Die Seiten sind lokal und nach einem Deploy nur über ihre URL erreichbar.

**Begriffe:** Die Aktivität heißt **„Warm-Up“**, technisch `module_key: warmup` (Kartenkopf „WARM-UP NN | Schlagwort“). Das frühere Warm-Up pro Lernbereich (Neugier-Karten) ist vollständig entfernt; Name, Modulfarbe und `module_key` gehören jetzt dem Warm-Up pro Check.

## Vorhandene Warm-Ups

| Datendatei (`_data/warmup/…`) | Check | URL | Erprobter Schwerpunkt |
|---|---|---|---|
| `analysis/marktgleichgewicht-grundlagen/02-kennzahlen-rechnerisch-linear.yml` | `analysis__marktgleichgewicht-grundlagen__02` | `/lernbereiche/analysis/marktgleichgewicht-grundlagen/warmup.html#check-2` | Mehrere unabhängige Teilaufgaben; Fading nach Rechenmuster; Graph wächst mit |
| `analysis/ertragsgesetzliche-kostenfunktionen/05-kennzahlen-rechnerisch-k3.yml` | `analysis__ertragsgesetzliche-kostenfunktionen__05` | `/lernbereiche/analysis/ertragsgesetzliche-kostenfunktionen/warmup.html#check-5` | Zwei gleichwertige Lösungswege (Extremstelle oder Schnittstelle mit $K'$); Erkenntnis am Graphen, dann beide Wege vorgemacht und geübt |
| `analysis/ertragsgesetzliche-kostenfunktionen/06-steckbrief-kennzahlen-k3.yml` | `analysis__ertragsgesetzliche-kostenfunktionen__06` | `/lernbereiche/analysis/ertragsgesetzliche-kostenfunktionen/warmup.html#check-6` | Informationen in Gleichungen übersetzen; Steckbrief wird abgehakt; Gleichungszeile |
| `stochastik/bedingte-wahrscheinlichkeiten/02-baumdiagramm-erstellen-mit-unabh.yml` | `stochastik__bedingte-wahrscheinlichkeiten__02` | `/lernbereiche/stochastik/bedingte-wahrscheinlichkeiten/warmup.html#check-2` | Ein Lösungsweg mit Schlüsselschritt; Baum füllt sich |
| `stochastik/binomialverteilung/05-bereichswahrscheinlichkeiten-berechnung.yml` | `stochastik__binomialverteilung__05` | `/lernbereiche/stochastik/binomialverteilung/warmup.html#check-5` | Text → Bereich auf dem Zahlenstrahl → $Bcd$-Eingabe (nur Taschenrechner-Weg); Sonderfälle Prozent, „oder“, anderes $p$ beim Zählen der Nieten, bestimmte Versuche |
| `stochastik/binomialverteilung/06-histogramme-einzeln.yml` | `stochastik__binomialverteilung__06` | `/lernbereiche/stochastik/binomialverteilung/warmup.html#check-6` | Balkenhöhe ablesen, Balken addieren, Gegenereignis; abgelesene Werte erscheinen über den Balken |
| `finanzmathematik/zinseszinsrechnung/01-zinseszinsformel-umformen.yml` | `finanzmathematik__zinseszinsrechnung__01` | `/lernbereiche/finanzmathematik/zinseszinsrechnung/warmup.html#check-1` | Umformen nach der Lage der Unbekannten (Faktor → teilen, Basis → Wurzel, Exponent → Logarithmus); Spickzettel als Liste, die sich füllt und am Ende wegfällt |
| `finanzmathematik/zinseszinsrechnung/02-zinseszins-sachaufgaben.yml` | `finanzmathematik__zinseszinsrechnung__02` | `/lernbereiche/finanzmathematik/zinseszinsrechnung/warmup.html#check-2` | Sachzusammenhang: früherer Betrag $K_0$, späterer $K_n$; Fragesatz bestimmt die gesuchte Größe; Fallen „heute“, „verfügen“, „Zahlung leisten“, „benötigt“; Gegeben/Gesucht-Liste füllt sich |
| `lineare-algebra/lineare-gleichungssysteme/05-lgs-rangkriterium.yml` | `lineare-algebra__lineare-gleichungssysteme__05` | `/lernbereiche/lineare-algebra/lineare-gleichungssysteme/warmup.html#check-5` | Begriff und Verfahren; Zeilen in der Matrix antippen |

Übersicht aller Warm-Ups (isoliert, `noindex`, nirgends verlinkt, automatisch aus den Daten erzeugt): `warmup.md` im Repo-Wurzelverzeichnis → `/warmup.html`


## Entscheidungen (mit Begründung)

Festgehalten, damit spätere Arbeit nicht hinter diese Punkte zurückfällt.

| Entscheidung | Begründung |
|---|---|
| **Warm-Up pro Check, vor dem Training** | Wer neu in einem Thema ist, lernt mehr aus vorgerechneten Beispielen als aus selbst gelösten Aufgaben. Bisher startete die Check-Kette direkt mit dem Training, also mit dem selbstständigen Lösen. |
| **Das alte Warm-Up pro Lernbereich ist entfernt** | Neugier-Karten pro Lernbereich wurden nicht mehr benötigt. Name, Modulfarbe (`--mt-warmup`, `check-card--warmup`) und `module_key: warmup` gehen an das neue Warm-Up. |
| **Drei Phasen: Worum geht's? → Zuschauen → Mitmachen** | Eine vierte Phase „Jetzt du“ mit echter Trainingsaufgabe wurde gebaut und wieder entfernt. Sie war ein Doppel zum Training, das direkt danach kommt. |
| **Keine Karte, die einer Trainingsaufgabe entspricht** | Aus demselben Grund. Das Fading endet kurz davor, Hinweise fürs Training stehen im `abschluss`. |
| **Phasen statt fester Kartenzahl** | Checks sind unterschiedlich groß. Insgesamt 3–8 Karten. |
| **Fading nach Rechenmuster, nicht nach Teilaufgaben** | Teilaufgaben sind oft unabhängig voneinander. Spätere Teilaufgabe einfach wegzulassen, wäre kein Fading. |
| **Scheinverständnis wird in Kauf genommen** | Der Einstieg soll leicht sein. Leichte Kontrollfragen (Auswahl, Zahl, Zuordnen) sorgen nur dafür, dass man nicht bloß durchklickt. |
| **„Zum Training →“ immer sichtbar** | Wer den Stoff schon kann, überspringt das Warm-Up. |
| **Gleichwertige Lösungswege beide zeigen** | z. B. Betriebsminimum als Extremstelle von $k_v$ oder als Schnittstelle von $K'$ und $k_v$. |
| **Kartendesign wie bei den anderen Modulen** | `check-card` mit Standard-Kartenkopf, feste Kartenhöhe, Scrollen nur im Kartenkörper, „Zurück/Weiter“ an festem Platz unter der Karte. Farbe: Warm-Up-Farbe (Terrakotta). |
| **Kein Phasen-Label vor dem Kartentitel** | Die Phasenleiste zeigt die Phase bereits an. Auf dem Handy war das Label zu viel. |
| **Ein gemeinsames Skript, Inhalte als Daten** | Wie beim Training: Ein Abspieler für alle Checks. Neue Interaktionen nur als allgemeine Schritt- oder Bildtypen. |
| **Eine Datendatei pro Check, eine Modulseite pro Lernbereich** | Daten unter `_data/warmup/<gebiet>/<lernbereich>/<NN>-<sammlung>.yml` (Namensschema wie bei `beispiele/`). Die Modulseite `warmup.md` zeigt alle Warm-Ups des Lernbereichs, Auswahl per `#check-<Nummer>` wie im Training. |
| **Metadaten nicht doppelt pflegen** | `titel` (`Schlagwort`), `kompetenz` (`Ich kann`), `nummer` (`Nummer`) und `training_url` ergänzt das Skript zur Laufzeit aus `checks.json` über `check_id`. Das Prüfskript lehnt diese Felder in den Datendateien ab. |
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
| `_data/warmup/<gebiet>/<lernbereich>/<NN>-<sammlung>.yml` | **Eine Datendatei pro Check.** `<gebiet>` = `Gebiet`, `<lernbereich>` = `Lernbereich`, `<NN>` = zweistellige `Nummer`, `<sammlung>` = `Sammlung` aus `checks.json` (wie bei `beispiele/`). Enthält nur `check_id`, `abschluss` und `karten`. |
| `lernbereiche/<gebiet>/<lb>/warmup.md` | **Eine Modulseite pro Lernbereich** mit mindestens einem Warm-Up: `layout: module`, `module_key: warmup`, `noindex: true`, `page_css: /assets/css/warmup.css?v=…`. Inhalt nur `{% include module/warmup-content.html %}`. |
| `_includes/module/warmup-content.html` | Check-Navigation (`#warmup-jump-nav`), Wurzel `#warmup-root` und die eingebetteten Daten: `<script type="application/json" id="warmup-data">{{ site.data.warmup[page.gebiet][page.lernbereich] | jsonify }}</script>` (Muster wie `checks.json`, aber direkt in der Seite, nur der eigene Lernbereich). |
| `assets/js/modules/warmup.js` | **Ein** gemeinsames Skript, das das Datenformat für alle Checks abspielt (`initWarmupModule`). Es ergänzt die Metadaten aus `checks.json` und nutzt die vorhandenen Bausteine `data/checks-repo.js`, `visuals/graph.js`, `visuals/baumdiagramm.js`, `visuals/histogramm.js`, `visuals/plotly-defaults.js`, `ui/check-meta.js` und `ui/check-jump-nav.js`. |
| `assets/js/app.js` | Modulzweig `context.moduleKey === "warmup"` ruft `initWarmupModule` auf, wie bei den anderen Modulen. |
| `assets/css/warmup.css` | Eigenes Stylesheet (Präfix `cw-`). Es wird über `page_css` nur auf den Warm-Up-Seiten und der Übersicht geladen. |
| `warmup.md` (Wurzel) | Isolierte Übersicht `/warmup.html`, aus `_data/warmup`, `_data/lernbereiche.yml` und `_data/checks.json` erzeugt. `noindex`, nirgends verlinkt. |
| `_data/warmup/validate_warmup.py` | Prüfskript für alle Datendateien (siehe unten). |

**Abgeleitete Felder (nicht in die Datendatei schreiben):** Das Skript sucht den Check über `check_id` in `checks.json` und setzt `nummer` = `Nummer`, `titel` = `Schlagwort`, `kompetenz` = `Ich kann` (angezeigt als „Ich kann …“) und `training_url` = `training.html#check-<Nummer>` (relativ zur Modulseite, also im selben Lernbereich).

**Auswahl des Checks:** Die Check-Navigation über der Karte listet nur die Checks des Lernbereichs, die ein Warm-Up haben. Ausgewählt wird wie im Training über den Anker `#check-<Nummer>` (`#check-5`, auch `#check-05`) oder über `?check_id=…`. Ein Wechsel des Ankers (`hashchange`) lädt das passende Warm-Up neu. Ohne passenden Anker startet das erste Warm-Up des Lernbereichs.

Layout: `layout: module` mit `body_class: page-module` wie die übrigen Module. Die Modulnavigation erscheint, der Warm-Up-Reiter bleibt dort ausgeblendet. Die Karte ist eine echte `check-card check-card--warmup` mit dem Standard-Kartenkopf aus `renderCheckMetaRowMarkup`. Der Hinweis „Prototyp“ im Kartenkopf bleibt, solange das Warm-Up nicht freigeschaltet ist.

**Feste Kartenhöhe:** Die Karte füllt die Bühne zwischen Kopfleiste, Modul-Reitern und Check-Navigation (`--check-stage-height` aus `shared.css`, auch im Vollbild). Nur der Kartenkörper (`.cw-body`) scrollt. Kartenkopf, Phasenleiste und „Zurück/Weiter“ bleiben an ihrem Platz. Ab 960 px stehen Bild und Schritte nebeneinander, und das Bild bleibt beim Scrollen stehen.

**Kartentitel ohne Phasen-Label:** Die aktuelle Phase zeigt allein die Phasenleiste. Vor dem Kartentitel steht kein eigenes Phasen-Label.

**Breitenbegrenzung:** Alle Rasterspalten im Warm-Up sind `minmax(0, 1fr)`. Sonst würde eine breite Formel die ganze Spalte und damit die Karte verbreitern. Abgesetzte Formeln (`mjx-container[display="true"]`) scrollen bei Bedarf in ihrem eigenen Kasten.

**Ablauf im Skript:**
- Die Schritte einer Karte erscheinen nacheinander.
- Ein Schritt gilt als erledigt, wenn er richtig gelöst oder aufgedeckt ist. Erst dann erscheint der nächste.
- „Weiter“ wird aktiv, sobald alle Schritte der Karte erledigt sind.
- Nach der letzten Karte erscheint der Abschlusskasten, und „Weiter zum Training“ wird aktiv.


## Datenformat (`_data/warmup/<gebiet>/<lernbereich>/<NN>-<sammlung>.yml`)

```yaml
# Warm-Up zu Check <NN> „<Schlagwort>“ (<Lernbereich>)
check_id: <gebiet>__<lernbereich>__<NN>
abschluss: '<p>Was im Training anders/gleich ist …</p>'
karten:
  - phase: orientierung | vormachen | mitmachen
    titel: '…'
    text: '<p>Einleitung (HTML + LaTeX)</p>'
    visual: { … }        # optional
    schritte: [ … ]
```

Erlaubt sind oben nur `check_id`, `abschluss` und `karten`. Neue Lernbereiche brauchen zusätzlich die Modulseite `lernbereiche/<gebiet>/<lb>/warmup.md` (eine vorhandene kopieren und `title`, `description`, `lernbereich`, `gebiet`, `permalink` anpassen).

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
| `histogramm` (Binomialverteilung, Einzelwahrscheinlichkeiten) | `n`, `p`, `bereiche[]` (anfangs markiert, je `[a, b]`), `gegen[]` (orange, z. B. fürs Gegenereignis), `werte[]` (anfangs beschriftete Balken), `kMin`, `kMax` (angezeigter Ausschnitt, Standard `0` bis `n`) | `{ bereiche: [[a, b], …], gegen: […] }` **ersetzen** die jeweilige Markierung (`[]` hebt sie auf), `{ werte: [k, …] }` schreibt die Balkenhöhe auf 2 Nachkommastellen über die Balken (bleibt stehen). Antippen zeigt wie im Training den Wert auf 2 Nachkommastellen. Bei schmalem Bild werden die Achsenbeschriftungen kleiner bzw. ausgedünnt und die Balkenwerte senkrecht geschrieben. |
| `zahlenstrahl` (Anzahlen $0$ bis $n$) | `n`, `p` (optional), `bereiche[]`, `marke` (nicht ganzzahlige Grenze, z. B. `2.6`) | `{ bereiche: […] }` ersetzt die markierten Anzahlen, `{ marke: 22.5 }` setzt bzw. `{ marke: null }` entfernt die gestrichelte Grenze, `{ p: 0.2 }` ändert $p$. Ist `p` gesetzt, steht unter dem Strahl automatisch die Eingabe $Bcd(a;b;n;p)$ (bei mehreren Bereichen als Summe). |
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
5. **Passendes Bild wählen:** Graph, Baum, Histogramm, Zahlenstrahl, Matrix, Steckbrief oder keins. Es soll sich mit den Antworten der Lernenden füllen (`zeige`).
6. **Zahlen konstruieren und nachrechnen.** Glatte Werte wählen und alles per Skript prüfen. Fachliche Nebenbedingungen beachten, z. B. ob eine Kostenfunktion ertragsgesetzlich ist ($a>0$, $b<0$, $d>0$, $b^2\le 3ac$) oder ob Betriebsminimum < Betriebsoptimum gilt. Zuordnungsaufgaben müssen in sich stimmig sein.
7. **Datendatei schreiben.** Am besten eine bestehende Datei kopieren und unter `_data/warmup/<gebiet>/<lernbereich>/<NN>-<sammlung>.yml` ablegen. `titel`, `kompetenz`, `nummer` und `training_url` **nicht** eintragen, sie kommen aus `checks.json`. Gibt es im Lernbereich noch kein Warm-Up, die Modulseite `lernbereiche/<gebiet>/<lb>/warmup.md` anlegen (Kopie einer vorhandenen). Die Übersicht `/warmup.html` ergänzt sich von selbst.
8. **Prüfskript ausführen:** `python _data/warmup/validate_warmup.py` (muss ohne Fehler durchlaufen).
9. **Testen** (siehe Checkliste).

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
- **Cache:** Nach Änderungen an `warmup.js` den `?v=`-Parameter des Imports in `assets/js/app.js` und den von `app.js` in `_layouts/module.html` hochzählen; nach Änderungen an `warmup.css` den `page_css`-Parameter in **allen** `warmup.md`-Seiten (und der Übersicht `warmup.md`). Sonst lädt der Browser die alte Version.
- **Jekyll braucht nach dem Speichern einige Sekunden**, bevor die neue Version ausgeliefert wird.

### Test-Checkliste

- [ ] `python _data/warmup/validate_warmup.py` läuft ohne Fehler.
- [ ] Alle Karten lassen sich bis „Weiter zum Training“ durchspielen, ohne JavaScript-Fehler.
- [ ] Wechsel zwischen den Warm-Ups eines Lernbereichs über die Check-Navigation bzw. `#check-<Nummer>` funktioniert, „Zum Training“ führt zum richtigen Check.
- [ ] Jede Auswahl einmal falsch und dann richtig, jede Eingabe einmal falsch, mit Dezimalkomma und negativen Zahlen.
- [ ] Bildänderungen (`zeige`) passieren an der richtigen Stelle.
- [ ] Keine MathJax-Fehler (`mjx-merror`), keine Formel überläuft die Karte.
- [ ] Desktop (≥ 960 px, Bild neben den Schritten) und Handy (360–390 px): kein seitliches Scrollen, nichts ragt über den Kartenrand, Navigation bleibt an ihrem Platz, Zuordnen steht untereinander. Möglichst keine abgesetzte Formel scrollt im eigenen Kasten.
- [ ] Hell- und Dunkelmodus.
- [ ] Fachlich: alle Zahlen und Gleichungen nachgerechnet, Begriffe wie im Skript.

**Automatisierter Durchlauf:** Ein Playwright-Skript liest die Daten aus `#warmup-data` (Objekt mit einem Eintrag pro Datendatei des Lernbereichs) und löst jeden Schritt anhand von `korrekt`, `loesung` bzw. `paare`. **Hinweis:** In einem verborgenen Browser-Tab zeichnet der Browser keine neuen Bilder (kein `requestAnimationFrame`). Dann hängen normale Playwright-Klicks, und Bildschirmfotos zeigen veraltete Zustände. Dort Klicks mit `locator.dispatchEvent('click')` auslösen und Bildschirmfotos nur im sichtbaren Tab machen.


## Prüfskript

`python _data/warmup/validate_warmup.py` prüft alle Datendateien und endet mit Exit-Code 1, sobald etwas nicht stimmt:

- `check_id` fehlt oder fehlt in `_data/checks.json`; Ordner oder Dateiname passen nicht zu `Lernbereich`, `Nummer`, `Sammlung`
- abgeleitete Felder (`titel`, `kompetenz`, `nummer`, `training_url`, `lernbereich_name`) oder unbekannte Felder in der Datei
- unbekannte `phase`, unbekannter Bild- oder Schritttyp (`typ`)
- `auswahl`: `korrekt` außerhalb der Optionen; `eingabe`: Feld ohne (numerische) `loesung`; `zuordnen`: unvollständige `paare`; `markieren`: ohne Matrix oder mit ungültigen Zeilen
- `zeige` verweist auf eine nicht vorhandene `id` (Graph-Punkte, Steckbrief-Einträge), Matrixzeile/-spalte, ein Baumfeld außerhalb 1–10 oder einen Bereich bzw. Wert außerhalb $0$ bis $n$ (Histogramm, Zahlenstrahl), oder die Karte hat gar kein Bild
- Modulseite `lernbereiche/<gebiet>/<lb>/warmup.md` fehlt
- `</script` in einem Text (würde die Einbettung als JSON brechen)


## Bekannte Grenzen und offene Punkte

- **Handy:** Bei schmalem Bildschirm steht das Bild über den Schritten. Wer unten etwas einträgt, sieht die Änderung oben nicht sofort.
- **Noch nicht verdrahtet (bewusst):** Feed, Speicherung des Fortschritts, Verlinkung aus Skript, Kompetenzliste, Training oder Navigation (Reiter in `_includes/module/nav.html` ausgeblendet). Die Modulseiten und die Übersicht `/warmup.html` sind nur über ihre URL erreichbar, `noindex` und nicht in der Sitemap. Bei einer Freischaltung zusätzlich den Hinweis „Prototyp“ im Kartenkopf (`buildCardHeader` in `warmup.js`) entfernen.
- **Wachstum:** Neue Interaktionen als allgemeine Schritt- oder Bildtypen im gemeinsamen Skript ergänzen, nie Code für einen einzelnen Check. Neue Typen auch im Prüfskript eintragen. Wird das Skript zu groß, aufteilen in `steps/` und `visuals/`.
