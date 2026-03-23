# Datenmodell & Inhalts-Architektur

Dieses Dokument beschreibt, wo Inhalte gespeichert sind, wer sie konsumiert und welche Konventionen gelten.

## Prinzip: Single Source of Truth

Jede Art von Inhalt wird **genau einmal** hinterlegt. Module sind Konsumenten, keine Eigentümer von Daten.


## Datenquellen

| Datenentität | Datei/Ordner | Granularität | Inhalt |
|---|---|---|---|
| **Lernbereich-Metadaten** | `_data/dev_lernbereiche.yml` | pro Lernbereich | Slug, Name, Gebiet, Szenario (Kontext, Einstiegsfrage, Abschluss, Bild) |
| **Check-Metadaten** | `dev/checks.json` | pro Check | Nummer, Name, Kompetenztext, Stichwörter, Skript-Anker |
| **Aufgaben** | `aufgaben/exports/json/*.json` | pro Check | Randomisierte Aufgaben mit Lösungen (Python-generiert) |
| **Beispiele** | `_data/dev_beispiele/<lernbereich>.yml` | pro Check | Standardbeispiel: Aufgabe + Lösungsweg (YAML mit LaTeX) |
| **Warm-Up** | `_data/dev_warmup.yml` | pro Lernbereich | 4 Karten (Wusstest-du, Schätzfrage, Vorwissen, Alltag) + Abschlusstext |
| **Modultypen** | `_data/dev_moduletypen.yml` | pro Modultyp | Farben, Icons, Beschreibungen |
| **Gebiete** | `_data/dev_gebiete.yml` | pro Gebiet | Analysis, Lineare Algebra, Stochastik |


## Modul → Datenquelle (Konsumenten-Matrix)

```
                    dev_lernbereiche  checks.json  dev_beispiele  Aufgaben-JSON  dev_warmup
                    (pro LB)          (pro Check)  (pro Check)    (pro Check)    (pro LB)
                    ────────────────  ───────────  ─────────────  ─────────────  ──────────
Start               Name, Gebiet
Warm-Up                                                                          4 Karten
Kompetenzliste                        Kompetenztext
Skript (Szenario)   szenario_einstieg
Skript (Fachinhalt) (direkt in MD)
Skript (Check-Anker)                  Stichwörter  Beispiel       1 Aufgabe
Skript (Abschluss)  szenario_abschluss
Training                                                          Aufgaben
Blurting                              Stichwörter
Feynman                               Stichwörter  Beispiel
Flashcards                                                        Aufgaben
```

## Kernszenario pro Lernbereich

Jeder Lernbereich hat ein durchgängiges Anwendungsszenario, das in `_data/dev_lernbereiche.yml` definiert ist.

### Felder

| Feld | Zweck |
|---|---|
| `szenario` | Kurzbeschreibung des Kontexts (1 Satz) |
| `szenario_einstieg` | Offene Frage, die zu Beginn des Skripts aufgeworfen wird (noch nicht lösbar) |
| `szenario_abschluss` | Auflösung am Ende des Skripts (Frage mit gelernten Methoden beantwortet) |
| `szenario_bild` | Dateiname des charakteristischen Bilds (`dev/assets/img/szenarien/<dateiname>`) |

### Verankerung im Skript

```
## [Szenario-Titel]              ← Bild + Alltagstext + offene Frage (szenario_einstieg)
## Einführung                     ← Fachlicher Einstieg (wie bisher)
## ...                            ← Fachinhalt mit Check-Ankern
## Zurück zum [Szenario]         ← Frage lösen mit gelernten Methoden (szenario_abschluss)
```

### Designentscheidung

- **Übungsaufgaben** (Training, Flashcards) sind bewusst **nicht** an das Szenario gebunden, um kontextunabhängigen Transfer zu sichern.
- **Warm-Up-Karten** orientieren sich am Szenario, müssen aber nicht exklusiv darauf beschränkt sein.
- Das Szenario dient als **roter Faden**, nicht als Korsett.


## Beispiele (`_data/dev_beispiele/`)

Pro Lernbereich eine YAML-Datei. Jeder Check hat einen Eintrag mit `aufgabe` und `loesung`.

### Format

```yaml
check-slug:
  aufgabe: "Aufgabentext mit $LaTeX$."       # Inline-String
  loesung: |                                   # Block-String (| bewahrt Zeilenumbrüche)
    Lösungsweg mit $$align$$-Umgebungen.
    Kein Doppel-Escaping nötig im |-Block.
```

### Konvention

- Kurze Aufgabentexte als Inline-Strings (`"..."`, LaTeX mit `\\`)
- Lösungswege als `|`-Blöcke (LaTeX ohne Doppel-Escaping)
- Schlüssel = Check-Slug aus `checks.json`


## Modulübersicht (Inhaltsquelle pro Modul)

| Modul | MD-Datei | Primäre Inhaltsquelle | Anmerkung |
|---|---|---|---|
| Start | `start.md` | direkt in MD | Überblick, Lernpfad |
| Warm-Up | `warmup.md` | `dev_warmup.yml` | 4 Karten + Abschluss, via Liquid-Template |
| Kompetenzliste | `kompetenzliste.md` | `checks.json` | Kompetenztexte, via JS |
| Training | `training.md` | `aufgaben/exports/json/` | Randomisierte Aufgaben, via JS |
| Blurting | `blurting.md` | `checks.json` (Stichwörter) | Active Recall, via JS |
| Feynman | `feynman.md` | `checks.json` + `dev_beispiele/` | Stichwörter + Beispiel, via JS |
| Skript | `skript.md` | direkt in MD + Szenario aus `dev_lernbereiche.yml` | Fachinhalt, Check-Anker |
| Flashcards | `flashcards.md` | `aufgaben/exports/json/` | Spaced Repetition, via JS |
