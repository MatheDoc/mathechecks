# Quoten (Trefferquoten als Kompetenzinstrument)

## Dokumentstatus

Diese Datei ist die kanonische Spezifikation für die check-, lernbereichs- und gebietsübergreifende Trefferquote in MatheChecks. Sie ist normativ für die Weiterentwicklung. Wo der aktuelle Code noch abweicht, gilt dieses Dokument.

- Feed-Mechanik (Cursor, Sticky-Lock, Zeitfenster) bleibt in `.github/feed.md`.
- Tabellen- und RPC-Grenzen zum produktiven System bleiben in `.github/benutzerverwaltung-mvp.md`.
- Begriffe in `.github/glossary.md`.

## Zielbild

Die Quote ist ein didaktisches Instrument für Kompetenzerleben, keine Zeugnisnote. Sie ist fortschritts-, nicht defizitorientiert: Auch nach anfänglichen Fehlern kann ein Nutzer realistisch wieder auf 100 % kommen. Sie wird ausschließlich aus `training`-Versuchen gebildet; `recall` und `feynman` bleiben reine Selbsteinschätzung und tragen nicht zur Quote bei.

## Grundprinzipien

- Es gibt genau **eine** persistente, user-scoped Quotenquelle pro Check (`check_id`).
- Lernbereichs-, Session- und Gesamtquote sind **Kompositionen** dieser Check-Quote über verschiedene Check-Mengen, kein eigener Rechenweg.
- Die Quote ist ein **Read-Model** über `user_activity_events`; es gibt keine eigene Quoten-Tabelle und keinen materialisierten Quoten-Zustand.
- Alle Stellschrauben liegen zentral in `public.system_settings` und werden serverseitig gelesen.

## Score-Modell

### Fragescore

Jede prüfbare Frage einer Trainingsaufgabe endet in genau einem von zwei Zuständen:

- **beantwortet:** Der Nutzer hat die Frage über `n >= 1` Versuche schließlich korrekt gelöst (alle Versuche vor dem letzten waren falsch).
- **aufgelöst:** Der Nutzer hat sich für diese Frage aktiv die Lösung anzeigen lassen, bevor sie korrekt war.

Der Fragescore ist:

- aufgelöste Frage: `s = 0`
- beantwortete Frage: `s = max(0, 1 - (n - 1) * p)`

`p` ist der Versuchsabzug (`proficiency.retry_penalty`, Default `0.5`). Es gibt **kein** typabhängiges Verhalten; Weiterprobieren ist überall erlaubt. Multiple-Choice-Raten bestraft sich selbst, weil jeder Fehlversuch `n` erhöht.

`p = 0.5` ergibt: 1. Versuch `1.0`, 2. Versuch `0.5`, 3. Versuch `0.0`. Kleinere `p` machen das Weiterprobieren milder.

### Taskscore

Der Taskscore ist das Mittel der Fragescores über alle prüfbaren Fragen der Aufgabe:

`task_score = (Σ s_Frage) / checkable_count`

Eine aufgelöste Frage zählt mit `0` in dieses Mittel (sie fällt **nicht** heraus). Damit lässt sich eine schwere Frage nicht durch „Lösung anzeigen" aus der Wertung drücken, während leichte Fragen 100 % behalten.

### Gate-Regeln

- Das automatische Einblenden der Einzellösung **nach** korrekter Beantwortung beeinflusst die Wertung nicht; die Frage ist bereits gewertet.
- Das Falsch-/Richtig-Styling nach dem Prüfen beeinflusst die Wertung nicht.
- Nur das aktive Anfordern der Lösung **für eine noch nicht korrekte Frage** setzt deren Fragescore auf `0`.
- Das frühere globale `solutionsShown`-Gate (irgendeine sichtbare Lösung ⇒ ganze Aufgabe ungewertet) entfällt zugunsten dieses Per-Frage-Zustands.

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
- `question_attempts`: Array der Versuchszahlen `n` je beantworteter Frage
- `revealed_count`: Anzahl aufgelöster Fragen (Score `0`)

Der Taskscore wird **serverseitig** aus diesen Rohdaten und `proficiency.retry_penalty` berechnet, damit der Versuchsabzug zentral in `system_settings` bleibt. Das Read-Model fällt für Alt-Events ohne dieses Schema auf die frühere `correctCount`/`totalCount`/`solutionsShown`-Logik zurück.

## UI und UX

### Abschluss-Controls

