# Datenmodell & Inhalts-Architektur

Dieses Dokument beschreibt, wo Inhalte gespeichert sind, wer sie konsumiert und welche Konventionen gelten.

## Prinzip: Single Source of Truth

Jede Art von Inhalt wird **genau einmal** hinterlegt. Module sind Konsumenten, keine Eigentümer von Daten.

Persistente Plattformdaten sind davon getrennt: Lern-Sessions, Check-Pipeline, Feed-Aktivitäten und nutzerbezogene Flashcard-Durchgänge liegen in Supabase. Das Repo bleibt Source of Truth für Lernbereiche, Checks, Aufgabenpools und Karteninhalt; Supabase speichert nur persönliche Zustände, Durchgänge, Bewertungen und Fälligkeiten.


## Datenquellen

| Datenentität | Datei/Ordner | Granularität | Inhalt |
|---|---|---|---|
| **Lernbereich-Metadaten** | `_data/lernbereiche.yml` | pro Lernbereich | Slug, Name, Gebiet, Szenario (Kontext, Einstiegsfrage, Abschluss, Bild) |
| **Check-Metadaten** | `checks.json` | pro Check | Nummer, Name, Kompetenztext, Tipps, optionale Recall-Felder, Skript-Anker |
| **Aufgaben** | `aufgaben/exports/json/*.json` | pro Check | Randomisierte Aufgaben mit Lösungen (Python-generiert) |
| **Beispiele** | `lernbereiche/<gebiet>/<lb>/beispiele/<NN>-<sammlung>.md` | pro Check | Standardbeispiel: Aufgabe + Lösungsweg (Markdown mit LaTeX) |
| **Warm-Up** | `_data/warmup/<slug>.yml` | pro Lernbereich | meist 3 Karten, optional 4, plus Abschlusstext |
| **Modultypen** | `_data/moduletypen.yml` | pro Modultyp | Farben, Icons, Beschreibungen |
| **Gebiete** | `_data/gebiete.yml` | pro Gebiet | Analysis, Lineare Algebra, Stochastik |


## Modul → Datenquelle (Konsumenten-Matrix)

```
                    lernbereiche.yml  checks.json  beispiele/*.md  Aufgaben-JSON  warmup/*.yml
                    (pro LB)          (pro Check)  (pro Check)    (pro Check)    (pro LB)
                    ────────────────  ───────────  ─────────────  ─────────────  ───────────
Start               Name, Gebiet
Warm-Up                                                                          meist 3 Karten
Kompetenzliste                        Kompetenztext
Skript (Szenario)   szenario_einstieg
Skript (Fachinhalt) (direkt in MD)
Skript (Check-Anker)                  Tipps        Beispiel       1 Aufgabe
Skript (Abschluss)  szenario_abschluss
Training                                                          Aufgaben
Recall                               Tipps, Ich kann
Feynman                               Tipps        Beispiel
Flashcards                                                        Aufgaben
```

## Kernszenario pro Lernbereich

Jeder Lernbereich hat ein durchgängiges Anwendungsszenario, das in `_data/lernbereiche.yml` definiert ist.

### Felder

| Feld | Zweck |
|---|---|
| `szenario` | Kurzbeschreibung des Kontexts (1 Satz) |
| `szenario_einstieg` | Offene Frage, die zu Beginn des Skripts aufgeworfen wird (noch nicht lösbar) |
| `szenario_abschluss` | Auflösung am Ende des Skripts (Frage mit gelernten Methoden beantwortet) |
| `szenario_bild` | Dateiname des charakteristischen Bilds (`assets/img/start/<dateiname>`) |

### Verankerung im Skript

```
## [Szenario-Titel]              ← Bild + Alltagstext + offene Frage (szenario_einstieg)
## Einführung                     ← Fachlicher Einstieg (wie bisher)
## ...                            ← Fachinhalt mit Check-Ankern
## Zurück zum [Szenario]         ← Frage lösen mit gelernten Methoden (szenario_abschluss)
```

### Designentscheidung

- **Übungsaufgaben** (Training, Flashcards) sind bewusst **nicht** an das Szenario gebunden, um kontextunabhängigen Transfer zu sichern.
- **Warm-Up-Karten** dürfen sich am Szenario orientieren, funktionieren aber auch als eigenständiger, motivierender Auftakt ohne direkte Skript-Vorbereitung.
- Das Szenario dient als **roter Faden**, nicht als Korsett.


## Beispiele

Pro Check eine Markdown-Datei im Ordner `beispiele/` des jeweiligen Lernbereichs.

### Pfad

```
lernbereiche/<gebiet>/<lernbereich>/beispiele/<NN>-<sammlung>.md
```

### Namenskonvention

