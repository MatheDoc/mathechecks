# Feed V2

## Dokumentstatus

Diese Datei beschreibt das fachliche Zielbild für den deterministischen Feed V2 und ist die kanonische Feed-Doku für die Weiterentwicklung.

Der singuläre Core-Feed mit serverseitigen Zeitfenstern, `planned_from`, Sticky-Lock und serverseitigem Cursor ist bereits weitgehend umgesetzt. Wo der aktuelle Stand noch vom Zielbild abweicht, ist dieses Dokument trotzdem normativ für die weitere Arbeit.

- Tabellen, RPCs und Datenmodellgrenzen zum aktuell produktiven System bleiben in `.github/benutzerverwaltung-mvp.md`.
- Übergangs- oder Hybridverhalten außerhalb dieses Zielbilds ist bewusst nicht als eigene zweite Feed-Doku ausgelagert.

## Zielbild

Der Core-Feed zeigt genau ein aktuelles Element statt einer sortierten Mehrkartenliste. Ein Lernbereich beginnt immer mit `start`; danach wird das erste `training` dieses Lernbereichs freigeschaltet. Innerhalb einer Check-Kette werden `training`, `recall`, `feynman` und `kompetenzliste` über echte Zeitfenster statt über Aktivitätszählung gesteuert. Gleichzeitig bleibt das aktuell angezeigte Element während aktiver Arbeit über einen Sticky-Lock stabil sichtbar, auch wenn andere Schritte im Hintergrund fällig werden. Die eigentliche Neuwahl des Feed-Elements passiert erst bei Abschluss, explizitem Verlassen, Ungültigkeit des aktuellen Elements oder nach Lock-Ablauf.

## Scope und Abgrenzung

- Primärer Gegenstand dieser Spezifikation ist der deterministische Core-Feed.
- Retention wird hier nur auf Prinzipienebene festgehalten; eine konkrete Retention-Auswahl- oder Mischlogik wird erst nach Stabilisierung des Core-Feeds neu spezifiziert.
- Freier Modulzugriff bleibt immer möglich und wird nicht vom Feed gesperrt.
- Ein Core-Feed-Schritt darf nur dann abgeschlossen oder weiterbewegt werden, wenn er über einen gültigen Feed-Cursor im Feed-Kontext geöffnet wurde.
- UI-Feinheiten wie Ampel, Farben oder genaue CSS-Zustände sind nicht Teil dieser V2-Spezifikation.
- `warmup` bleibt außerhalb dieses Feed-Schnitts.
- Das Frontend soll den V2-Feed nicht per direktem Tabellen-CRUD steuern.

## Retention und Mischbetrieb

- Retention bleibt fachlich getrennt vom Core-Cursor.
- Retention darf keine Core-Schritte abschließen, weiterbewegen oder den Sticky-Lock eines Core-Elements erneuern.
- Ob Retention später als eigener Cursor, als sekundäre Queue oder nur als Dashboard-Fallback erscheint, wird erst nach Stabilisierung des Core-Feeds entschieden.
- Solange diese Entscheidung offen ist, legt diese Spezifikation bewusst keine normative Mischreihenfolge zwischen Core und Retention fest.
- Sinnvoller Minimalanspruch für die spätere Retention-Anbindung bleibt: Retention darf eine aktive Core-Session nicht dominieren und freier Retention-Zugriff darf vom Core-Feed getrennt bleiben.

## Grundbegriffe

