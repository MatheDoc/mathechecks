# MatheChecks AI-Agenten-Anweisungen

Dieses Dokument enthält wichtige Kontextinformationen für KI-Agenten, die mit dem MatheChecks-Codebase arbeiten.

## Projektübersicht

MatheChecks ist eine auf Jekyll basierende Bildungsplattform für mathematische Inhalte. Das Projekt kombiniert statische Seitengenerierung mit interaktiven Komponenten zur Vermittlung mathematischer Lerninhalte.

## Hauptkomponenten

### Inhaltsstruktur
- `/lernbereiche/` - Hauptinhalte, nach mathematischen Themen geordnet
- `/_includes/` - Wiederverwendbare HTML-Komponenten und interaktive Elemente
- `/_layouts/` - Jekyll-Layoutvorlagen

### Wichtige Dateien
- `_config.yml` - Jekyll-Konfiguration
- `kompetenzliste.json` - Grundlegende Kompetenzdefinitionen

## Inhaltskonventionen

### Markdown-Dateien
- Verwendung von YAML-Frontmatter mit erforderlichen Feldern: `layout`, `title`, `description`
- Mathematische Inhalte verwenden KaTeX/MathJax-Syntax innerhalb von `$$`-Begrenzern
- Interaktive Elemente werden über spezielle Include-Tags eingebunden

Beispiel:
```markdown
---
layout: skript
title: Beispieltitel
description: Kurze Beschreibung
lernbereich: themen-bezeichner
---
```

### Interaktive Komponenten
- Komponenten sind in `/_includes/` definiert
- Einbindung über Jekyll-Include-Syntax: `{% include komponenten-name.html param=wert %}`

## Entwicklungs-Workflow

### Lokale Entwicklung
1. Jekyll-Server: `bundle exec jekyll serve --port 4001`

### Deployment
- Seite wird über GitHub Pages bereitgestellt (automatisch auf dem main-Branch)

## Integrationspunkte
- MathJax für mathematisches Rendering
- Benutzerdefinierte interaktive Komponenten für Visualisierungen

## Häufige Muster
- Verwendung von Jekyll-Layouts für einheitliche Seitenstruktur
- Mathematische Inhalte sollten zugänglich und korrekt formatiert sein
- Interaktive Elemente sollten statische Fallback-Inhalte haben

## Hinweise
- Deutsch ist die primäre Inhaltssprache
- Mathematische Notation folgt Standard-LaTeX-Konventionen
- Inhalte sollten thematisch in `/lernbereiche/` organisiert werden