# Aktionsfeed

Der Feed steuert, was Schüler:innen als Nächstes tun sollen. Er läuft immer innerhalb einer aktiven **Session**. Eine Session enthält einen oder mehrere Lernbereiche und die je Lernbereich aktiven Checks (Standard: alle). Die Feeds mehrerer Lernbereiche können sich überlappen.

## Übersicht

| Modul | Kernauslöser (Kurz) |
|---|---|
| `einstiegsquiz` | Lernbereich erstmals aktiviert |
| `training` | In der Kette mehrfach pro Check; zusätzlich über `Laufende Checks` |
| `blurting` | `x` Tage nach `training` |
| `feynman` | `x` Tage nach `training` (nach `blurting`) |
| `kompetenzliste` | `x` Tage nach drittem `training` (als gesamte Lernbereichs-Kompetenzliste) |
| `flashcards` | Alle Checks einmal bearbeitet |
| `klausur` | `x` Tage nachdem alle Checks der Kompetenzliste abgeschlossen sind |

---

## Sessionsteuerung

- **Session-Start:** User wählt einen oder mehrere Lernbereiche, optional ausgeschlossene Checks, und startet mit „Los geht's".
- **Ausschlussregel:** Ausgeschlossene Checks tauchen im Feed nicht auf und werden bei Zustandsfortschritt/Fälligkeit nicht berücksichtigt.
- **Session-Parameter:** `x` (Tempo in Tagen) ist Teil der Session und kann pro Session gesetzt werden.
- **Dashboard-Aktionen:**
   - `Neue Session starten`
   - `Aktuelle Session abbrechen`
   - `Session bearbeiten`

- **Session-Bearbeitung (verbindliche Regeln):**
  - **Lernbereich entfernen:** Alle zugehörigen Aktionen und Fortschritte werden aus der aktiven Session entfernt (mit Warnhinweis vor dem Speichern).
  - **Check entfernen:** Alle zugehörigen Aktionen und Fortschritte werden aus der aktiven Session entfernt (mit Warnhinweis vor dem Speichern). Wenn dadurch alle Checks als abgeschlossen gelten, können `flashcards` und `klausur` fällig werden.
  - **Lernbereich hinzufügen:** Das zugehörige `einstiegsquiz` wird sofort fällig und im Feed an erster Stelle angezeigt.
  - **Check in bestehendem Lernbereich hinzufügen:** Das erste `training` der Kette wird sofort fällig. Falls dadurch nicht mehr alle Checks abgeschlossen sind, entfallen ggf. fällige `flashcards`/`klausur` bis zum erneuten Erreichen der Abschlussbedingung.

---

## Module im Detail

### `einstiegsquiz`
- **Zweck:** Vorwissen aktivieren, Einstieg in den Lernbereich motivieren, vorausschauend zeigen „wo die Reise hingeht"
- **Aufbau:** Einfache, motivierende Fragen (keine Zufallsgeneratoren nötig); vorausschauende Erklärungen eingebettet; interaktiv oder nicht — offen
- **Auslöser:** Lernbereich erstmals aktiviert
- **Abschlussbedingung:** Einmal bearbeitet 
- **Nächste Aktion:** Erster Training-Check
- **Implementierung:** Muss pro Lernbereich manuell erstellt werden

Nach dem Einstiegsquiz gibt es je Check die Kette der Module `training` -> `blurting` -> `training` -> `feynman` -> `training` -> `kompetenzliste`. Auslöser von `blurting`, `feynman` und `kompetenzliste` ist stets `x` Tage nach Erfüllung der Abschlussbedingung des vorherigen Moduls. Bei `kann nicht` in `blurting` oder `feynman` erfolgt kein Modulwechsel: Es wird ein Skript-Link angeboten und dasselbe Modul kann nach `y`  Minuten erneut bearbeitet werden. Der jeweilige Eintrag bleibt bis zur Auswahl `kann` als oberster offener Feed-Eintrag für den Check stehen. Die Feeds für die verschiedenen Checks können sich dabei überlappen.