- `activity_key`: Stabile Identität eines Feed-Schritts. Für V2 gilt fachlich `session:{session_id}:area:{lernbereich_id}:step:start` für Lernbereichsstarts und `session:{session_id}:check:{check_id}:step:{step_key}` für Check-Schritte.
- `status`: Persistenter Lebenszykluswert eines Schritts. In V2 reichen `pending`, `completed` und `dropped`; Fälligkeit wird aus den Zeitfeldern abgeleitet.
- `available_from`: Ab dann darf ein Schritt überhaupt im Feed kandidieren.
- `planned_from`: Ab dann sollte ein Schritt aus Session-Sicht drankommen, damit das Ziel realistisch bleibt.
- `overdue_from`: Ab dann gilt ein Schritt als deutlich hinten dran.
- `effective_planned_from`: `max(available_from, planned_from)`.
- `current_activity_key`: Das aktuell gelockte Core-Feed-Element.
- `locked_until`: Zeitstempel, bis zu dem das aktuelle Element sticky bleibt.
- `selected_at`: Zeitpunkt, zu dem der Feed-Cursor auf das aktuelle Element gesetzt wurde.
- `selection_reason`: Grund der letzten Cursor-Wahl. V2 nutzt `initial`, `auto_pick`, `repeat_request`, `lock_expired` und `invalidated`.
- `G`: Basisabstand für didaktische Übergänge innerhalb einer Check-Kette.
- `G_step`: Der für einen konkreten Übergang gesetzte Abstand. Für didaktische Übergänge entspricht er in V2 dem Profilwert `G`.
- `G_gate`: Gate-Abstand für `start -> training`; in V2 gilt `G_gate = 0`.
- `M`: Überfälligkeitsfaktor. Für didaktische Übergänge gilt in V2 fachlich `M = 2` bezogen auf den Abschluss des Vorgängerschritts.
- `L`: Sticky-Lock-Dauer.
- `activities_per_day`: Materialisierte Session-Geschwindigkeit in Aktivitäten pro Tag.
- `required_activities_per_day`: Aus offener Last und verbleibenden Tagen abgeleitete erforderliche Geschwindigkeit in Aktivitäten pro Tag.
- `p`: Druckverhältnis `activities_per_day / required_activities_per_day`.

## Zustandsmodell pro Lernbereich und Check

### Lernbereichsstart

- Jeder Lernbereich beginnt mit genau einer `start`-Aktivität.
- `start` ist ein Gate-Schritt und löst selbst keine spaced-repetition-Kette aus.
- Solange `start` für einen Lernbereich offen ist, darf kein Check-Schritt dieses Lernbereichs im Feed kandidieren.
- Bei mehreren neuen Lernbereichen sind alle `start`-Aktivitäten gleichzeitig verfügbar. Ihre Bearbeitungsreihenfolge ergibt sich aus der kanonischen Reihenfolge.
- `start.available_from` ist der Sessionstart oder der Zeitpunkt, zu dem der Lernbereich zur Session hinzugefügt wurde.
- `start.planned_from` kommt aus der Session-Planung.
- `start.overdue_from` ist planbasiert: Sobald `planned_from` materialisiert ist, gilt `overdue_from = effective_planned_from + G`.
- Nach Abschluss von `start` wird das erste `training` dieses Lernbereichs freigeschaltet.
- Der Gate-Übergang `start -> training` nutzt `G_gate = 0`.
- Das erste `training` ist nach `start` also sofort verfügbar.
- `G_gate = 0` darf nicht dazu führen, dass dieses `training` sofort als überfällig gilt; seine Plan- und Überfälligkeitslogik kommt aus dem Session-Druck.

### Check-Kette

Pro Check ist zu jedem Zeitpunkt höchstens der nächste offene Schritt aktiv:

1. `training`
2. `recall`
3. `feynman`
4. `kompetenzliste`

Für jeden offenen Schritt werden mindestens diese fachlichen Felder benötigt:

- `activity_key`
- `current_step_key`
- `status`
- `available_from`
- `planned_from`
- `overdue_from`
- `step_anchor_completed_at`

Zusätzlich pro aktiver Session:

- `current_activity_key`
- `locked_until`
- `selected_at`
- `selection_reason`

`step_anchor_completed_at` ist der Abschlusszeitpunkt des unmittelbar vorherigen Schritts und bildet die Basis für die Ableitung der Zeitfenster.

## Zeitlogik innerhalb der Check-Kette

### Übergangstypen

V2 trennt Gate-Übergänge und didaktische Übergänge:

- `start -> training`: Gate-Übergang mit `G_gate = 0`
- `training -> recall`: didaktischer Übergang mit `G_step = G`
- `recall -> feynman`: didaktischer Übergang mit `G_step = G`
- `feynman -> kompetenzliste`: didaktischer Übergang mit `G_step = G`

