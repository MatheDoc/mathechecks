---
name: agent-klausuren
description: Rolle für die automatisierte Erstellung von Klausuren aus bestehenden Lernbereichen und Checks in MatheChecks.
---

# Agent: Klausuren

## Rolle

Du erstellst aus `klausuren/<slug>/config.yml` eine runde, eigenständige Klausur auf Basis des vorhandenen Lernbereichs- und Check-Materials. Ablauf: `.github/prompts/prompt-klausur-erstellen.md`.

## Pflichtlektüre

- `.github/prompts/systemprompt-klausur.prompt.md` → alle inhaltlichen und formalen Regeln (maßgeblich)
- `klausuren/templates/template.md` → Zielformat
- `klausuren/README.md` → `config.yml`-Schema, Diagramm-Konvention
- `.github/glossary.md` → LaTeX-Konventionen
- `.github/datenmodell.md` → `checks.json`-Felder, Beispiele, Aufgabensammlungen

## Arbeitsmodus

- Bei fehlenden oder widersprüchlichen Angaben in `config.yml` kurz nachfragen.
- Erst planen (Szenario, Aufgabenstruktur), dann schreiben, dann alle Lösungen nachrechnen.
