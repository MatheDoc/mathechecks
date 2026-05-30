# Aktionsfeed

## Dokumentstatus

Diese Datei bleibt als breiterer Design- und Zielbildtext erhalten.
Die aktuell wirksame Feed-Reihenfolge, Hybrid-Mischung und lokale UI-Stabilisierung wird ab jetzt in `.github/feed-logic.md` dokumentiert.
Tabellen, RPCs und Datenmodellgrenzen bleiben in `.github/benutzerverwaltung-mvp.md`.
Die V2-Spezifikation fuer den deterministischen Core-Feed ohne Retention steht in `.github/feed-v2-core-spec.md`.

Der Feed steuert, was Schüler:innen als Nächstes tun sollen. Er ist aktuell **hybrid**: Offene Aktivitäten der aktiven Session bleiben leitend, aber fällige Retention-Flashcards aus früher abgeschlossenen Lernbereichen werden während einer aktiven Session in festen Abständen dazwischen gemischt. Ohne aktive Session bleibt für diese Wiederholungen die zeitbasierte Fälligkeit maßgeblich. Eine Session enthält einen oder mehrere Lernbereiche und die je Lernbereich aktiven Checks (Standard: alle). Die Feeds mehrerer Lernbereiche können sich überlappen.

## Aktueller Implementierungsstand

Stand Mai 2026 ist eine erste checkbezogene Feed-Stufe umgesetzt und um lernbereichsweite Feed-Aktivitäten für `start` und `flashcards` erweitert:

- Das Dashboard speichert, lädt und löscht die aktive Lern-Session über Supabase.
- `session_check_state` ist die serverseitige Projektion des aktuellen Pipeline-Schritts pro Check.
- Dashboard und Sidebar lesen dieselbe Feed-Projektion und ergänzen Titel, Lernbereich, Modulpfad und UI-Metadaten aus dem Repo.
- Der Feed-Kontext wird über URL-Parameter geöffnet: `feed=1`, `check_id`, `activity_key`, `activity_step`, `activity_run`.
- `start`, `training`, `recall`, `feynman`, `kompetenzliste` und `flashcards` haben eine gemeinsame kompakte Feed-Shell im Kartenkopf und eine gemeinsame Feed-Aktionsschicht im Frontend.
- Der aktuelle Feed zeigt insgesamt bis zu fünf Einträge, hält Session-Aktivitäten vorne und mischt fällige Retention-Flashcards während einer aktiven Session nach einem serverseitig gezählten Aktivitätsabstand dazwischen.
- `session_activity_state` enthält aktuell pro Lernbereich zuerst eine direkte `start`-Aktivität und zusätzlich `flashcards`; der Retention-Fallback kann auch aktive Lernbereiche ohne bisherige Retention-Card-State-Zeilen wieder aufnehmen.
- Das Dashboard zeigt neben `Session` und `Feed` zusätzlich eine eigene Box `Abgeschlossen` für vollständig bestätigte Lernbereiche, auch wenn die zugehörige Session bereits beendet ist.
- Flashcard-Durchgänge, Kartenbewertungen und Karten-Fälligkeiten werden serverseitig über `session_flashcard_rounds`, `session_flashcard_round_cards` und `session_flashcard_card_state` gespeichert.
- Zentrale Systemwerte wie Feed-Limit, Hybrid-Abstand und Default-Tempo liegen in `public.system_settings` mit kurzer Beschreibung pro Schlüssel.

Noch nicht umgesetzt sind Feed-Historie, persistierte Start-/Abbruchereignisse und automatisierte Trainingsnachweise. `warmup` ist im aktuellen Feed-Schnitt bewusst ausgeklammert.

## Übersicht

| Modul | Kernauslöser (Kurz) |
|---|---|
| `start` | Direkt nach Session-Start einmal pro Lernbereich als Orientierung und Einstieg |
| `warmup` | Derzeit bewusst nicht Teil des aktuellen Feed-Schnitts |
| `training` | In der Kette mehrfach pro Check; zusätzlich jederzeit frei im Lernbereich |
| `recall` | `x` Tage nach `training` |
| `feynman` | `x` Tage nach `training` (nach `recall`) |
| `kompetenzliste` | `x` Tage nach drittem `training` (als gesamte Lernbereichs-Kompetenzliste) |
| `flashcards` | Nach Abschluss des Lernbereichs in der Session; später erneut als Retention-Wiederholung |
| `klausur` | `x` Tage nachdem alle Checks der Kompetenzliste abgeschlossen sind |