- **Feed-Kontext:** Das pulsierende Feed-Icon mit Entscheidungsdialog (`jetzt wiederholen`, `später`, `abschließen`) bleibt unverändert für `training`, `recall`, `feynman`, `kompetenzliste_gate`, `start` und `flashcards`. Es ist das visuelle Signal „du bist in einer Feed-Aktivität" und steuert den Cursor.
- **Freier Kontext:** `training`, `recall` und `feynman` teilen sich ein **einheitliches** Abschluss-Icon (Haken-Symbol) an **derselben Stelle** wie das Feed-Icon, also im Karten-Header. Es pulsiert grün, sobald die Aktivität abschließbar ist (Training: alle prüfbaren Fragen geprüft; `recall`/`feynman`: Selbsteinschätzung sichtbar) und öffnet das Abschluss-Popup. Der Haken unterscheidet es optisch vom Feed-Signal (Wellen-Icon); beide nutzen dieselbe Header-Position und Pulsoptik. `kompetenzliste` bekommt im freien Aufruf **kein** Abschluss-Control.

### Abschluss-Popup

- Das Popup orientiert sich gestalterisch am Feed-Entscheidungsdialog (Eyebrow, Titel, zweispaltige Aktionsbuttons mit Icon, Label und Detailzeile).
- Trainings-Abschluss zeigt das **Quotendelta** des Checks in allen drei Trainings-Modi: Feed-Training eines Session-Checks, freies Training eines Session-Checks, freies Training eines Nicht-Session-Checks.
- Aufwärts-Delta (z. B. 60 % → 80 %) wird motivierend animiert dargestellt.
- Abwärts-Delta wird sachlich und ohne Demotivation dargestellt.
- Folge-Optionen sind ausschließlich `Wiederholen` und `Zum Dashboard`. `Wiederholen` lädt im Training eine neue Variante (neuer Taskscore); bei `recall`/`feynman` ist es erneutes Durcharbeiten ohne Quote. `Zum Dashboard` ist im freien Kontext reine Navigation und verändert den Feed nicht.
- `recall`/`feynman` zeigen kein Quotendelta.
- **Ungewerteter Durchgang:** Wurde die globale Aktion „alle Lösungen anzeigen" (Drei-Punkte-/Toolbar-Menü der Aufgabe) genutzt, zählt der **ganze Versuch nicht**. Es wird kein Trainings-Event geschrieben, die Quote bleibt unverändert, und statt des Quotendeltas erscheint ein kurzer Hinweis im Popup. Das gilt in Feed- wie freiem Training.

### Per-Frage-Fluss im Training

1. Frage ungeprüft.
2. Geprüft und korrekt: Einzellösung wird automatisch eingeblendet (exakter Wert, vermeidet Folgefehler), Frage ist gewertet.
3. Geprüft und falsch: Der Nutzer kann weiterprobieren (`n` erhöht sich) oder die Lösung einzeln anzeigen (Fragescore `0`).
4. Globale Aktion „alle Lösungen anzeigen": macht den gesamten Durchgang ungewertet (siehe Abschluss-Popup). Per-Frage-Lösungen aus Schritt 3 bleiben davon unberührt und zählen weiterhin als Fragescore `0`.

### Dashboard-Worklist

- Eine Box listet die Session-Checks als sortierte Fortschrittsbalken, die schwächsten oben.
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
2. Eine im zweiten Versuch gelöste Frage trägt bei `p = 0.5` den Fragescore `0.5`.
3. „Lösung anzeigen" für eine Frage setzt deren Fragescore auf `0`, die übrigen Fragen bleiben gewertet.
4. Drei aufeinanderfolgende perfekte Varianten heben die Check-Quote auf `100 %`, auch nach schwachem Start.
5. Ein alter schwacher Taskscore verliert mit jeder neuen Variante an Gewicht und fällt nach `N` Varianten aus dem Fenster.
6. Freies Training eines Session-Checks hebt die Session-Quote, ohne den Feed-Cursor zu verändern.
7. Die Lernbereichs-Quote berücksichtigt nur trainierte Checks.
8. Das Abschluss-Popup zeigt in allen drei Trainings-Modi ein Quotendelta; aufwärts motivierend, abwärts sachlich.
9. `recall`/`feynman` erzeugen keine Quote und kein Delta.
10. Das automatische Einblenden der Einzellösung nach korrekter Antwort verändert die Wertung nicht.

## Konkrete nächste Schritte

1. (a) Read-Model und `system_settings`-Parameter bereitstellen.
2. (b) Gate von global auf Per-Frage umstellen.
3. (c) Freies Abschluss-Control und Drei-Modi-Popup mit Delta.
4. (d) Per-Frage-Auto-Lösung und Weiterprobieren/Lösung-anzeigen.
5. (e) Dashboard-Worklist.
6. Legacy entfernen und `glossary.md`/`benutzerverwaltung-mvp.md` nachziehen.
