# Feed

## Dokumentstatus

Kanonische, normative Feed-Spezifikation. Umgesetzt mit den Migrationen `supabase/migrations/20261121120000_feed_simplification.sql` (neues Modell) und `20261121130000_feed_legacy_cleanup.sql` (Altlasten des Cursor-Feeds entfernt).

- Tabellen und RPCs im Gesamtzusammenhang stehen in `.github/benutzerverwaltung-mvp.md`.
- Quoten und Abschluss-Popup stehen in `.github/quoten.md`.

## Leitidee

**Fortschritt ist ein Fakt, der Feed ist nur eine Empfehlung.**

- Jede einmal durchgemachte Aktivität einer Session zählt für den Session-Fortschritt, egal ob sie aus dem Feed oder aus der freien Navigation gestartet wurde.
- Der Session-Fortschritt ist rein quantitativ („Aktivität einmal durchgemacht“). Qualität zeigen die Quoten im Dashboard; gezielte Wiederholungen verbessern die Quote, nicht den Fortschritt.
- Der Feed empfiehlt die didaktisch sinnvollste nächste offene Aktivität. Er sperrt nichts, hat keinen Cursor, keinen Sticky-Lock und keine gespeicherten Zeitfenster.
- Check-Karten haben kein Feed-Icon und keinen Feed-Modus mehr. Alle Aktivitäten laufen gleich: Abschluss über das pulsierende Haken-Icon, danach das Abschluss-Popup.

## Aktivitäten einer Session

| Aktivität | Ebene | `activity_key` |
| --- | --- | --- |
| `start` | je Lernbereich | `lernbereich:{slug}:start` |
| `training`, `test`, `recall`, `feynman` | je Check | `check:{check_id}:{step}` |
| `flashcards` | je Lernbereich mit mindestens einem Check in der Session | `lernbereich:{slug}:flashcards` |

Didaktische Kettenreihenfolge je Check: `training` → `test` → `recall` → `feynman`.

- Die Reihenfolge ist eine **Empfehlung**. Schritte zählen unabhängig voneinander; ein frei vorgezogener Schritt zählt sofort voll.
- Aktivitäten von vor dem Session-Start zählen nicht (kein Backfill aus der Historie).
- Warm-Up ist (noch) keine Session-Aktivität.

## Wann gilt eine Aktivität als abgeschlossen?

Sobald das Modul die Aktivität als durchgemacht meldet (das Haken-Icon wird abschließbar bzw. der Durchgang wird gespeichert):

- `training`: Aufgabe vollständig bearbeitet (auch im Skript). Ein Durchgang mit global eingeblendeten Lösungen wird nicht gewertet und zählt nicht.
- `test`: Testdurchgang beendet.
- `recall`, `feynman`: Durchgang über das Haken-Icon abgeschlossen; das Ergebnis fließt nur in die Quote.
- `flashcards`: Durchgang beendet (frei oder Retention).
- `start`: Klick auf das Haken-Icon der Startseite.

## Datenmodell

- `session_activity_completions (session_id, activity_key, activity_type, lernbereich_slug, check_id, completed_at)`, Primärschlüssel `(session_id, activity_key)`: genau ein Abschluss je Aktivität und Session. Einzige Quelle des Session-Fortschritts.
- Offene Aktivitäten werden immer abgeleitet: Session-Aktivitäten (`session_lernbereiche`, `session_check_state` ohne `session_check_exclusions`) minus Abschlüsse. Serverseitig: `session_activity_items(session_id)`.
- `session_check_state` ist nur Mitgliedschaft (welche Checks gehören zur Session).
- Rohlog bleiben `user_activity_events` (Quoten, XP, Statistik).
- Abgeschlossene Aktivitäten bleiben bei Session-Bearbeitung stabil; entfernte Checks zählen nicht mehr, kommen bei erneutem Hinzufügen aber mit ihren Abschlüssen zurück.

## Schreibweg

Es gibt genau einen Schreibweg mit zwei Einstiegen:

- `record_user_activity(...)` (alle Module) ruft `credit_session_activity(...)` auf.
- `complete_session_start(p_lernbereich_slug)` für `start`.

`credit_session_activity` trägt den Abschluss idempotent in die aktive Session ein, falls die Aktivität dazugehört und noch offen ist. Bei neuer Gutschrift:

- Der user-scoped Aktivitätszähler (`user_feed_activity_counters`) für den Retention-Takt steigt um 1.
- Sind danach alle Check-Schritte eines Lernbereichs erledigt, startet die Flashcards-Wiederholung des Lernbereichs (`user_retention_scopes`).

## Empfehlung (`get_feed_recommendation`)

Zustandslos berechnet bei jedem Aufruf. Kandidaten:

- offenes `start`
- je Check der erste offene Schritt in Kettenreihenfolge
- offenes `flashcards`, sobald alle `training`-Schritte des Lernbereichs erledigt sind