---

## Sessionsteuerung

- **Session-Start:** User wählt einen oder mehrere Lernbereiche, optional ausgeschlossene Checks, und startet mit „Los geht's".
- **Ausschlussregel:** Ausgeschlossene Checks tauchen im Feed nicht auf und werden bei Zustandsfortschritt/Fälligkeit nicht berücksichtigt.
- **Session-Parameter:** `x` (Tempo in Tagen) ist ein späterer Ausbaupunkt; für die erste `session_check_state`-Semantik wird bewusst noch **keine Zeitlogik** verwendet.
- **Dashboard-Aktionen:**
   - `Neue Session starten`
   - `Aktuelle Session abbrechen`
   - `Session bearbeiten`

- **Session-Bearbeitung (verbindliche Regeln):**
  - **Lernbereich entfernen:** Alle zugehörigen Aktionen und Fortschritte werden aus der aktiven Session entfernt (mit Warnhinweis vor dem Speichern).
  - **Check entfernen:** Alle zugehörigen Aktionen und Fortschritte werden aus der aktiven Session entfernt (mit Warnhinweis vor dem Speichern). Wenn dadurch alle Checks als abgeschlossen gelten, können `flashcards` und `klausur` fällig werden.
   - **Lernbereich hinzufügen:** Es entsteht eine neue `start`-Aktivität für diesen Lernbereich; `warmup` bleibt weiterhin außerhalb des aktuellen Feed-Schnitts, neue Checks starten zusätzlich über die bestehende Check-Pipeline.
  - **Check in bestehendem Lernbereich hinzufügen:** Das erste `training` der Kette wird sofort fällig. Falls dadurch nicht mehr alle Checks abgeschlossen sind, entfallen ggf. fällige `flashcards`/`klausur` bis zum erneuten Erreichen der Abschlussbedingung.

## Grundprinzip: Modulzugriff und Feed-Bearbeitung trennen

- Alle Module bleiben jederzeit direkt aufrufbar, auch ohne Session und ohne Feed.
- Die Session bestimmt nur, welche Lernbereiche und Checks im Feed berücksichtigt werden.
- Der Feed steuert also nicht den Zugang zu einem Modul, sondern nur dessen Rolle als **nächste empfohlene Aktivität**.

### Empfohlene UX für den Feed-Kontext

- Kein globaler Schalter der Art `Feed aktivieren`.
- Stattdessen öffnet jeder Feed-Eintrag ein Modul **im Feed-Kontext**. Der Start kommt bewusst nur aus Dashboard oder Sidebar-Projektion, nicht aus dem freien Modulzugriff.
- Der Feed-Kontext wird direkt an der betroffenen Aktivitätskarte sichtbar: ein kompaktes `Feed`-Menü im Kartenkopf kennzeichnet und steuert die laufende Aktivität.
- Es gibt keine großflächige `Feed-Kontext`-Box über dem Modul. Das ist besonders auf mobilen Ansichten zu platzraubend und trennt Start/Abschluss unnötig von der eigentlichen Aktivität.
- Ein Seitenwechsel, der denselben Feed-Kontext nicht weiterträgt, fragt nach, ob die Aktivität wirklich abgebrochen werden soll.
- Links, die dieselbe Aktivität fortsetzen, zum Beispiel `Tipps` vom Training ins Skript, behalten den Feed-Kontext bei und gelten nicht als Abbruch.

### Feed-URL und lokaler Aktivitätszustand

Die aktuelle v1-Implementierung trennt drei Ebenen:

- `activity_key`: stabile Identität der Feed-Aktivität, zum Beispiel `check:<check_id>:training_1`.
- `activity_step`: fachlicher Pipeline-Schritt, zum Beispiel `training_1`, `recall` oder `feynman`.
- `activity_run`: flüchtiger UI-Durchlauf für Eingaben, Bewertungsmarkierungen und lokale UI-Zustände.

Regeln:

