# MatheChecks  Copilot Instructions

## Projekt
Jekyll-Lernplattform für Sekundarstufe II Mathematik. Deutsch. Fachlich korrekt > schön formuliert. Kleine Änderungen > große Umbauten.

## Konventionen
- Mathe-Notation: immer `\(...\)` (kein `$$...$$`)
- Markdown-Dateien: YAML-Frontmatter mit `layout`, `title`, `description` (+ optional `lernbereich`, `gebiet`)
- Interaktive Komponenten über `_includes/` einbinden

## Lernbereichs-Architektur (verbindlich)
Jeder Lernbereich hat: `start.md`, `skript.md`, `uebungen.md`, `kompetenzliste.md`, `flashcards.md`
- `kompetenzliste.md` + `flashcards.md`: nur YAML-Frontmatter nötig  werden automatisch aus `kompetenzliste.json` gerendert
- Jede Kompetenz hat mind. eine Aufgabe im Training und einen Bezug im Skript

## Datei-Rollen
- `.github/agents/agent-<rolle>.md`  Rollen und Zuständigkeiten
- `.github/prompts/systemprompt-<kontext>.prompt.md`  harte Ausgaberegeln
- `.github/prompts/prompt-<zweck>.prompt.md`  konkrete Arbeitsaufträge

## Qualität
Bei Änderungen prüfen: fachliche Korrektheit, Verständlichkeit, Kompetenz-Aufgabe-Skript-Verknüpfung.