Der Kompetenzlisten-Eintrag wird im Feed immer als **gesamte Kompetenzliste des Lernbereichs** angezeigt (nicht als einzelner Check).

Setze zunächst `x = 1`.

### `training`
- **Zweck:** Zentrale Übungseinheit mit formativem Feedback
- **Aufbau:** Interaktive Aufgaben mit automatischer Bewertung
- **Aufrufwege:**
   - innerhalb der Kette (`training` vor `blurting`, `training` vor `feynman`, `training` vor `kompetenzliste`)
   - jederzeit über `5) Laufende Checks`
- **Abschlussarten:**
   - **Automatisierter Abschluss:** Alle Fragen eines Checks richtig beantworten. Ein Check kann beliebig oft wiederholt werden; es müssen nicht in einem Durchgang alle Fragen richtig sein (z. B. bei 3 Fragen: im 1. Durchgang nur Frage 2 richtig, im 2. Durchgang Fragen 1 und 3 richtig -> Abschluss erfüllt). Eine Frage zählt nur dann als richtig, wenn vorher keine Lösung angezeigt wurde.
   - **Manueller Abschluss:** User klickt nach dem Training auf „Weiter" (oder äquivalent) und setzt den Trainingsschritt manuell als abgeschlossen.
- **Wirkung der Abschlussarten:**
   - automatisiert **oder** manuell gesetzter Abschluss kann das nächste Modul in der Kette auslösen
   - nur automatisierte Abschlüsse zählen für die Kompetenzlisten-Freigabe (3 fehlerfreie Trainingsabschlüsse)
   - solange weniger als 3 automatisierte Trainingsabschlüsse vorliegen, gilt das entsprechende `training` weiterhin als ausgelöst
- **Auslöser:**
   - erstes `training`: direkt nach Einstiegsquiz
   - zweites `training`: `x` Tage nach erfolgreichem `blurting`
   - drittes `training`: `x` Tage nach erfolgreichem `feynman`
- **Implementierung:** Aufgaben kommen aus generierten JSONs

### `blurting`
- **Zweck:** Active Recall auf Begriffsebene (primär: Begriffe nennen, nicht ausformuliert erklären)
- **Aufbau:** Dem/der Schüler:in wird ein Schlüsselbegriff präsentiert und zum Brainstormen aufgefordert; danach (Timer) Selbstüberprüfung mit eingeblendeten Referenz-Begriffen und Selbsteinschätzung (`kann` / `kann nicht`)
- **Abschlussbedingung:** Selbsteinschätzung `kann`
- **Bei `kann nicht`:** Skript-Link zum passenden Abschnitt einblenden; nach 10 Minuten kann `blurting` erneut durchgeführt werden
- **Feed-Priorität:** `blurting` bleibt für den betroffenen Check an erster Stelle im Feed, bis `kann` ausgewählt wird
- **Auslöser:** `x` Tage nach Abschluss des vorherigen Moduls (`training`)
- **Implementierung:** Schlüsselbegriffe pro Check in `checks.json`, Feld `Blurting`; UI braucht Begriff, Referenz-Begriffe und 2-stufige Selbsteinschätzung, zeitgesteuert (z. B. 5 min)

### `feynman`
- **Zweck:** Tieferes Verständnis durch Erklären einer Methode/Technik
- **Aufbau:** Prompt der Art „Erkläre, wie man die Extrempunkte einer Funktion berechnet" → strukturiertes Erklären einer konkreten Technik/eines klaren Sachverhalts
- **Abschlussbedingung:** Selbsteinschätzung (evtl. erst nach Ablauf eines Timers möglich)
- **Bei `kann nicht`:** Skript-Link zum passenden Abschnitt einblenden; nach 10 Minuten kann `feynman` erneut durchgeführt werden
- **Feed-Priorität:** `feynman` bleibt für den betroffenen Check an erster Stelle im Feed, bis `kann` ausgewählt wird
- **Auslöser:** `x` Tage nach Abschluss des vorherigen Moduls (`training` nach `blurting`)
- **Implementierung:** Ähnlich wie Blurting; Technik-Prompts müssen pro Lernbereich definiert und mit den relevanten Checks verknüpft werden, UI braucht Prompt (in `checks.json`, Feld `feynman`), evtl. Avatar zur Erklärungsatmosphäre, zeitgesteuert (z. B. 5 min)