- Die Feed-Aufgabeninstanz im Training wird stabil nach `activity_key` gespeichert.
- Freies Training und Feed-Training haben getrennte lokale Aufgabenindizes und Shuffle-Nonces.
- Eingaben, rote/grüne Markierungen und aufgeklappte UI-Zustände hängen zusätzlich an `activity_run`.
- Ein erneutes Öffnen derselben Feed-Aktivität zeigt deshalb dieselbe Feed-Aufgabe, aber ohne alte Eingaben und Bewertungsmarkierungen.
- `activity_run` darf nicht als fachliche Aktivitätsidentität verwendet werden.

### Einheitlich für alle Feed-Elemente

Diese UX darf nicht nur für checkbezogene Module gelten, sondern für alle Aktivitätstypen:

- checkbezogen: `training`, `recall`, `feynman`
- lernbereichsbezogen: `start`, `flashcards`, später `warmup`
- sessionweit: später mögliche Aktivitäten ohne direkten Check- oder Lernbereichsbezug

Der Feed darf also nicht implizit annehmen, dass jede Aktivität eine `check_id` hat.

### Einheitlicher Abschlussmechanismus

- Die Entscheidung `abschließen` oder `offen lassen` sollte für alle Aktivitätstypen gleich aussehen.
- Diese Entscheidung sollte **nicht** als modulspezifischer Sonderbutton erscheinen, sondern als gemeinsame Plattform-Aktion im `Feed`-Menü der aktiven Karte.
- Das Modul liefert nur seinen lokalen Ablauf und ein Signal `bereit für Feed-Entscheidung`.
- Die Plattform zeigt den eigentlichen Feed-Abschluss kartennah und einheitlich.

### Einheitlicher Startmechanismus

- Schon der Einstieg in eine Feed-Aktivität sollte überall gleich aussehen.
- Ein Feed-Eintrag zeigt deshalb keine modulspezifischen Start-Buttons; Dashboard-Karte und Sidebar-Eintrag öffnen die Aktivität direkt über denselben Feed-Kontext.
- Erst danach erscheint das eigentliche Modul oder die jeweilige Aktivitätsoberfläche im Feed-Kontext.
- Der visuelle Unterschied zwischen freiem Aufruf und Feed-Aufruf muss sofort erkennbar sein.

### Einheitliche Feed-Übergänge

Auch technisch sollte der Feed überall dieselben Übergänge kennen:

- Aktivität aus dem Feed öffnen
- Aktivität im Feed abschließen
- Aktivität im Feed offen lassen

Das gilt unabhängig davon, ob die Aktivität checkbezogen, lernbereichsbezogen oder später sessionweit ist.

### Vorschlag für die gemeinsame Feed-Steuerung

Die Feed-Steuerung besteht in v1 aus drei klar getrennten UI-Rollen:

1. **Dashboard/Sidebar:** Startpunkt und Projektion der offenen Session-Aktivitäten
2. **Aktive Karte:** das `Feed`-Menü im Kartenkopf markiert die aktuell geöffnete Feed-Aktivität
3. **Feed-Menü im Kartenkopf:** einheitliche Plattform-Aktionen

Das Feed-Menü zeigt in der ersten Stufe:

- `Aktivität abbrechen`
- `Abschluss vorbereiten`
- danach `Aktivität abschließen` oder `Aktivität wiederholen`

Optional später:

- `Überspringen`
- `Zurück in den Feed`
- `Hilfe / Skript öffnen`

### Sidebar-Rolle

- Die Sidebar zeigt aktuell dieselbe Liste offener Feed-Einträge und dieselbe Reihenfolge wie der Dashboard-Feed.
- Ein Klick auf einen Sidebar-Eintrag löst denselben Feed-Start aus wie ein Klick im Dashboard.
- Sie ist aber nicht der beste einzige Ort für den Abschluss einer Aktivität, weil sie eingeklappt sein kann und auf kleinen Screens leicht an Sichtbarkeit verliert.
- Empfehlenswerter ist daher: Sidebar für Navigation und Status, aktive Karte für Startzustand und Abschluss.

## Generisches Feed-Aktivitätsmodell

Damit Start und Abschluss wirklich überall gleich aussehen, braucht der Feed eine generische Aktivitätsebene.

### Mindestfelder eines Feed-Eintrags

