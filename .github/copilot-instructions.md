# MatheChecks AI-Agenten-Anweisungen

Dieses Dokument ist der zentrale Einstieg für alle KI-Agenten im Projekt.

## Projektziel

MatheChecks soll Schüler:innen der Sekundarstufe II das bestmögliche Framework zum Lernen von Mathematik bieten.
Alle Entscheidungen zu Struktur, Inhalt, UX und Technik werden daran gemessen.

## Grundprinzipien für alle Agenten

- Fachlich korrekt vor „schön formuliert“.
- Didaktisch wirksam vor maximaler Feature-Dichte.
- Kleine, nachvollziehbare Änderungen vor großen Umbauten.
- Konsistente Begriffe, Symbolik und Notation über Inhalte, Aufgaben und UI hinweg.
- Deutsch als Standardsprache.

## Projektkontext (Kurzfassung)

- Jekyll-basiertes Projekt mit Lerninhalten, Übungsmaterial und interaktiven Komponenten.
- Kernbereiche:
	- `/lernbereiche/` (Inhalte)
	- `/_includes/`, `/_layouts/` (Bausteine/Layouts)
	- `/assets/` (CSS/JS)
	- `aufgaben/` (Python-Aufgabenerzeugung)

## Inhaltskonventionen

- Markdown-Dateien mit YAML-Frontmatter (`layout`, `title`, `description`; optional z. B. `lernbereich`).
- Mathematische Notation in Aufgaben-/JSON-Texten konsistent als Inline-LaTeX `\\(...\\)` (kein `$$...$$`).
- Interaktive Komponenten über Includes einbinden.

## Struktur für Agenten und Prompts

### 1) Agent-Dateien (Rollen)

- Ablage: `.github/agents/`
- Format: Markdown (`.md`)
- Namensschema: `agent-<rolle>.md`
- Inhalt: Rolle, Zuständigkeiten, Prioritäten, Arbeitsmodus, Übergaben.
- Agent-Dateien enthalten **keine** detaillierten, formatstrengen Output-Verträge für einzelne Features.

### 2) Systemprompts (globale Regeln)

- Ablage: `.github/prompts/`
- Format: Markdown Prompt-Files (`.prompt.md`)
- Namensschema: `systemprompt-<kontext>.prompt.md`
- Inhalt: harte Regeln, Qualitätskriterien, Ausgabeformat, Negativliste, Prioritäten.

### 3) Spezifische Prompts (Task/Feature)

- Primär in `.github/prompts/` oder bei starker Kontextbindung direkt am Modul.
- Namensschema: `prompt-<zweck>.prompt.md`
- Inhalt: eng umrissener Arbeitsauftrag (z. B. Review, Migration, Qualitätscheck).

## Trennung der Verantwortung

- `copilot-instructions.md`: Projektziele, Leitplanken, Strukturkonventionen.
- `agent-*.md`: Wer macht was und nach welchen Prioritäten.
- `systemprompt-*.prompt.md`: Wie Inhalte/Artefakte generiert werden müssen.
- `prompt-*.prompt.md`: Konkrete, wiederverwendbare Arbeitsaufträge.

## Offene Strukturentscheidungen

Die grundlegende Lernbereichsarchitektur ist projektweit verbindlich:

- pro Lernbereich gibt es mindestens die Seiten **Checkliste**, **Training** und **Skript**
- jede Kompetenz in der Checkliste hat mindestens eine zugeordnete Aufgabe im Training
- jede Aufgabe im Training hat einen klaren inhaltlichen Bezug im Skript
- diese Zuordnung zieht sich konsistent durch alle Lernbereiche

Weitere Seiten (z. B. Start, Flashcards) sind möglich, aber optional.

## Automatisch generierte Seiten

Die folgenden Seiten werden **nicht manuell befüllt**, sondern zur Laufzeit automatisch aus `/kompetenzliste.json` erzeugt:

- **Kompetenzliste** (`kompetenzliste.md`): Die zugehörige JS-Datei (`assets/js/kompetenzliste.js`) liest `kompetenzliste.json`, filtert nach `Lernbereich` und rendert die Tabelle dynamisch.
- **Flashcards** (`flashcards.md`): Die zugehörige JS-Datei (`assets/js/flashcards.js`) liest ebenfalls `kompetenzliste.json`, filtert nach `Lernbereich` und generiert die Lernkarten automatisch.

Diese Dateien brauchen lediglich das korrekte YAML-Frontmatter (`layout`, `title`, `description`, `lernbereich`, ggf. `gebiet`). Inhalt im Markdown-Body ist nicht nötig und wird ignoriert.

## Verknüpfungsprinzip Kompetenz -> Aufgabe -> Skript

- Kompetenzbeschreibungen, Aufgabenstellungen und Skriptabschnitte verwenden konsistente Begriffe und Symbolik.
- Zu jeder Kompetenz soll nachvollziehbar sein, **wo geübt** wird (Training) und **wo erklärt** wird (Skript).
- Bei neuen Inhalten ist die Verknüpfung explizit mitzudenken und bei Überarbeitungen mitzuprüfen.

## Qualitätssicherung

- Bei Änderungen immer prüfen: Beitrag zum Lernzuwachs, fachliche Korrektheit, Verständlichkeit, Anschlussfähigkeit.
- Bestehende Projektkonventionen und Dateistrukturen respektieren, sofern kein klarer Grund zur Änderung vorliegt.