- `<NN>` = zweistellige Nummer aus `checks.json` (steuert die Reihenfolge analog zum Skript)
- `<sammlung>` = `Sammlung`-Wert aus `checks.json` (1:1, keine Transformation)
- Beispiel: `07-kennzahlen-rechnerisch-e1k3.md`

### Inhalt

- Reines Markdown + LaTeX/MathJax — kein Front Matter, keine Metadaten
- Die Zuordnung zum Check ergibt sich aus Pfad und Dateiname
- Typischer Inhalt: Aufgabenstellung, Lösungsweg mit `$$align$$`-Umgebungen


## Modulübersicht (Inhaltsquelle pro Modul)

| Modul | MD-Datei | Primäre Inhaltsquelle | Anmerkung |
|---|---|---|---|
| Start | `start.md` | direkt in MD | Überblick, Lernpfad |
| Warm-Up | `warmup.md` | `_data/warmup/<slug>.yml` | meist 3 Karten + Abschluss, optional 4, via Liquid-Template |
| Kompetenzliste | `kompetenzliste.md` | `checks.json` | Kompetenztexte, via JS |
| Training | `training.md` | `aufgaben/exports/json/` | Randomisierte Aufgaben, via JS |
| Recall | `recall.md` | `checks.json` (`Tipps`, `Ich kann`) | Geführter Active Recall, via JS |
| Feynman | `feynman.md` | `checks.json` (Tipps) + `beispiele/*.md` | Tipps + Beispiel, via JS |
| Skript | `skript.md` | direkt in MD + Szenario aus `_data/lernbereiche.yml` | Fachinhalt, Check-Anker |
| Flashcards | `flashcards.md` | `aufgaben/exports/json/` | Karteninhalt aus Aufgaben; Feed-Spaced-Repetition serverseitig |

## Persistente Plattformdaten

Aktueller Stand mit v2-Grundlage:

- `learning_sessions`: aktive Lernkonfiguration eines Benutzers plus Planungsparameter wie Zieltermin, Zeitzone, Freigabelimit und Parallelitätsgrenze.
- `session_check_state`: checkbezogene Feed-Pipeline (`training_1`, `recall`, `training_2`, `feynman`, `training_3`, `kompetenzliste_gate`) inklusive materialisiertem letztem erfolgreichem Abschlusszeitpunkt.
- `session_activity_state`: lernbereichsweite Feed-Projektion für `start` und `flashcards` innerhalb einer Core-Session.
- `user_retention_scopes`: nutzerweite Retention-Scope-Projektion für Flashcards nach Ende einer Core-Session.
- `user_feed_activity_deferrals`: user-scoped Sperrmarkierungen für zurückgestellte Feed-Aktivitäten; Freigabe über einen Aktivitätszähler statt über Listenplätze.
- `user_feed_activity_counters`: user-scoped Zähler abgeschlossener Feed-Aktivitäten; Referenzgröße für Deferred-Freigaben.
- Flashcard-Tabellen: sessionseitige Durchgänge plus additive user-scoped Retention-Zustände für Kartenfälligkeiten jenseits der Core-Session.

Der freie Flashcards-Aufruf persistiert keinen Spaced-Repetition-Zustand im Browser. Im Feed-Kontext werden nur Karten-IDs, Check-IDs, Aufgabenindex, Bewertung und Fälligkeit gespeichert; der eigentliche Aufgaben-/Karteninhalt bleibt in `aufgaben/exports/json/`. Die endliche Core-Session und die länger laufende Retention-Schicht bleiben dabei bewusst getrennt.


## checks.json — Feldsemantik

Verantwortung: inhaltliche Felder → Content-Agent; `Sammlung` → Python-Agent.

| Feld | Verantwortung | Beschreibung |
|---|---|---|
| `Gebiet` | Content | `analysis`, `lineare-algebra` oder `stochastik` |
| `Lernbereich` | Content | Slug des Lernbereichs (z. B. `quadratische-funktionen`) |
| `LernbereichAnzeigename` | Content | Anzeigename (z. B. „Quadratische Funktionen") |
| `Nummer` | Content | Fortlaufend innerhalb des Lernbereichs, bestimmt Reihenfolge |
| `check_id` | Content | Schema: `<gebiet>__<lernbereich>__<NN>` (zweistellig) |
| `Ich kann` | Content | Kompetenzformulierung — präzise, überprüfbar, endet mit Verb |
| `Schlagwort` | Content | Treffendes Kürzel für den Check (2–4 Wörter) |
| `Tipps` | Content | Array mit kompakten Erinnerungsstützen (dürfen LaTeX enthalten) |
| `skript_anchor` | Content | Schema: `check-<gebiet>-<lernbereich>-<NN>` |
| `Flashtyp` | Content | `einzeln` oder `gruppiert` |
| `questionOrder` | Content | `shuffle` (Standard) oder `fixed` |
| `Sammlung` | Python-Agent | Slug der Aufgabensammlung |
