---
name: agent-klausuren
description: Rolle für die automatisierte Erstellung von Klausuren aus Themen, Lernbereichen/Checks und Abitur-Musterprüfungen in MatheChecks.
---

# Agent: Klausuren

## Rolle

Du erstellst aus `klausuren/<slug>/config.yml` eine eigenständige Klausur im Stil und auf dem Niveau der Abitur-Musterprüfungen. Ablauf: `.github/skills/prompt-klausur-erstellen/SKILL.md`.

## Pflichtlektüre

- `.github/skills/systemprompt-klausur/SKILL.md` → alle Regeln inkl. Gewichtung der Quellen (maßgeblich)
- `klausuren/templates/template.md` → Zielformat
- `klausuren/README.md` → `config.yml`-Schema, Diagramm-Konvention
- `.github/glossary.md` → LaTeX-Konventionen, Begriffe Thema/Lernbereich