### `kompetenzliste`
- **Zweck:** Strukturierte Selbsteinschätzung der Kompetenzen
- **Auslöser:** `x` Tage nach Abschluss des vorherigen Moduls (drittes `training`); angezeigt wird immer die gesamte Kompetenzliste des Lernbereichs
- **Abschlussbedingung:** Eine Kompetenz kann nur dann als abgeschlossen markiert werden, wenn der zugehörige Check zuvor **3 automatisierte** (nicht manuell gesetzte) fehlerfreie Trainingsabschlüsse hat
- **Rücknahme-Regel:** User darf eine Abschlussmarkierung wieder zurücknehmen, wenn Lernlücken auffallen. Das verändert den bisherigen Feed-Verlauf nicht rückwirkend; es wird keine Kette neu gestartet.
- **Hinweislogik:** Falls die 3 automatisierten Trainingsabschlüsse noch nicht erreicht sind, direkter Hinweis „es fehlen noch 1/2/3 erfolgreiche Trainingsabschlüsse"; optional direkte Weiterleitung zum Training
- **Implementierung:** Selbsteinschätzungsfunktion auf `kompetenzliste.md` fehlt noch

Ab hier werden die Feed-Einträge nicht mehr strikt pro Kompetenz/Check gesteuert.

### `flashcards`
- **Zweck:** Retrieval Practice für Begriffe, Formeln, Zusammenhänge
- **Auslöser:** `x` Tage nachdem alle Checks der Kompetenzliste abgeschlossen sind, danach alle `y` Tage
- **Implementierung:** Basis vorhanden; Intervalllogik prüfen (Open End, zeitgesteuert, z. B. 5 min; keine Anzeige der Art `10/10`, aber Berücksichtigung der Selbsteinschätzung)
- **Abschlussbedingung:** Nicht vorhanden, da offene Wiederholung

### `klausur`
- **Zweck:** Prüfungssimulation über einen kompletten Lernbereich
- **Aufbau:** Alle Aufgaben eines Lernbereichs auf PDF (zum Ausdrucken oder auf dem Screen per Pen zu bearbeiten)
- **Auslöser:** `x` Tage nachdem alle Checks der Kompetenzliste abgeschlossen sind
- **Implementierung:** Schüler:innen bekommen PDF-Export mit aufeinander folgenden Aufgaben (eine Seite pro Aufgabe), ein Tag später die Lösungen; zu überlegen: Aufgaben nicht aus den bestehenden Trainings-JSONs übernehmen, sondern neu mit den Generatoren erstellen, damit sie sich von den Trainingsaufgaben unterscheiden (dafür müssten langfristig alle JSONs generatorbasiert sein, keine rein manuell erstellten Aufgaben mehr)

---

## Laufende Checks
Neben dem Feed gibt es im Dashboard eine Übersicht der laufenden Checks, also der Checks, die im Feed schon einmal erschienen sind, mit kurzer Übersicht (z. B. wie oft richtig beantwortet). Per Klick gelangt man direkt ins Training. Trainings können daher sowohl über den Feed als auch über `Laufende Checks` gestartet werden. Nach Abschluss eines Checks (Zustand 5) gibt es keinen Feed-Eintrag mehr für diesen Check. In `Laufende Checks` bleibt er mit kleiner Markierung (abgeschlossen, 100 %) sichtbar. Das Check-Training bleibt dennoch jederzeit erreichbar (u. a. für 100 % Kompetenzfortschritt), ohne zeitliche Restriktionen für Wiederholungen.

