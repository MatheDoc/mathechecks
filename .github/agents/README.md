# Agenten-Struktur für MatheChecks

Diese Dateien definieren Rollen für wiederkehrende Arbeitsmodi.
Sie ergänzen die Prompt-Dateien in `.github/prompts/`.

## Ziel

- Zuständigkeiten klar trennen.
- Kontext pro Chat klein und fokussiert halten.
- Entscheidungen konsistent auf das Projektziel ausrichten.

## Agenten

1. `agent-content-didaktik.md`
   - mathematische Inhalte, Erklärtexte, Aufgabenstellungen, Feedbacksprache
2. `agent-python-aufgaben.md`
   - Aufgabengeneratoren, Exportlogik, Python-Refactoring in `aufgaben/`
3. `agent-frontend-ux.md`
   - Lernoberfläche, Includes, Layouts, Barrierearmut und Bedienbarkeit
4. `agent-infra-architektur.md`
   - Systemgrenzen, Firebase/Functions, Regeln, Deploy-/Risikoaspekte
5. `agent-aktionsfeed.md`
   - Feed-Logik „Deine nächsten Aktionen": Aktionstypen, Trigger, Priorisierung, Spaced Repetition, nicht-digitale Lernstrategien

## Abgrenzung zu Prompts

- Agent-Dateien beantworten: **Wer arbeitet mit welchem Fokus?**
- Systemprompts beantworten: **Welche verbindlichen Output-/Qualitätsregeln gelten?**
- Task-Prompts beantworten: **Was ist der konkrete Auftrag in diesem Task?**

## Konvention

- Dateinamen: `agent-<rolle>.md`
- Format: Markdown
- Kopfbereich: YAML-Frontmatter mit `name` und `description`
- Inhalt: Rolle, Zuständigkeiten, Prioritäten, Arbeitsmodus, Übergabeformat
