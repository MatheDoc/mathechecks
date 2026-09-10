# Quoten (Trefferquoten als Kompetenzinstrument)

## Dokumentstatus

Diese Datei ist die kanonische Spezifikation für die check-, lernbereichs- und gebietsübergreifende Trefferquote in MatheChecks. Sie ist normativ für die Weiterentwicklung. Wo der aktuelle Code noch abweicht, gilt dieses Dokument.

- Feed-Mechanik (Cursor, Sticky-Lock, Zeitfenster) bleibt in `.github/feed.md`.
- Tabellen- und RPC-Grenzen zum produktiven System bleiben in `.github/benutzerverwaltung-mvp.md`.
- Begriffe in `.github/glossary.md`.

## Zielbild

Die Quote ist ein didaktisches Instrument für Kompetenzerleben, keine Zeugnisnote. Sie ist fortschritts-, nicht defizitorientiert: Auch nach anfänglichen Fehlern kann ein Nutzer realistisch wieder auf 100 % kommen. Die Trainingsquote wird ausschließlich aus `training`-Versuchen gebildet; `recall` und `feynman` tragen nicht zu **dieser** Quote bei. Stattdessen speisen `recall` und `feynman` jeweils ein eigenes, separates Read-Model, siehe [Recall-Quote](#recall-quote-separates-paralleles-read-model) und [Feynman-Quote](#feynman-quote-separates-paralleles-read-model).

## Grundprinzipien

- Es gibt genau **eine** persistente, user-scoped Quotenquelle pro Check (`check_id`).
- Lernbereichs-, Session- und Gesamtquote sind **Kompositionen** dieser Check-Quote über verschiedene Check-Mengen, kein eigener Rechenweg.
- Die Quote ist ein **Read-Model** über `user_activity_events`; es gibt keine eigene Quoten-Tabelle und keinen materialisierten Quoten-Zustand.
- Alle Stellschrauben liegen zentral in `public.system_settings` und werden serverseitig gelesen.

## Score-Modell

### Feldscore und Fragescore

Jedes logische Antwortfeld einer Trainingsaufgabe endet in genau einem von zwei Zuständen. Zusammengesetzte Controls wie Zahl plus „existiert nicht“ (`NUMERICAL_OPT`) zählen als ein Feld:

- **beantwortet:** Der Nutzer hat das Feld über `n >= 1` Versuche schließlich korrekt gelöst (alle Versuche vor dem letzten waren falsch).
- **aufgelöst:** Der Nutzer hat die Lösung der Teilfrage angefordert, bevor dieses Feld korrekt geprüft war.

Der Feldscore ist:

- aufgelöstes Feld: `s = 0`
- beantwortetes Feld: `s = max(0, 1 - (n - 1) * p)`

`p` ist der Versuchsabzug (`proficiency.retry_penalty`, Default `0.5`). Es gibt **kein** typabhängiges Verhalten; Weiterprobieren ist überall erlaubt. Multiple-Choice-Raten bestraft sich selbst, weil jeder Fehlversuch `n` erhöht.

`p = 0.5` ergibt: 1. Versuch `1.0`, 2. Versuch `0.5`, 3. Versuch `0.0`. Kleinere `p` machen das Weiterprobieren milder.

Der Fragescore ist das Mittel der Feldscores dieser Teilfrage. Bereits korrekt geprüfte Felder behalten ihren erzielten Score, auch wenn anschließend die Einzellösung angezeigt wird; nur noch offene Felder werden aufgelöst. Bloß eingetragene, ungeprüfte Werte zählen nicht als korrekt beantwortet.

Bei zwei Feldern ergibt „eines sofort richtig, eines aufgelöst“ den Fragescore `0.5`; „eines sofort richtig, eines im zweiten Versuch richtig“ ergibt `0.75`.

### Taskscore

Der Taskscore ist das Mittel der Fragescores über alle prüfbaren Fragen der Aufgabe:

`task_score = (Σ s_Frage) / checkable_count`

Aufgelöste Felder zählen mit `0` in ihr Fragenmittel (sie fallen **nicht** heraus). Alle prüfbaren Teilfragen haben im Taskscore dasselbe Gewicht, unabhängig von ihrer Feldanzahl. Eine Frage mit neun Matrixelementen wiegt somit nicht mehr als eine Frage mit einem Feld.

### Gate-Regeln

- Das automatische Einblenden der Einzellösung **nach** korrekter Beantwortung beeinflusst die Wertung nicht; die Frage ist bereits gewertet.
- Das Falsch-/Richtig-Styling nach dem Prüfen beeinflusst die Wertung nicht.
- Das aktive Anfordern der Einzellösung setzt nur die **noch nicht korrekt geprüften Felder** dieser Teilfrage auf `0`; bereits erzielte Feldscores bleiben erhalten.
- Das frühere globale `solutionsShown`-Gate (irgendeine sichtbare Lösung ⇒ ganze Aufgabe ungewertet) entfällt zugunsten dieser Feldzustände. Die explizite globale Aktion „alle Lösungen einblenden“ bleibt dagegen ungewertet (siehe Abschluss-Popup).

### Wertungszeitpunkt

- Ein Taskscore entsteht beim **ersten vollständigen Abschluss** einer Task-Instanz, also sobald alle prüfbaren Fragen aufgelöst oder korrekt beantwortet sind.
- Es entsteht genau **ein** Event pro Task-Instanz.
- Verbesserung erfolgt über eine **neue Variante** (Reload): neue Task-Instanz, neuer Taskscore, der ins Recency-Fenster wandert.

## Aggregation zur Check-Quote

Die Check-Quote ist das **recency-gewichtete Mittel** der letzten `N` Taskscores dieses Checks (`proficiency.window_size`, Default `3`):

```
quote = Σ_i ( d^alter_i * task_score_i ) / Σ_i ( d^alter_i )
```

- `alter_i = 0` für den jüngsten Taskscore, `1` für den nächstälteren, usw.
- `d` ist der Recency-Decay (`proficiency.recency_decay`, Default `0.5`); jüngere Taskscores zählen stärker.
- Nur die jüngsten `N` Taskscores gehen ein; ältere fallen aus dem Fenster.

Beispiel mit `N = 3`, `d = 0.5`, Taskscores alt→neu `0, 1, 1`:
`(0.25*0 + 0.5*1 + 1*1) / (0.25 + 0.5 + 1) = 1.5 / 1.75 ≈ 0.857`.

## Komposition

- **Check-Quote:** wie oben, pro `check_id`.
- **Lernbereichs-Quote:** Mittel der Check-Quoten **nur der trainierten** Checks dieses Lernbereichs. Untrainierte Checks zählen nicht (Abdeckung/Quantität hat eine eigene Anzeige).
- **Session-Quote:** Mittel der Check-Quoten der Checks in der aktiven Session (View-Filter auf dieselbe Check-Quote).
- **Gesamt-/Lebenszeitquote:** Mittel der Check-Quoten aller trainierten Checks. Sie nutzt dasselbe Modell und ersetzt die frühere kumulative Micro-Average.

Da nur `check_id` zählt, hebt **jedes** Training eines Checks die Quote — frei oder im Feed, innerhalb oder außerhalb der Session.

## Erfassung im Event

`record_user_activity('training', ...)` schreibt pro abgeschlossener Task-Instanz ein Event mit user-scoped `check_id` und `lernbereich_slug`. Die Rohdaten für den serverseitigen Score liegen in `details`:

- `checkable_count`: Anzahl prüfbarer Fragen
- `question_fields`: Array je prüfbarer Teilfrage mit einem Array ihrer logischen Antwortfelder, jeweils `{attempts, correct, revealed}`. Dies ist die maßgebliche Scorequelle für neue Events.
- `question_attempts`: kompatibles Altschema mit Versuchszahlen je vollständig korrekt beantworteter Frage
- `revealed_count`: Anzahl per Einzellösung abgeschlossener, nicht vollständig korrekt beantworteter Fragen; kein pauschaler Nullscore für diese Fragen im neuen Schema

Der Taskscore wird **serverseitig** aus diesen Rohdaten und `proficiency.retry_penalty` berechnet, damit der Versuchsabzug zentral in `system_settings` bleibt. Alt-Events ohne `question_fields` behalten ihre bisherige Berechnung aus `question_attempts`/`revealed_count` beziehungsweise `correctCount`/`totalCount`/`solutionsShown`. Feldversuche werden nicht nachträglich aus Altdaten erfunden. Bei bereits lokal gespeicherten Durchgängen ohne Feldzustände werden vorhandene Fragenzustände konservativ auf die Felder übernommen; neue Durchgänge erfassen die Feldhistorie vollständig.

## UI und UX

### Abschluss-Controls

- **Feed-Kontext:** Das pulsierende Feed-Icon mit Entscheidungsdialog (`jetzt wiederholen`, `später`, `abschließen`) bleibt unverändert für `training`, `recall`, `feynman`, `test`, `start` und `flashcards`. Es ist das visuelle Signal „du bist in einer Feed-Aktivität" und steuert den Cursor.
- **Freier Kontext:** `training`, `recall` und `feynman` teilen sich ein **einheitliches** Abschluss-Icon (Haken-Symbol) an **derselben Stelle** wie das Feed-Icon, also im Karten-Header. Es pulsiert grün, sobald die Aktivität abschließbar ist (Training: alle prüfbaren Fragen korrekt beantwortet oder aufgelöst; `recall`: alle Items korrekt oder aufgelöst; `feynman`: KI-Auswertung liegt vor) und öffnet das Abschluss-Popup. Der Haken unterscheidet es optisch vom Feed-Signal (Wellen-Icon); beide nutzen dieselbe Header-Position und Pulsoptik. `kompetenzliste` bekommt im freien Aufruf **kein** Abschluss-Control.

### Abschluss-Popup

- Das Popup orientiert sich gestalterisch am Feed-Entscheidungsdialog (Eyebrow, Titel, zweispaltige Aktionsbuttons mit Icon, Label und Detailzeile).
- Trainings-Abschluss zeigt das **Quotendelta** des Checks in allen drei Trainings-Modi: Feed-Training eines Session-Checks, freies Training eines Session-Checks, freies Training eines Nicht-Session-Checks.
- Aufwärts-Delta (z. B. 60 % → 80 %) wird motivierend animiert dargestellt.
- Abwärts-Delta wird sachlich und ohne Demotivation dargestellt.
- Folge-Optionen sind ausschließlich `Wiederholen` und `Zum Dashboard`. `Wiederholen` lädt im Training eine neue Variante (neuer Taskscore); bei `recall` und `feynman` startet es einen neuen Durchgang. `Zum Dashboard` ist im freien Kontext reine Navigation und verändert den Feed nicht.
- `recall` und `feynman` zeigen ihr eigenes Quotendelta, aber verändern die Trainingsquote nicht.
- **Ungewerteter Durchgang:** Wurde die globale Aktion „alle Lösungen einblenden" (Drei-Punkte-/Toolbar-Menü der Aufgabe) genutzt, zählt der **ganze Versuch nicht**. Es wird kein Trainings-Event geschrieben, die Quote bleibt unverändert, und statt des Quotendeltas erscheint ein kurzer Hinweis im Popup. Das gilt in Feed- wie freiem Training.

### Per-Frage-Fluss im Training

Eine **prüfbare Frage** ist eine Teilfrage mit mindestens einem Eingabefeld (`NUMERICAL`, `NUMERICAL_OPT`, `INTERVAL_BOUND`, `ANALYSIS_BOUND`, `MC`). Teilfragen ohne Eingabefeld (z. B. gegebene Werte) zählen nicht in `checkable_count`.

Bedienung und Wertung sind getrennt: Pro Teilfrage gibt es weiterhin genau **einen** Prüf-Button (am letzten Eingabefeld); Enter in einem beliebigen Feld prüft ebenfalls die ganze Teilfrage. Eine Prüfung markiert alle ausgefüllten Felder als richtig/falsch, leere Felder bleiben neutral. Versuche und Scores werden jedoch **pro logischem Antwortfeld** erfasst und anschließend zum Fragescore gemittelt.

1. Frage ungeprüft.
2. Geprüft und korrekt: Einzellösung wird automatisch eingeblendet (exakter Wert, vermeidet Folgefehler), Frage ist gewertet.
3. Geprüft und teilweise/falsch: Bereits korrekt geprüfte Felder behalten ihren Score. Der Nutzer kann offene Felder weiterprobieren oder die Einzellösung anzeigen (nur offene Felder erhalten Score `0`).
4. Globale Aktion „alle Lösungen einblenden": macht den gesamten Durchgang ungewertet (siehe Abschluss-Popup). Einzellösungen aus Schritt 3 lösen dieses globale Gate nicht aus.

**Versuchszählung bei mehreren Feldern:** Jede Prüfung erhöht `n` für jedes ausgefüllte, noch offene Feld. Leere, bereits korrekt beantwortete oder aufgelöste Felder erhalten keinen weiteren Versuch. Schrittweises Ausfüllen bleibt möglich; Fehlversuche eines Felds zählen dabei auch dann, wenn andere Felder noch leer sind. Nach korrekter Prüfung oder Auflösung ist dessen Score für diesen Durchgang festgeschrieben.

**Numerische Eingaben:** Ein nicht-numerischer Anhang ohne weitere Ziffern oder Rechenzeichen (Einheiten wie `5 ME`, `12 %`, Sprach-Rauschen) wird toleriert, die Zahl davor gewertet. Folgen nach der Zahl weitere Ziffern oder Rechenzeichen (`2/3`, `3-4`, `5.3.2`), gilt die Eingabe als nicht interpretierbar und wird als falsch gewertet (zählt als Versuch).

### Dashboard-Worklist

- Eine Box listet die Session-Checks (oder wahlweise alle Checks oder Auffrischen-Checks)als sortierte Fortschrittsbalken, die schwächsten oben.
- Klick auf einen Check öffnet **freies Training** dieses Checks. Das verändert den Core-Feed nicht (kein Cursor, kein Lock) und hebt dennoch die Session-Quote, weil diese nur ein View-Filter auf die Check-Quote ist.

### Session-Hervorhebung

Auf Modulseiten gibt es keinen Session-Marker. Der Session-Fokus wird allein über die Dashboard-Worklist transportiert.

## Systemwerte

Neue `public.system_settings`-Schlüssel:

- `proficiency.window_size` (`value_integer`, Default `3`): Fenstergröße `N`.
- `proficiency.recency_decay` (`value_numeric`, Default `0.5`): Recency-Decay `d`.
- `proficiency.retry_penalty` (`value_numeric`, Default `0.5`): Versuchsabzug `p`.

## Serverseitige Operationen (Zielbild)

- `get_user_activity_overview()`: liefert u. a. die Gesamtquote als Komposition der Check-Quoten.
- Eine Worklist-/Proficiency-Projektion liefert pro Check (und je Lernbereich) die aktuelle Quote für Dashboard und Abschluss-Popup, inklusive vorigem Wert für das Delta.

Namen sind teils Platzhalter; maßgeblich ist die Trennung zwischen Rohversuch (`user_activity_events`) und abgeleiteter Quote (Read-Model).

## Goldszenarien

1. Erste korrekte Beantwortung aller Fragen einer Aufgabe ergibt Taskscore `1.0`.
2. Ein im zweiten Versuch gelöstes Feld trägt bei `p = 0.5` den Feldscore `0.5`.
3. „Lösung anzeigen" für eine Frage setzt nur deren noch offene Felder auf `0`; bereits korrekt geprüfte Felder und übrige Fragen behalten ihre Scores.
4. Drei aufeinanderfolgende perfekte Varianten heben die Check-Quote auf `100 %`, auch nach schwachem Start.
5. Ein alter schwacher Taskscore verliert mit jeder neuen Variante an Gewicht und fällt nach `N` Varianten aus dem Fenster.
6. Freies Training eines Session-Checks hebt die Session-Quote, ohne den Feed-Cursor zu verändern.
7. Die Lernbereichs-Quote berücksichtigt nur trainierte Checks.
8. Das Abschluss-Popup zeigt in allen drei Trainings-Modi ein Quotendelta; aufwärts motivierend, abwärts sachlich.
9. `recall`/`feynman` erzeugen keine Quote und kein Delta **in diesem Training-Quote-Modell**. Beide haben eigene, separate Read-Models und ändern nichts am Training-Quote-Verhalten.
10. Das automatische Einblenden der Einzellösung nach korrekter Antwort verändert die Wertung nicht.
11. Eine Frage mit zwei Feldern, eines sofort richtig und eines aufgelöst, ergibt Fragescore `0.5`.
12. Eine Frage mit zwei Feldern, eines sofort richtig und eines im zweiten Versuch richtig, ergibt Fragescore `0.75`.
13. Teilfragen bleiben im Taskscore gleich gewichtet, unabhängig von ihrer Feldanzahl.

## Konkrete nächste Schritte

1. (a) Read-Model und `system_settings`-Parameter bereitstellen.
2. (b) Gate von global auf Per-Frage umstellen.
3. (c) Freies Abschluss-Control und Drei-Modi-Popup mit Delta.
4. (d) Per-Frage-Auto-Lösung und Weiterprobieren/Lösung-anzeigen.
5. (e) Dashboard-Worklist.
6. Legacy entfernen und `glossary.md`/`benutzerverwaltung-mvp.md` nachziehen.

## Recall-Quote (separates, paralleles Read-Model)

Die Recall-Quote ist **kein Teil** der obigen Trainings-Quote und beeinflusst sie nicht. Sie ist eine eigenständige, analog aufgebaute Projektion für den Recall-Check (Cue/Response-Kernpunkte), weil Recall inhaltlich etwas anderes prüft als Training (aktiver Abruf statt gerechneter Aufgaben) und bewusst eigene Stellschrauben behalten soll.

### Rohdaten

`checks.json` liefert je Check ein `Tipps`-Array aus `{cue, response}`-Objekten sowie `tippOrder` (`shuffle` als Standard, `fixed` z. B. bei Schritten eines Hypothesentests). `cue` kann leer sein (noch nicht redigierter Kernpunkt); die Abfrage bleibt dann „blind“, das Item zählt aber weiterhin.

### Bewertung

Beim Abruf (Retrieve-Stage) tippt der Nutzer je Kernpunkt eine Antwort. Ein minimaler serverseitiger Proxy (`supabase/functions/recall-evaluate`) hält den Gemini-API-Key und bewertet alle geänderten, noch offenen Items eines Durchgangs gebündelt (Score `0.0–1.0` je Item, kurzer Hinweis). Die KI erhält dabei alle aktuellen Antworten als Kontext, gibt aber nur für die markierten offenen Items neue Bewertungen aus. Bereits korrekte, unveränderte Items werden nicht erneut bewertet. Ein erneuter Klick ohne Textänderung erzeugt weder eine KI-Anfrage noch einen weiteren Versuch. Nach jeder Prüfung werden die Response-Felder direkt eingefärbt. Teilweise/falsche Antworten können im selben Feld beliebig oft nachgebessert und erneut geprüft werden; angezeigte Lösungen zählen wie im Training als aufgelöst. Schlägt die KI-Bewertung fehl (Netzwerk, Rate-Limit, Parsing), werden die Lösungen der noch offenen Items eingeblendet; damit ist der Durchgang abschließbar, diese Items zählen aber als aufgelöst.

### Taskscore und Aggregation

`task_score = Summe der Item-Scores / checkableCount`. Für ein nicht aufgelöstes Item werden der Score der ersten Bewertung `s_1` und der beste Score aller späteren Bewertungen `s_best` gespeichert. Der Item-Score ist `s = s_1 + (s_best - s_1) · w` mit `w = 0,5`. Eine Verbesserung erhöht damit den Score, ersetzt den Erstversuch aber nicht vollständig und kann den Score niemals verschlechtern. Aufgelöste Items zählen als `0`. Ein Durchgang wird erst abschließbar, wenn alle Items entweder aktuell korrekt bewertet wurden oder die Lösung angezeigt wurde.

Die Check-Recall-Quote ist wie bei Training das recency-gewichtete Mittel der letzten `N` Taskscores:

```
recall_quote = Σ_i ( d^alter_i * task_score_i ) / Σ_i ( d^alter_i )
```

mit eigenen Parametern `recall_proficiency.window_size` (Default `3`), `recall_proficiency.recency_decay` (Default `0.5`) und dem aus Kompatibilitätsgründen weiter so benannten `recall_proficiency.retry_penalty` als Verbesserungsgewicht `w` (Default `0.5`) in `system_settings` — unabhängig von `proficiency.*`.

### Erfassung und Projektion

`record_user_activity('recall', ...)` schreibt pro abgeschlossenem Durchgang `details.rawItemScores`, `details.firstItemScores`, `details.bestItemScores`, `details.itemAttempts`, `details.itemRevealed`, `details.checkableCount`, `details.revealedCount` plus den kompatiblen `details.itemScores`-Snapshot, `selfOutcome` und `model`. `public._compute_recall_task_score(details, w)` berechnet daraus den Taskscore; Legacy-Events ohne Erst-/Bestscore behalten ihre bisherige Retry-Berechnung. `public.get_user_recall_proficiency()` liefert `overall`/`checks[]`/`byLernbereich` analog zu `get_user_check_proficiency()`; `get_user_activity_overview()` liefert sie zusätzlich unter `recallProficiency`.

### UI

Die Bewertung erscheint inline am jeweiligen Response-Feld: gemeinsame Trainingsklassen `answer-input`, `is-correct`/`is-incorrect`, zusätzlich `is-partial` für orange, KI-Hinweis direkt unter dem Feld. Bei korrekten Antworten wird die hinterlegte Response direkt angezeigt; bei teilweise/falsch erscheint ein Button „Lösung anzeigen“. Das Header-Abschluss-Icon pulsiert und wird erst klickbar, wenn alle Items korrekt oder aufgelöst sind.

## Feynman-Quote (separates, paralleles Read-Model)

Die Feynman-Quote ist **kein Teil** der Trainingsquote und beeinflusst sie nicht. Sie misst, ob Schülererklärungen zu konkreten Aufgaben den fachlichen Lösungsweg verständlich und tragfähig beschreiben. Grundlage sind zufällig gezogene Aufgaben aus derselben Sammlung wie im Training; statt numerischer Antwortfelder gibt es freie Erklärungstextfelder.

### Bewertung

Ein serverseitiger Proxy (`supabase/functions/feynman-evaluate`) hält den Gemini-API-Key und bewertet beim ersten Prüfen alle Teilfragen eines Durchgangs gebündelt. Bei späteren Prüfungen erhält die KI weiterhin Check-Kontext, Kompetenz, Tipps, Aufgabenstellung, Visual-Kontext, interne Zielantworten, ggf. Referenzbeispiel und alle aktuellen Schülerantworten, bewertet aber ausschließlich die seit ihrer letzten Bewertung geänderten Teilantworten. Ein erneuter Klick ohne Textänderung erzeugt weder eine KI-Anfrage noch einen weiteren Versuch. Ein vollständiges Ausrechnen bis zum Endwert ist nicht zwingend erforderlich, wenn der Lösungsweg fachlich korrekt erklärt ist.

Score-Skala:

- `1.0`: sehr gut erklärt; zentrale Schritte, Begriffe und Begründung sind korrekt
- `0.8`: im Kern gut; kleine Ungenauigkeit oder Lücke
- `0.5`: teilweise brauchbar; ein zentraler Schritt, Begriff oder Zusammenhang fehlt
- `0.0`: fachlich falsch, kaum verwertbar oder leer

### Taskscore und Aggregation

`task_score = Summe der Item-Scores / checkableCount`. Für jedes Item gilt wie bei Recall `s = s_1 + (s_best - s_1) · w` mit `w = 0,5`. Eine spätere optionale Anzeige einer KI-Erklärung kann über `itemRevealed` als aufgelöst und damit `0` gewertet werden; im MVP gibt es zunächst nur Feedback, keine Musterlösung.

Die Check-Feynman-Quote ist das recency-gewichtete Mittel der letzten `N` Taskscores:

```
feynman_quote = Σ_i ( d^alter_i * task_score_i ) / Σ_i ( d^alter_i )
```

mit eigenen Parametern `feynman_proficiency.window_size` (Default `3`), `feynman_proficiency.recency_decay` (Default `0.5`) und dem aus Kompatibilitätsgründen weiter so benannten `feynman_proficiency.retry_penalty` als Verbesserungsgewicht `w` (Default `0.5`) in `system_settings` — unabhängig von `proficiency.*` und `recall_proficiency.*`.

### Erfassung und Projektion

`record_user_activity('feynman', ...)` schreibt pro abgeschlossenem Durchgang `details.rawItemScores`, `details.firstItemScores`, `details.bestItemScores`, `details.itemAttempts`, `details.itemRevealed`, `details.checkableCount`, `details.revealedCount`, `details.itemScores`, `selfOutcome`, `taskIndex` und `model`. `public._compute_feynman_task_score(details, w)` berechnet daraus den Taskscore; Legacy-Events ohne Erst-/Bestscore behalten ihre bisherige Retry-Berechnung. `public.get_user_feynman_proficiency()` liefert `overall`/`checks[]`/`byLernbereich` analog zu Recall.

### UI

Feynman-Karten nutzen das breite Aufgabenlayout aus dem Training: links Einleitung/Visualisierung, rechts Teilfragen mit freien Erklärungstextfeldern und Mikrofon. Die Bewertung erscheint inline am jeweiligen Feld: grün `gut erklärt`, orange `nachbessern`, rot `noch unklar`. Der freie Abschluss und der Feed-Abschluss werden erst nach einer vollständigen KI-Auswertung aktiv. Dashboard und Kartenheader zeigen die Feynman-Quote als dritte eigenständige Quote neben Training und Recall.