## Zustandsmodell pro Check
1. **Zustand 1:** Check noch nie getriggert
2. **Zustand 2:** Check in der Kette
   - **a)** `training` (1)
   - **b)** `blurting`
   - **c)** `training` (2)
   - **d)** `feynman`
   - **e)** `training` (3)
3. **Zustand 3:** Check nach der Kette, aber noch keine 3 automatisierten Trainingsabschlüsse
   - Das zugehörige `training` gilt weiterhin als ausgelöst, bis 3 automatisierte Abschlüsse erreicht sind
4. **Zustand 4:** 3 automatisierte Trainingsabschlüsse vorhanden, Kompetenz noch nicht als abgeschlossen markiert
5. **Zustand 5:** Kompetenz/Check als abgeschlossen markiert

Hinweis: Bei Rücknahme der Abschlussmarkierung wechselt der Check von Zustand 5 zurück in Zustand 4; der bereits durchlaufene Feed bleibt unverändert.

## Reihenfolge im Dashboard-Feed
1. Nur fällige Aktionen werden angezeigt (Aktion wurde ausgelöst).
2. Bei mehreren fälligen Aktionen gilt: je kleiner der Zustand (1 bis 5), desto höher im Feed.
3. Innerhalb von Zustand 2 ordnen die Teilzustände `a` bis `e`.
4. Bei Konflikten zwischen Lernbereichen gilt die fest hinterlegte Lernbereichs-Reihenfolge.
5. Session-Bearbeitung mit Regel "Lernbereich hinzufügen" übersteuert diese Sortierung einmalig (neues `einstiegsquiz` an erster Stelle).
6. Bei verbleibender Gleichheit (inkl. Teilzustandsgleichheit) entscheidet der frühere Auslöse-Zeitstempel.
7. Zustand 5 wird nicht mehr im Feed angezeigt.

## Feed-Datenmodell (Trennung)
- **Verlinkungsdaten (Routing):** `session_id`, `lernbereich`, `modultyp`, `check_id`
- **Steuerungsdaten (Logik):** Zustand/Teilzustand, Auslöse-Zeitstempel, Abschluss-Zeitstempel, `automated_training_count`, Retry-/Cooldown-Information, Session-Parameter (`x`)

### Dashboard

Der Kompetenzfortschritt wird im Dashboard pro Lernbereich und pro Check ausgewiesen.

- Kompetenzfortschritt für gesamten Lernbereich: Aufteilen der 100 % in `n+1` Teile, wobei `n` die Anzahl der Checks ist
   - `1/(n+1)` nach Einstiegsquiz
   - danach jeweils `1/(n+1)` pro abgeschlossenem Check; zusätzlich wird der Kompetenzfortschritt pro Check berücksichtigt
- Kompetenzfortschritt pro Check
   - 50 % nach erfolgreichem Abschluss des ersten Trainings; Fragen anteilig berücksichtigen (hat der Check 4 Fragen, dann 12,5 % nach erster richtiger Frage, 25 % nach zweiter, 37,5 % nach dritter, 50 % nach vierter)
   - 60 % nach erfolgreichem Abschluss `blurting`
   - 65 % nach erfolgreichem Abschluss des zweiten Trainings
   - 70 % nach erfolgreichem Abschluss `feynman`
   - 80 % nach erfolgreichem Abschluss des dritten Trainings
   - 90 % wenn 3 automatisierte Trainingsabschlüsse erreicht sind (Kompetenzlisten-Freigabe)
   - 100 % nach Markierung „Check abgeschlossen" in der Kompetenzliste
 
### Offene Fragen / Zu klärende Punkte


- **Technische Trigger:** Wie werden Auslöser in Firestore abgebildet?
- **Firestore-Datenmodell:** Wie werden `state`, `substate`, Zeitstempel, `automated_training_count` und Feed-Historie pro `check_id` gespeichert (Collection-/Dokumentstruktur)?
- **Bewertung:** Das Zustandsmodell 1-5 mit Teilzustand 2a-2e ist didaktisch klar und technisch gut abbildbar; zusätzliche Komplexität entsteht vor allem im Übergang Zustand 3 -> 4.