Für V2 werden die drei didaktischen Übergänge gleich behandelt. Sie teilen denselben Basisabstand `G`, auch wenn spätere Versionen diese Werte auseinanderziehen dürfen.

Vorgeschlagene Startwerte:

- `sehr eng`: `G = 12 Stunden`
- `eng`: `G = 18 Stunden`
- `normal`: `G = 24 Stunden`
- `entspannt`: `G = 36 Stunden`
- `sehr entspannt`: `G = 48 Stunden`

Damit ist im Normalprofil das typische Ziel:

- Tag 1: mehrere Trainingsschritte
- Tag 2: Recall eines früheren Checks

### Ableitung der Zeitfenster

Beim Abschluss eines Schritts wird für den nächsten Schritt gesetzt:

- `available_from = completed_at + G_step`
- für didaktische Übergänge: `overdue_from = available_from + G_step`, also in V2 `completed_at + M * G_step` mit `M = 2`

Beispiel im Normalprofil:

- `training A` endet Montag 10:00
- `recall A.available_from = Dienstag 10:00`
- `recall A.overdue_from = Mittwoch 10:00`

Für `start -> training` gilt stattdessen:

- `training.available_from = completed_at`
- `training.planned_from` kommt aus der Session-Planung
- `training.overdue_from` wird nicht aus `G_gate = 0` abgeleitet
- für erste Trainingsschritte ohne didaktischen Vorgänger gilt dieselbe planbasierte Regel wie bei `start`: `overdue_from = effective_planned_from + G`

Wichtig: Didaktische `available_from`- und `overdue_from`-Zeitpunkte werden beim Abschluss des vorherigen Schritts geschrieben und nicht bei jedem Feed-Read neu berechnet.

## Session-Druck und `planned_from`

Die Session braucht neben dem Ketten-Druck einen zweiten Takt: Welche offenen Schritte müssen wann drankommen, damit die gesamte Session im Zielzeitraum abgeschlossen werden kann?

Deshalb bekommt jeder offene Schritt, auch ein offenes `training`, ein `planned_from`.

### Plan-Kapazität

Konzeptionell gilt:

- `activities_per_day`: materialisierte Session-Geschwindigkeit
- `d`: verbleibende Tage bis zum Session-Ziel
- `C = d * activities_per_day`: grobe Plan-Kapazität der Session-Geschwindigkeit

`activities_per_day` ist ein persistenter Sessionwert in `learning_sessions.activities_per_day`.

- Ohne explizite Nutzerangabe bleibt `activities_per_day = planning.default_activities_per_day`.
- Ein explizites `target_date` aendert nicht stillschweigend die gespeicherte Session-Geschwindigkeit.
- Ein nur vorgeschlagenes `target_date` (`target_source = 'suggested'`) dient als UI- und Planungshinweis, verschärft das Tagespensum nicht selbstständig.
- Für explizite Zieltermine wird zusätzlich `required_activities_per_day = W / d` aus offener Last und verbleibenden Tagen berechnet.

Für Tagesgrenzen, `d` und Tagespakete gilt die Zeitzone `Europe/Berlin`.

Die offene Last wird gewichtet nach Schritttyp betrachtet. Ein möglicher V2-Startwert ist:

- `training = 1.0`
- `recall = 0.7`
- `feynman = 1.0`
- `kompetenzliste = 0.5`

Damit ergibt sich:

`W = 1.0 * n_T + 0.7 * n_R + 1.0 * n_F + 0.5 * n_K`

und fuer explizite Ziele daraus die erforderliche Geschwindigkeit:

`required_activities_per_day = W / d`

Der Druckwert lautet dann:

`p = activities_per_day / required_activities_per_day`

Wenn `W = 0`, gibt es keine offene Last und der Feed liefert einen abgeschlossenen Zustand statt eines Druckprofils.

### Druckprofile

- `sehr eng`: `p < 0.80`
- `eng`: `0.80 <= p < 0.95`
- `normal`: `0.95 <= p < 1.20`
- `entspannt`: `1.20 <= p < 1.45`
- `sehr entspannt`: `p >= 1.45`

