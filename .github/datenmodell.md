# Datenmodell & Inhalts-Architektur

Dieses Dokument beschreibt, wo Inhalte gespeichert sind und welche Module sie nutzen. Inhaltliche Regeln: `inhalte.md`.

## Prinzip: Single Source of Truth

Jede Art von Inhalt wird **genau einmal** hinterlegt. Module sind Konsumenten, keine Eigentümer von Daten.

Persistente Plattformdaten sind davon getrennt: Lern-Sessions, Check-Pipeline, Feed-Aktivitäten und nutzerbezogene Flashcard-Durchgänge liegen in Supabase. Das Repo bleibt Source of Truth für Lernbereiche, Checks, Aufgabenpools und Karteninhalt; Supabase speichert nur persönliche Zustände, Durchgänge, Bewertungen und Fälligkeiten.


## Datenquellen

| Datenentität | Datei/Ordner | Granularität | Inhalt |
|---|---|---|---|
| **Lernbereich-Metadaten** | `_data/lernbereiche.yml` | pro Lernbereich | Slug, Name, Gebiet, Bild, didaktische Reihenfolge |
| **Themen** | `_data/themen.yml` | pro Thema | Slug, Name, Gebiet; Obermenge der Lernbereiche (jeder Lernbereich = Thema mit gleichem Slug), auch nicht umgesetzte Themen aus Musterprüfungen |
| **Check-Metadaten** | `_data/checks.json` (unter `/checks.json` als JSON ausgeliefert) | pro Check | Nummer, Name, Kompetenztext, Tipps, optionale Recall-Felder, Skript-Anker |
| **Aufgaben** | `aufgaben/exports/json/<gebiet>/<lb>/<sammlung>.json` | pro Check | Randomisierte Aufgaben mit Lösungen (Python-generiert) |
| **Test-Fragen** | `test/<gebiet>/<lb>/<check_id>.json` | pro Check | 10 Single-Choice-Fragen (handgepflegt) |
| **Musterprüfungen** | `muster-pruefungen/abitur/pruefungen-md/` (gitignored) | pro Teilaufgabe | Abituraufgaben mit Erwartungshorizont; `_themen.json` = Index Thema → Teilaufgaben |
| **Beispiele** | `lernbereiche/<gebiet>/<lb>/beispiele/<NN>-<sammlung>.md` | pro Check | Standardbeispiel: Aufgabe + Lösungsweg (Markdown mit LaTeX) |
| **Warm-Up** *(nicht verlinkt)* | `_data/warmup/<gebiet>/<lernbereich>/<NN>-<sammlung>.yml` | pro Check | Geführter Einstieg: Karten mit Schritten (Vormachen, Fading); Titel, Kompetenz, Nummer, Trainingslink aus `checks.json`; Format → `_data/warmup/README.md` |
| **Startseiten-Texte** | `_data/start/<lernbereich>.yml` | pro Lernbereich | „Worum geht es“, Vorkenntnisse, optional Podcast-Metadaten |
| **Modultypen** | `_data/moduletypen.yml` | pro Modultyp | Farben, Icons, Beschreibungen |
| **Gebiete** | `_data/gebiete.yml` | pro Gebiet | Analysis, Lineare Algebra, Stochastik, Finanzmathematik |


## Beispiele

Pro Check eine Datei `lernbereiche/<gebiet>/<lernbereich>/beispiele/<NN>-<sammlung>.md`:

- `<NN>` = zweistellige `Nummer` aus `_data/checks.json`, `<sammlung>` = `Sammlung` (1:1)
- Front Matter nur `layout: null` und `permalink` (gleicher Pfad mit `.html`); die Zuordnung zum Check ergibt sich aus dem Dateinamen
- Inhaltliche Regeln: `inhalte.md`

Das Bild für die Materialkarte eines Lernbereichs steht im Feld `bild` in `_data/lernbereiche.yml` (Datei in `assets/img/start/`).


## Modulübersicht (Inhaltsquelle pro Modul)

`checks.json` steht hier kurz für `_data/checks.json`.