- `activity_key`: stabiler technischer Schlüssel des Feed-Eintrags
- `activity_type`: zum Beispiel `training`, `recall`, `feynman`, `kompetenzliste`, `flashcards`; später auch weitere Aktivitätstypen
- `scope_type`: `check`, `lernbereich` oder später `session`
- `session_id`
- `lernbereich_slug` optional
- `check_id` optional
- `target_module_key`: wohin der Feed-Einstieg routet
- `status`: in der ersten Stufe mindestens `blocked`, `due`, `completed`
- `sort_bucket`: grobe Reihenfolgegruppe im Feed
- `sort_index`: feine Reihenfolge innerhalb der Gruppe
- `title` und kurze Kontextbeschreibung für das UI

### Warum `session_check_state` allein nicht reicht

- `session_check_state` ist gut für die Check-Pipeline.
- Er reicht aber nicht für lernbereichsweite Aktivitäten wie `start`, `flashcards` oder später `warmup`.
- Deshalb braucht das Feed-UI zusätzlich eine generische Aktivitätsprojektion oberhalb der reinen Check-Zustände; mit `start` und `flashcards` ist der erste konkrete Teil davon umgesetzt.

### Empfohlenes Zielbild für die Datenlogik

- `session_check_state`: fachlicher Pipeline-Zustand pro Check
- `session_activity_state`: generische UI-nahe Projektion aller im Feed sichtbaren Aktivitäten

### Minimaler Umgang mit Start und Abschluss in v1

- Der Feed-Einstieg nutzt aktuell `activity_key` plus Routingfelder aus `session_check_state`, `session_activity_state` und Repo-Metadaten.
- Feed-Abschluss und `Aktivität wiederholen` laufen in v1 über eine gemeinsame Feed-Aktionsschicht, die checknahe RPCs für Training/Recall/Feynman/Kompetenzliste und Flashcards-RPCs für Flashcard-Durchgänge bündelt.
- Erst darunter werden die modulspezifischen Rohdaten wie Trainingsabschluss, Recall-/Feynman-Ergebnis oder Flashcard-Bewertungen verarbeitet.
- Dadurch bleibt das Feed-UI gleich, auch wenn die Modul-Interna sehr unterschiedlich sind.

### Pragmatischer Startumfang

Damit der Start technisch klein und belastbar bleibt, sollte der erste echte Feed-Schnitt noch **nicht** alle Aktivitätstypen zugleich persistieren.

Aktueller Stand:

1. Checkbezogene Feed-Aktivitäten laufen über `session_check_state` serverseitig.
2. Dieselbe Feed-Shell wird bereits von Training, Recall, Feynman und Flashcards genutzt.
3. `start` und `flashcards` sind als erste lernbereichsweite Aktivitäten in `session_activity_state` materialisiert.
4. Dashboard und Sidebar lesen bereits dieselbe gemeinsame Feed-Projektion.
5. Weitere lernbereichsweite oder sessionweite Aktivitäten kommen erst in die DB-Projektion, wenn ihre eigenen Rohdaten serverseitig existieren.

Das bedeutet konkret:

- Das UI darf von Anfang an einheitlich sein.
- Das erste Datenmodell darunter darf aber bewusst noch kleiner sein als das spätere Zielbild.
- `session_activity_state` existiert in v1 für `start` und Flashcards, noch nicht als vollständige Feed-Liste für alle Aktivitätstypen.
- Genau dieser Stand ist aktuell erreicht: checkbezogene Feed-Schritte laufen serverseitig, `start` und Flashcards laufen als erste lernbereichsweite Projektion, die vollständige generische Aktivitätsschicht bleibt Zielbild.

Damit bleibt die Trennung sauber:

- Check-Logik bleibt checknah.
- Feed-UI bleibt einheitlich über alle Aktivitätstypen.

## Erste technische Stufe ohne Zeitlogik

Für checkbezogene Pipeline-Schritte gilt bewusst die vereinfachte Regel:

- `fällig` bedeutet nur: dieser Schritt ist in der Kette als nächster dran.
- Es gibt dort noch kein `due_at`, kein `x` in Tagen und keinen zeitlichen Cooldown.
- Ein `repeat` oder `offen lassen` lässt denselben Schritt offen; er bleibt also `fällig`.
- Ein erfolgreicher Abschluss schiebt die Kette sofort logisch weiter; in der aktuellen `session_check_state`-Form wird der nächste Schritt als `due` gespeichert, nicht die komplette Historie aller abgeschlossenen Schritte.
- Zeitliche Verzögerung zwischen `training`, `recall`, `feynman` und weiteren Schritten ist ein späterer Ausbau.