Das Druckprofil waehlt das gemeinsame `G` fuer neu entstehende didaktische Übergänge:

- `sehr eng`: `G = 12 Stunden`
- `eng`: `G = 18 Stunden`
- `normal`: `G = 24 Stunden`
- `entspannt`: `G = 36 Stunden`
- `sehr entspannt`: `G = 48 Stunden`

Ein Profilwechsel wirkt nur auf neu entstehende didaktische Übergänge; bereits geschriebene `available_from`- und `overdue_from`-Werte bleiben stabil.

### Lebenszyklus von `planned_from`

`planned_from` ist ein materialisierter Wert. Er wird nicht bei jedem Feed-Read neu berechnet.

Re-Plan-Trigger sind:

- Sessionstart
- Zieldatum- oder Geschwindigkeitsänderung, wobei damit eine Änderung von `activities_per_day` gemeint ist
- Hinzufügen oder Entfernen von Lernbereichen oder Checks
- Abschluss eines Schritts
- Tageswechsel

Der Tageswechsel darf in V2 lazy beim ersten serverseitigen Feed-Read eines neuen Tages verarbeitet werden. Das ist kein normaler Read-Effekt: Der Server schreibt idempotent nur, wenn der letzte Replan vor dem aktuellen Kalendertag in `Europe/Berlin` lag und sich Werte tatsächlich ändern. Weitere Reads desselben Tages verändern `planned_from` nicht.

Replanning verändert primär `planned_from`. `available_from` bleibt stabil. Didaktisch abgeleitete `overdue_from`-Werte bleiben nach dem Schreiben stabil; planbasierte `overdue_from`-Werte für `start` und erste Trainingsschritte dürfen neu berechnet werden, solange der Schritt noch nicht fällig oder überfällig ist.

Kurzregel: Planbasiertes `overdue_from` folgt seinem `planned_from`; didaktisches `overdue_from` bleibt nach dem Schreiben stabil.

### Berechnung von `planned_from`

Alle offenen Schritte werden in eine kanonische Reihenfolge gebracht und in Tagespakete nach `activities_per_day` Aktivitäten pro Tag aufgeteilt.

Beispiel bei `activities_per_day = 3`:

- Rang 1 bis 3: `planned_from = heute`
- Rang 4 bis 6: `planned_from = morgen`
- Rang 7 bis 9: `planned_from = übermorgen`

Ein Schritt kann aus Session-Sicht zwar für heute geplant sein, aus Ketten-Sicht aber erst morgen verfügbar werden. Deshalb gilt für die eigentliche Session-Fälligkeit immer:

- `effective_planned_from = max(available_from, planned_from)`

Bereits fällige oder überfällige Schritte dürfen durch Replanning nicht wieder in die Zukunft geschoben werden.

### Kanonische Reihenfolge für die Planung

Die Rangbildung für `planned_from` muss deterministisch sein. V2 nutzt dafür diese Sortierung:

1. vorhandenes `effective_planned_from`, falls gesetzt, sonst `available_from`
2. fachlich tieferer Schritt einer bereits begonnenen Check-Kette
3. globale Lernbereichs- und Check-Reihenfolge aus Repo-Metadaten
4. Schritt-Reihenfolge `start`, `training`, `recall`, `feynman`, `kompetenzliste`
5. stabiler Tie-Breaker nach `check_id` und `activity_key`

Für offene `start`-Aktivitäten ohne Check gilt die globale Lernbereichsreihenfolge als fachliche Reihenfolge.

## Sticky-Lock

Der Feed hat genau ein aktuelles Element:

- `current_activity_key`

Dieses Element bleibt sticky bis:

- Abschluss
- explizites Verlassen
- Ablauf von `locked_until`
- Ungültigkeit des Elements

Für V2 reicht genau ein Lock-Zeitpunkt:

- `L = 20 Minuten`

Solange `now < locked_until`, bleibt das aktuelle Element oben sichtbar. Neu verfügbare oder neu fällige Schritte können im Hintergrund entstehen, verdrängen das aktuelle Element aber nicht sofort.

Der Lock wird bei einer echten Neuwahl gesetzt:

- `current_activity_key = gewähltes Element`
- `selected_at = now`
- `locked_until = now + L`
- `selection_reason` passend zum Auslöser, z. B. `initial`, `auto_pick`, `lock_expired` oder `invalidated`

Reine Feed-Reads verlängern `locked_until` nicht. Dadurch kann ein Dashboard-Reload den Lock nicht unbegrenzt frisch halten. Der Lock darf nur durch explizite Nutzeraktionen erneuert oder aufgehoben werden.

Explizites Verlassen meint in V2 nur die Feed-Entscheidung `Nein, zum Dashboard`. Navigation über Sidebar oder freier Modulzugriff hebt den Lock nicht auf; er bleibt bestehen oder läuft regulär ab.

## Popup-Semantik beim Abschluss eines Feed-Elements

Die bestehende Popup-Idee bleibt fachlich sinnvoll und wird nur klarer an den Feed-Cursor gekoppelt:

- `Ja, nächste Aktivität`
  Das aktuelle Element wird abgeschlossen. Danach erfolgt eine echte Neuwahl.
- `Ja, zum Dashboard`
  Das aktuelle Element wird abgeschlossen. Danach Rücksprung ins Dashboard.
- `Nein, jetzt wiederholen`
  Das Element bleibt offen und sticky. `locked_until` wird immer auf `now + L` erneuert; `selection_reason` wird `repeat_request`.
- `Nein, zum Dashboard`
  Das Element bleibt offen, aber der Sticky-Lock wird aufgehoben. Bei der nächsten Feed-Abfrage wird neu gewählt.

## Neuwahl-Regel des singulären Feeds

Eine Neuwahl findet statt bei:

- Abschluss des aktuellen Elements
- explizitem Verlassen des aktuellen Elements
- Ablauf von `locked_until`
- Session-Bearbeitung, die das aktuelle Element ungültig macht

Wenn `current_activity_key` gesetzt ist, prüft der Server vor jeder Rückgabe, ob dieses Element noch offen und gültig ist. Ist es abgeschlossen oder ungültig, wird der Cursor gelöscht und neu gewählt.

### Kandidatenpool

In den Kandidatenpool kommen nur Schritte mit:

- `now >= available_from`

### Priorität bei Neuwahl

1. überfällige Schritte (`now >= overdue_from`)
2. geplante fällige Schritte (`now >= effective_planned_from`)
3. nur verfügbare Schritte (`available_from <= now < effective_planned_from`)

Diese Priorität gilt für alle offenen Schrittarten, also auch für offene `recall`, `feynman` und `kompetenzliste`, nicht nur für `training`.

Für die UI soll diese Server-Klasse direkt transportiert werden (`overdue`, `due`, `available`). Das Badge im Feed darf nicht nur aus Browser-Zeitstempeln rekonstruiert werden, weil sonst kleine Uhrabweichungen zwischen Client und Server frisch geplante Schritte fälschlich als nur `available` labeln können.

Innerhalb derselben Prioritätsklasse entscheidet in V2:

1. Klasse 1 nach `overdue_from` aufsteigend, Klasse 2 nach `effective_planned_from` aufsteigend, Klasse 3 nach `available_from` aufsteigend
2. fachlich tieferer Schritt einer bereits begonnenen Kette
3. globale Lernbereichs- und Check-Reihenfolge aus Repo-Metadaten
4. Schritt-Reihenfolge `start`, `training`, `recall`, `feynman`, `kompetenzliste`
5. stabiler Tie-Breaker nach `check_id` und `activity_key`

Ein Schritt ohne `overdue_from` kann nicht in Prioritätsklasse 1 fallen.

## Zustand ohne fälliges Element

Wenn kein Schritt verfügbar ist, zeigt der Feed keinen künstlichen Ersatzschritt.

Stattdessen gibt der Feed einen Wartezustand zurück mit:

- nächstem verfügbaren Schritt
- nächstem `available_from`

Im Wartezustand gibt es keinen Sticky-Lock und keinen `current_activity_key`. Sobald ein Schritt `available_from` erreicht, kann der Feed bei der nächsten Abfrage direkt ein neues aktuelles Element wählen.