| Modul | MD-Datei | Primäre Inhaltsquelle | Anmerkung |
|---|---|---|---|
| Start | `start.md` | `_data/start/<lernbereich>.yml`, `checks.json`, `medien/podcast.mp3` | Überblick, Vorkenntnisse, Lernpfad, optional Podcast |
| Warm-Up *(nicht verlinkt)* | `warmup.md` | `_data/warmup/<gebiet>/<lernbereich>/*.yml` + `checks.json` | nur in Lernbereichen mit Warm-Up; Auswahl per `#check-<Nummer>`, via JS; `noindex`, kein Reiter in der Navigation |
| Kompetenzliste | `kompetenzliste.md` | `checks.json` | Kompetenztexte, via JS |
| Training | `training.md` | `aufgaben/exports/json/` | Randomisierte Aufgaben, via JS |
| Recall | `recall.md` | `checks.json` (`Tipps`, `Ich kann`) | Geführter Active Recall, via JS |
| Feynman | `feynman.md` | `checks.json` (Tipps) + `beispiele/*.md` | Tipps + Beispiel, via JS |
| Test | `test.md` | `test/<gebiet>/<lernbereich>/<check_id>.json` | 10 Single-Choice-Fragen pro Check, via JS |
| Skript | `skript.md` | direkt in MD; je Check-Anker: Tipps, Beispiel, 1 Aufgabe | Fachinhalt mit Szenario und Check-Ankern |
| Flashcards | `flashcards.md` | `aufgaben/exports/json/` | Karteninhalt aus Aufgaben; Feed-Spaced-Repetition serverseitig |

## Persistente Plattformdaten

Aktueller Stand mit v2-Grundlage:

- `learning_sessions`: aktive Lernkonfiguration eines Benutzers plus Planungsparameter wie Zieltermin, Zeitzone, Freigabelimit und Parallelitätsgrenze.
- `session_check_state`: checkbezogene Feed-Pipeline (`training`, `recall`, `feynman`, `test`) inklusive materialisiertem letztem erfolgreichem Abschlusszeitpunkt.
- `session_activity_state`: lernbereichsweite Feed-Projektion für `start` und `flashcards` innerhalb einer Core-Session.
- `user_retention_scopes`: nutzerweite Retention-Scope-Projektion für Flashcards nach Ende einer Core-Session.
- `user_feed_activity_counters`: user-scoped Zähler abgeschlossener Feed-Aktivitäten; Referenzgröße für serverseitige Retention-Abstände.
- Flashcard-Tabellen: sessionseitige Durchgänge plus additive user-scoped Retention-Zustände für Kartenfälligkeiten jenseits der Core-Session.

Der freie Flashcards-Aufruf persistiert keinen Spaced-Repetition-Zustand im Browser. Im Feed-Kontext werden nur Karten-IDs, Check-IDs, Aufgabenindex, Bewertung und Fälligkeit gespeichert; der eigentliche Aufgaben-/Karteninhalt bleibt in `aufgaben/exports/json/`. Die endliche Core-Session und die länger laufende Retention-Schicht bleiben dabei bewusst getrennt.


## `_data/checks.json` — Feldsemantik

Verantwortung: inhaltliche Felder → Content-Agent; `Sammlung` → Python-Agent.

| Feld | Verantwortung | Beschreibung |
|---|---|---|
| `Gebiet` | Content | `analysis`, `lineare-algebra`, `stochastik` oder `finanzmathematik` |
| `Lernbereich` | Content | Slug des Lernbereichs (z. B. `quadratische-funktionen`) |
| `LernbereichAnzeigename` | Content | Anzeigename (z. B. „Quadratische Funktionen") |
| `Nummer` | Content | Fortlaufend innerhalb des Lernbereichs, bestimmt Reihenfolge |
| `check_id` | Content | Schema: `<gebiet>__<lernbereich>__<NN>` (zweistellig) |
| `Ich kann` | Content | Kompetenzformulierung, endet mit Verb |
| `Schlagwort` | Content | Treffendes Kürzel für den Check (2–4 Wörter) |
| `Tipps` | Content | Array aus `{cue, response}`, Regeln in `inhalte.md` |
| `tippOrder` | Content | `shuffle` oder `fixed` (Prozess-Tipps) |
| `skript_anchor` | Content | Schema: `check-<gebiet>-<lernbereich>-<NN>` |
| `Flashtyp` | Content | `einzeln` oder `gruppiert` |
| `questionOrder` | Content | `shuffle` (Standard) oder `fixed` |
| `Sammlung` | Python-Agent | Slug der Aufgabensammlung |