Für nicht-checkbezogene Aktivitäten gilt aktuell:

- `warmup` ist im aktuellen Schnitt bewusst nicht Teil des Feed.
- `start` wird pro Lernbereich einmal direkt nach Session-Beginn fällig und kann ohne weitere Fachlogik abgeschlossen werden.
- `flashcards` werden über `session_activity_state` fällig, sobald ihre fachliche Freigabebedingung gilt.
- Flashcards nutzt bereits `due_at` aus den Kartenfälligkeiten; `offen lassen` hält Flashcards sofort fällig, und der Retention-Fallback kann auch ohne bestehende Retention-Card-States starten.

---

## Module im Detail

### `warmup`
- **Zweck:** Vorwissen aktivieren, Einstieg in den Lernbereich motivieren, vorausschauend zeigen „wo die Reise hingeht"
- **Aufbau:** Einfache, motivierende Fragen (keine Zufallsgeneratoren nötig); vorausschauende Erklärungen eingebettet; interaktiv oder nicht — offen
- **Auslöser:** Lernbereich erstmals aktiviert
- **Abschlussbedingung:** Einmal bearbeitet 
- **Nächste Aktion:** Erster Training-Check
- **Implementierung:** Muss pro Lernbereich manuell erstellt werden

Nach dem Warm-Up gibt es je Check die Kette der Module `training` -> `recall` -> `training` -> `feynman` -> `training` -> `kompetenzliste`. In der ersten technischen Stufe ohne Zeitlogik wird jeweils einfach der **nächste offene Schritt** `fällig`. Ein `offen lassen` bei `recall` oder `feynman` führt zu keinem Modulwechsel; derselbe Schritt bleibt im Feed offen. Erst ein erfolgreicher Abschluss schiebt die Kette weiter. Die Feeds für die verschiedenen Checks können sich dabei überlappen.

Der Kompetenzlisten-Eintrag wird im Feed immer als **gesamte Kompetenzliste des Lernbereichs** angezeigt (nicht als einzelner Check).

Das spätere Session-Tempo `x` wird für die erste technische Stufe bewusst ignoriert.

### `training`
- **Zweck:** Zentrale Übungseinheit mit formativem Feedback
- **Aufbau:** Interaktive Aufgaben mit automatischer Bewertung
- **Aufrufwege:**
   - innerhalb der Kette (`training` vor `recall`, `training` vor `feynman`, `training` vor `kompetenzliste`)
   - jederzeit über den freien Modulzugriff im jeweiligen Lernbereich
- **Abschlussarten:**
   - **Automatisierter Abschluss:** Alle Fragen eines Checks richtig beantworten. Ein Check kann beliebig oft wiederholt werden; es müssen nicht in einem Durchgang alle Fragen richtig sein (z. B. bei 3 Fragen: im 1. Durchgang nur Frage 2 richtig, im 2. Durchgang Fragen 1 und 3 richtig -> Abschluss erfüllt). Eine Frage zählt nur dann als richtig, wenn vorher keine Lösung angezeigt wurde.
   - **Manueller Abschluss:** User klickt nach dem Training auf „Weiter" (oder äquivalent) und setzt den Trainingsschritt manuell als abgeschlossen.
- **Wirkung der Abschlussarten:**
   - automatisiert **oder** manuell gesetzter Abschluss kann das nächste Modul in der Kette auslösen
   - nur automatisierte Abschlüsse zählen für die Kompetenzlisten-Freigabe (3 fehlerfreie Trainingsabschlüsse)
   - solange weniger als 3 automatisierte Trainingsabschlüsse vorliegen, gilt das entsprechende `training` weiterhin als ausgelöst
- **Feed-Abschluss:** In v1 über dieselbe gemeinsame Feed-Shell wie bei Recall und Feynman; kein trainingsspezifischer Sonderbutton in der Karte
- **V1-Serverlogik:** Zunächst wird nur der **manuelle Feed-Abschluss** serverseitig persistiert; automatisierte Trainingsnachweise sind ein späterer eigener Datenpfad
- **Auslöser:**
   - erstes `training`: direkt mit dem ersten offenen Check-Schritt; im aktuellen technischen Schnitt ohne vorgeschaltetes Warm-Up
   - zweites `training`: `x` Tage nach erfolgreichem `recall`
   - drittes `training`: `x` Tage nach erfolgreichem `feynman`