Beispieltext für die spätere UI:

- `Nächster Schritt ab Dienstag 10:00: Recall A`

## Session-Bearbeitung während des Laufs

Der Nutzer darf während einer laufenden Session Lernbereiche, Checks und Zieldatum ändern.

Regeln:

1. Abgeschlossene Schritte bleiben stabil.
2. Entfernte Checks verlieren ihre noch offenen künftigen Schritte.
3. Wenn das aktuelle Feed-Element dadurch ungültig wird, wird `current_activity_key` sofort geleert.
4. Nach Zieländerung wird `required_activities_per_day` und damit das Druckprofil neu berechnet.
5. Noch nicht fällige Schritte dürfen mit dem neuen Profil neu geplant werden.
6. Bereits fällige oder überfällige Schritte dürfen nicht wieder in die Zukunft geschoben werden.
7. Der Sticky-Lock bleibt nur bestehen, wenn das aktuelle Element weiterhin gültig ist.

Das aktuelle Element ist ungültig, wenn:

- der zugehörige Check aus der Session entfernt wurde
- der zugehörige Lernbereich aus der Session entfernt wurde
- der Schritt serverseitig bereits abgeschlossen wurde
- der Schritt durch eine Pfadänderung nicht mehr Teil des Lernpfads ist

Eine reine Zieldatumänderung macht das aktuelle Element nicht ungültig.

## Mehr-Tab- und Mehr-Geräte-Semantik

`current_activity_key` und `locked_until` sind session-scoped und serverseitig maßgeblich. Dadurch sehen mehrere Tabs oder Geräte dieselbe fachliche Feed-Auswahl.

Wenn ein Schritt in Tab B abgeschlossen wird, der in Tab A noch als Sticky-Element sichtbar ist, gilt:

- Der Abschluss-RPC löscht den Cursor, wenn `current_activity_key` diesem Schritt entspricht.
- Tab A zeigt den alten Stand bis zum nächsten Read weiter.
- Beim nächsten Read erkennt der Server den Abschluss und gibt eine neue Auswahl oder einen Wartezustand zurück.

Freie Navigation allein erneuert oder löscht den Lock nicht. Ein freier Modulaufruf ohne gültigen Feed-Cursor verändert den Core-Feed nicht; auch ein erfolgreicher freier Modulabschluss schließt keinen Core-Feed-Schritt ab und bewegt die Check-Pipeline nicht weiter.

## Additives Datenmodell (Vorschlag)

Die Umsetzung soll additiv erfolgen und den bestehenden V1-Pfad nicht hart ersetzen.

### Schrittzustand

Option A: Erweiterung von `session_check_state`.

Option B: neue Tabelle `session_check_step` pro `(session_id, check_id, step_key)`.

V2 benötigt fachlich mindestens:

- `session_id`
- `check_id`
- `step_key`
- `status`
- `available_from`
- `planned_from`
- `overdue_from`
- `step_anchor_completed_at`
- `created_at`
- `updated_at`

### Feed-Cursor

Neue session-scoped Projektion, z. B. `session_feed_cursor`:

- `session_id`
- `current_activity_key`
- `locked_until`
- `selected_at`
- `selection_reason`
- `created_at`
- `updated_at`

### Systemwerte

Mögliche neue `public.system_settings`-Schlüssel:

- `planning.default_activities_per_day`
- `feed.core_gap_very_tight_hours`
- `feed.core_gap_tight_hours`
- `feed.core_gap_normal_hours`
- `feed.core_gap_relaxed_hours`
- `feed.core_gap_very_relaxed_hours`
- `feed.pressure_very_tight_threshold`
- `feed.pressure_tight_threshold`
- `feed.pressure_relaxed_threshold`
- `feed.pressure_very_relaxed_threshold`
- `feed.lock_duration_minutes`
- `feed.weight_training`
- `feed.weight_recall`
- `feed.weight_feynman`
- `feed.weight_kompetenzliste`

## Serverseitige Operationen (Zielbild)