`G` = empfohlener Abstand zwischen zwei Schritten derselben Kette (`system_settings.feed.recommendation_gap_hours`, Standard 20 h, „über Nacht“). Anker einer Kette ist ihr letzter Abschluss.

Prioritätsklassen:

1. **Reife Folgeschritte**: Anker + `G` ist erreicht. Weiter fortgeschrittene Ketten zuerst (mehr erledigte Schritte), dann ältester Anker. `flashcards` reift mit dem letzten `training` des Lernbereichs + `G`.
2. **Neuer Stoff**: `start` und erste `training`s noch unberührter Checks, in Lernbereichs-Reihenfolge (Gebiet, Sortierindex), innerhalb eines Lernbereichs `start` vor den Trainings nach Check-Nummer.
3. **Vorgezogene Folgeschritte**: Anker + `G` noch nicht erreicht; früheste Reife zuerst. Es gibt keinen Wartezustand: Solange etwas offen ist, gibt es eine Empfehlung.

Konsolidieren geht damit vor neuem Stoff, und neuer Stoff vor zu frühem Wiederholen.

Fällige Retention-Flashcards werden im Frontend vor einer Klasse-3-Empfehlung gezeigt (siehe Retention).

## Tagesziel und Badge (`feed_attention_summary`)

Der rote Punkt mit Zahl im Header ist ein schlichtes Tagessignal („heute noch X“):

- `tagesziel = ceil(max(activities_per_day, erforderliches Tempo))`
- erforderliches Tempo nur bei explizitem Zieldatum: `(offen + heute erledigt) / max(Zieldatum − heute, 1)` – bezogen auf den Stand zu Tagesbeginn, damit das Ziel über den Tag stabil bleibt.
- `badge = min(offen, max(0, tagesziel − heute erledigt))`; der Tag läuft nach `Europe/Berlin`.
- Im Frontend kommen fällige Retention-Flashcards dazu.
- Es gibt keine Zustände „fällig“/„überfällig“. Den Zeitdruck zeigt nur die Einschätzung neben dem Zieldatum (z. B. „Sportlich“).

## Abschluss-Popup

Einheitlich für alle Aktivitäten (`assets/js/modules/ui/task-completion-popup.js`):

- **Nächste Aktion**: lädt die aktuelle Empfehlung und öffnet sie. Entfällt bei einem ungewerteten Trainingsdurchgang (alle Lösungen eingeblendet), weil dieser nicht zählt.
- **Zum Dashboard**
- **Wiederholen**: neuer Durchgang bzw. neue Variante (falls das Modul es anbietet).
- **Auf Seite bleiben**

Die Gutschrift ist zu diesem Zeitpunkt bereits gespeichert; das Popup entscheidet nur über die Navigation.

## Links und Module

- Feed-Links öffnen das Modul ganz normal, bei Check-Aktivitäten mit `?check_id=…` (Modul scrollt zum Check). Keine `feed`-/`activity_*`-Parameter.
- Nur Retention-Flashcards laufen noch im Feed-Kontext (`?feed=1&activity_key=retention:…`) mit eigenen Serverrunden und eigenem Entscheidungsdialog.

## Retention

- Retention bleibt user-scoped und getrennt vom Session-Fortschritt (`user_retention_scopes`, `retention_flashcard_*`).
- Start: sobald alle Check-Schritte eines Lernbereichs der Session erledigt sind.
- Takt: über den Aktivitätszähler (jede neue Session-Gutschrift zählt).
- Ein Retention-Durchgang auf einem Lernbereich mit offener Session-`flashcards`-Aktivität schreibt diese gut.

## Goldszenarien

1. Neue Session: Empfehlung ist `start` des ersten Lernbereichs, danach dessen erste Trainings.
2. Training A erledigt: `test A` wird erst nach `G` als reif empfohlen; vorher kommt neuer Stoff (Training B).
3. Ist kein neuer Stoff mehr offen, wird `test A` vor Ablauf von `G` vorgezogen empfohlen (Klasse 3), statt zu warten.
4. Recall eines Checks frei vor seinem Training erledigt: zählt sofort; die Empfehlung holt das Training als nächsten Schritt dieser Kette nach.
5. Gleiche Aktivität zweimal erledigt: zählt einmal (idempotent); die Quote zählt beide Durchgänge.
6. Start-Aktivität eines Lernbereichs frei abgehakt: zählt, Badge sinkt.
7. Zieldatum geändert: Tagesziel ändert sich sofort; erledigte Aktivitäten bleiben.
8. Check entfernt: seine Aktivitäten fallen aus Fortschritt und Empfehlung.
9. Letzter Check-Schritt eines Lernbereichs erledigt: Flashcards-Wiederholung startet.
10. Zwei Tabs: Es gibt keinen Lock; beide zeigen nach dem nächsten Laden dieselbe Empfehlung.