- **Implementierung:** Aufgaben kommen aus generierten JSONs

#### Technische Konsequenz für v1

- Der erste echte Pipeline-Übergang im Backend ist nicht `Frage korrekt beantwortet`, sondern `Training im Feed bewusst abgeschlossen`.
- Dadurch kann `training_1 -> recall`, `training_2 -> feynman` und `training_3 -> kompetenzliste_gate` sauber modelliert werden, ohne sofort die gesamte Trainingsauswertung in die Datenbank zu ziehen.
- Lokale Trainingslogik, Aufgabenshuffle, Lösungsanzeige und spätere Statistik bleiben davon zunächst getrennt.
- Im Feed-Kontext sind `Lösungen anzeigen` und `Neue Aufgabe` in der normalen Trainingskarte deaktiviert; diese Entscheidungen laufen über das Feed-Menü.
- `Tipps` bleibt im Feed-Kontext aktiv und führt ins Skript mit derselben Feed-Aktivität.
- Die Feed-Aufgabe darf nicht durch freie Trainingsaktionen gewechselt oder über freie Lösungen umgangen werden.

### `recall`
- **Zweck:** Geführter Active Recall zu einem einzelnen Check
- **Aufbau:** Kompetenz dauerhaft sichtbar; kurze Denkphase; Kernpunkte aus `Tipps` einprägen; Kernpunkte abrufen und mit Referenz-Kernpunkten abgleichen
- **Modulende ohne Feed:** neutraler Abschlusszustand ohne plattformspezifische Abschlussbuttons
- **Feed-Abschluss:** erfolgt einheitlich über die gemeinsame Feed-Shell im Kartenkopf
- **Bei offen lassen:** derselbe Recall-Schritt bleibt im Feed offen
- **Feed-Priorität:** `recall` bleibt für den betroffenen Check an erster Stelle im Feed, bis die Aktivität als abgeschlossen markiert wird
- **Auslöser:** nach Abschluss des vorherigen Moduls (`training`); in der ersten Stufe ohne Zeitverzug
- **Implementierung:** `Ich kann` und `Tipps` aus `checks.json`; optional `recall.begriff`; UI mit drei Phasen, aber ohne endgültige Feed-Steuerbuttons in der Karte
- **V1-Persistenz:** `can_do` und `repeat` werden als `learning_activity_attempts` gespeichert; `can_do` bewegt die Check-Pipeline weiter, `repeat` hält denselben Schritt offen.

### `feynman`
- **Zweck:** Tieferes Verständnis durch Erklären einer Methode/Technik
- **Aufbau:** Prompt der Art „Erkläre, wie man die Extrempunkte einer Funktion berechnet" → strukturiertes Erklären einer konkreten Technik/eines klaren Sachverhalts
- **Modulende ohne Feed:** neutraler Abschlusszustand ohne plattformspezifische Abschlussbuttons
- **Feed-Abschluss:** erfolgt einheitlich über die gemeinsame Feed-Shell im Kartenkopf
- **Bei offen lassen:** derselbe Feynman-Schritt bleibt im Feed offen
- **Feed-Priorität:** `feynman` bleibt für den betroffenen Check an erster Stelle im Feed, bis die Aktivität als abgeschlossen markiert wird
- **Auslöser:** nach Abschluss des vorherigen Moduls (`training` nach `recall`); in der ersten Stufe ohne Zeitverzug
- **Implementierung:** Ähnlich wie Recall; Technik-Prompts müssen pro Lernbereich definiert und mit den relevanten Checks verknüpft werden, UI braucht Prompt (in `checks.json`, Feld `feynman`), aber keinen endgültigen Feed-Abschlussbutton in der Karte
- **V1-Persistenz:** `can_do` und `repeat` werden als `learning_activity_attempts` gespeichert; `can_do` bewegt die Check-Pipeline weiter, `repeat` hält denselben Schritt offen.


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
- **Auslöser v1:** Sobald alle ausgewählten Checks eines Lernbereichs nach `training_3` mindestens bei `kompetenzliste_gate` stehen. Abgewählte Checks werden weder für die Freigabe noch für den Kartenpool berücksichtigt.
- **Durchgang:** Ein Feed-Durchgang besteht aus bis zu 20 Karten aus den ausgewählten Checks des Lernbereichs. Die Kartenliste und Aufgabenvariante werden serverseitig für den Durchgang stabil gespeichert.
- **Bewertung:** Rot/orange/grün bewertet die einzelne Karte und steuert ihre nächste Fälligkeit. Rot bleibt sehr bald fällig, orange moderat, grün später.
- **Feed-Abschluss:** Nachdem alle Karten bewertet wurden, erscheint über die gemeinsame Feed-Shell der Abschlussdialog `Kann ich` / `Noch nicht`. `Kann ich` schließt den Durchgang und plant den nächsten anhand der Kartenfälligkeiten; `Noch nicht` hält Flashcards sofort fällig und erzeugt beim Weiterarbeiten einen neuen Durchgang.
- **Freier Modus:** Keine lokale Spaced-Repetition- oder LocalStorage-Logik mehr. Die Smileys dienen dort nur noch als flüchtige Navigation zur nächsten Karte.
- **Zielbild Zeitlogik:** Das Session-Tempo bleibt der zentrale Parameter. Ein späterer Zieltermin, z. B. Datum in 30 Tagen, kann daraus einen Plan ableiten, sodass bis dahin mindestens eine definierte Zahl an Flashcard-Durchgängen erreicht wird.