Das Frontend soll den V2-Feed nicht per Tabellen-CRUD steuern. Die zentralen Operationen sollten serverseitig laufen:

- `pick_feed_cursor(session_id)`: validiert Cursor, führt bei Bedarf Neuwahl aus und liefert genau ein aktuelles Element oder einen Wartezustand.
- `complete_feed_step(activity_key, decision)`: validiert `activity_key` gegen den aktuellen Feed-Cursor und schließt nur diesen Feed-Schritt ab oder verarbeitet dessen Popup-Entscheidung.
- `replan_session(session_id)`: materialisiert `planned_from` für offene Schritte bei Re-Plan-Triggern.

Namen sind Platzhalter; wichtig ist die Trennung zwischen Lesen, Abschließen und Replanning.

Cursor-Wahl muss atomar sein: Wenn zwei Tabs gleichzeitig einen leeren oder abgelaufenen Cursor lesen, darf serverseitig nur eine Auswahl gewinnen; der zweite Read bekommt den gesetzten Cursor zurück. `pick_feed_cursor(session_id)` darf außerdem das idempotente Tages-Replanning auslösen, bevor es den Cursor validiert oder neu wählt.

## Hinweise für die UI

Fachlich müssen `planned_from` und `overdue_from` getrennt existieren. Im Frontend müssen sie anfangs aber nicht als zwei gleichrangige sichtbare Zustände auftauchen.

Für V2 reicht im UI:

- das aktuelle Element ist `jetzt dran`
- optional ein Zusatz wie `seit heute fällig` oder `seit 2 Tagen fällig`
- optional ein Hinweis, dass nach Lock-Ende neu priorisiert wird

Die eigentliche Ampel- oder CSS-Diskussion kann später erfolgen. Zuerst müssen die fachlichen Zustände sauber vorliegen.

## Goldszenarien

1. Eine neue Session mit mehreren Lernbereichen zeigt zuerst `start` für den ersten Lernbereich.
2. Nach Abschluss von `start` wird das erste `training` des Lernbereichs sofort verfügbar (`G_gate = 0`) und nicht sofort als überfällig markiert.
3. Nach Abschluss von `training A` wird `recall A` im Normalprofil erst am nächsten Tag verfügbar.
4. Ein offenes `training B` bleibt während eines gültigen Sticky-Locks sichtbar, auch wenn `recall A` zwischenzeitlich verfügbar wird.
5. Nach Ablauf des Sticky-Locks wird neu gewählt; ein überfälliger Schritt gewinnt dann gegen ein offenes `training`.
6. `Nein, jetzt wiederholen` erneuert `locked_until` auf `now + L`.
7. `Nein, zum Dashboard` lässt den Schritt offen, entfernt aber den Lock.
8. Wenn kein Schritt verfügbar ist, wird ein Wartezustand statt eines Ersatzschritts gezeigt; dieser Zustand setzt keinen Lock.
9. Ein geändertes Zieldatum darf noch nicht fällige Schritte neu takten, aber bereits fällige Schritte nicht wieder zurückschieben.
10. Wird ein Check aus der Session entfernt, verschwinden seine künftigen offenen Schritte sofort.
11. Session-Druck betrifft alle offenen Schritte, nicht nur Trainingsschritte.
12. Wenn Tab B einen in Tab A gelockten Schritt abschließt, wird der Cursor serverseitig gelöscht und Tab A bekommt beim nächsten Read eine neue Auswahl.
13. Freier Modulzugriff bleibt jederzeit möglich; reine Navigation und freie Modulabschlüsse verändern den Core-Feed nicht.

## Konkrete nächste Schritte

1. Diese V2-Spezifikation fachlich freigeben.
2. Aus den Goldszenarien formale Abnahmekriterien ableiten.
3. Additives Datenmodell gegen `session_check_state` und `session_activity_state` auf Doppelungen prüfen und entscheiden, ob `start` in `session_activity_state` bleibt oder in das neue Schrittmodell wandert.
4. Serverseitige RPCs für Cursor-Wahl, Schrittabschluss und Replanning entwerfen.
5. Erst danach offene UI-Details konkretisieren und die Retention-Anbindung separat spezifizieren.