### `klausur`
- **Zweck:** Prüfungssimulation über einen kompletten Lernbereich
- **Aufbau:** Alle Aufgaben eines Lernbereichs auf PDF (zum Ausdrucken oder auf dem Screen per Pen zu bearbeiten)
- **Auslöser:** `x` Tage nachdem alle Checks der Kompetenzliste abgeschlossen sind
- **Implementierung:** Schüler:innen bekommen PDF-Export mit aufeinander folgenden Aufgaben (eine Seite pro Aufgabe), ein Tag später die Lösungen; zu überlegen: Aufgaben nicht aus den bestehenden Trainings-JSONs übernehmen, sondern neu mit den Generatoren erstellen, damit sie sich von den Trainingsaufgaben unterscheiden (dafür müssten langfristig alle JSONs generatorbasiert sein, keine rein manuell erstellten Aufgaben mehr)

---

## Dashboard-Zuschnitt heute

Aktuell zeigt das Dashboard die drei Boxen `Session`, `Feed` und `Abgeschlossen`.

- `Session` verwaltet die aktive Core-Session.
- `Feed` zeigt bis zu fünf offene Aktivitäten aus derselben gemeinsamen Projektion wie die Sidebar.
- `Abgeschlossen` zeigt Lernbereiche, deren ausgewählte Checks über den letzten Kompetenzlisten-Schritt vollständig bestätigt wurden, auch nach bereits beendeten Sessions.

Eine separate Übersicht `Laufende Checks` ist derzeit nicht umgesetzt. Falls sie später zurückkommt, sollte sie nur ein zusätzliches Read-Model sein und keine zweite, konkurrierende Feed-Logik einführen.

## Zustandsmodell pro Check (didaktisches Zielbild)

Das folgende Modell beschreibt die fachliche Zielstruktur. Technisch materialisiert ist aktuell vor allem `current_step_key` plus `current_step_status` in `session_check_state`, nicht die vollständige 1-bis-5-Systematik als eigene Persistenz.

1. **Zustand 1:** Check noch nie getriggert
2. **Zustand 2:** Check in der Kette
   - **a)** `training` (1)
   - **b)** `recall`
   - **c)** `training` (2)
   - **d)** `feynman`
   - **e)** `training` (3)
3. **Zustand 3:** Check nach der Kette, aber noch keine 3 automatisierten Trainingsabschlüsse
   - Das zugehörige `training` gilt weiterhin als ausgelöst, bis 3 automatisierte Abschlüsse erreicht sind
4. **Zustand 4:** 3 automatisierte Trainingsabschlüsse vorhanden, Kompetenz noch nicht als abgeschlossen markiert
5. **Zustand 5:** Kompetenz/Check als abgeschlossen markiert

Hinweis: Bei Rücknahme der Abschlussmarkierung wechselt der Check von Zustand 5 zurück in Zustand 4; der bereits durchlaufene Feed bleibt unverändert.

## Reihenfolge im Dashboard-Feed

Aktueller Stand:

- Dashboard und Sidebar lesen bereits dieselbe gemeinsame Feed-Projektion.
- Das Dashboard zeigt bis zu fünf Einträge; die primäre Karte hebt nur den ersten Eintrag dieser Projektion hervor.
- Session-Aktivitäten aus `session_check_state` und `session_activity_state` haben Vorrang vor Retention-Flashcards.
- Erst ohne Session-Treffer fällt die Projektion auf Retention-Flashcards aus früheren Sessions zurück.
- Die Anzeige- und Routingdaten werden im Frontend aus Repo-Metadaten ergänzt.

Zielbild:

1. Nur fällige Aktionen werden angezeigt (Aktion wurde ausgelöst).
2. Bei mehreren fälligen Aktionen gilt: je kleiner der Zustand (1 bis 5), desto höher im Feed.
3. Innerhalb von Zustand 2 ordnen die Teilzustände `a` bis `e`.
4. Bei Konflikten zwischen Lernbereichen gilt die fest hinterlegte Lernbereichs-Reihenfolge.
5. Session-Bearbeitung mit Regel "Lernbereich hinzufügen" fügt neue Checks direkt wieder als `training_1` in dieselbe Sortierung ein; ein `warmup`-Sondereinstieg ist aktuell bewusst nicht Teil des Feed.
6. Bei verbleibender Gleichheit (inkl. Teilzustandsgleichheit) entscheidet der frühere Auslöse-Zeitstempel.
7. Zustand 5 wird nicht mehr im Feed angezeigt.

## Feed-Datenmodell (Trennung)
- **Verlinkungsdaten (Routing):** `session_id`, `lernbereich`, `modultyp`, `check_id`
- **Steuerungsdaten (Logik):** Zustand/Teilzustand, Auslöse-Zeitstempel, Abschluss-Zeitstempel, `automated_training_count`, Retry-/Cooldown-Information, Session-Parameter (`x`)

### Dashboard (späteres Zielbild)

Der Kompetenzfortschritt wird im Dashboard pro Lernbereich und pro Check ausgewiesen.

- Kompetenzfortschritt für gesamten Lernbereich: Aufteilen der 100 % in `n+1` Teile, wobei `n` die Anzahl der Checks ist
   - `1/(n+1)` nach Warm-Up
   - danach jeweils `1/(n+1)` pro abgeschlossenem Check; zusätzlich wird der Kompetenzfortschritt pro Check berücksichtigt
- Kompetenzfortschritt pro Check
   - 50 % nach erfolgreichem Abschluss des ersten Trainings; Fragen anteilig berücksichtigen (hat der Check 4 Fragen, dann 12,5 % nach erster richtiger Frage, 25 % nach zweiter, 37,5 % nach dritter, 50 % nach vierter)
   - 60 % nach erfolgreichem Abschluss `recall`
   - 65 % nach erfolgreichem Abschluss des zweiten Trainings
   - 70 % nach erfolgreichem Abschluss `feynman`
   - 80 % nach erfolgreichem Abschluss des dritten Trainings
   - 90 % wenn 3 automatisierte Trainingsabschlüsse erreicht sind (Kompetenzlisten-Freigabe)
   - 100 % nach Markierung „Check abgeschlossen" in der Kompetenzliste
 
### Offene Fragen / Zu klärende Punkte


- **Technische Trigger:** Welche zusätzlichen Aktivitäten werden als nächstes serverseitig ausgelöst: automatisierte Trainingsnachweise, Lernbereichsabschlüsse oder weitere lernbereichsweite Module?
- **Backend-Datenmodell:** Wie wird die aktuell Flashcards-spezifische `session_activity_state` zu einer vollständigen Feed-Projektion für weitere Aktivitätstypen verbreitert?
- **Feed-Historie:** Welche Start-, Abbruch-, Wiederholungs- und Abschlussereignisse müssen persistent nachvollziehbar sein?
- **Bewertung:** Das Zustandsmodell 1-5 mit Teilzustand 2a-2e ist didaktisch klar und technisch gut abbildbar; zusätzliche Komplexität entsteht vor allem im Übergang Zustand 3 -> 4.