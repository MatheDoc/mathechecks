# Prompt-Strategie für MatheChecks

Diese Konvention hält Prompt-Dateien schlank, auffindbar und konsistent.

## Dateitypen

- **Systemprompts** in `.github/prompts/`:
  - Namensschema: `systemprompt-<kontext>.prompt.md`
  - Zweck: globale oder domänenspezifische, wiederverwendbare Regeln
- **Task-/Feature-Prompts** in `.github/prompts/` oder modulnah:
  - Namensschema: `prompt-<zweck>.prompt.md`
  - Zweck: konkreter Arbeitsauftrag für einen klaren Use Case

## Standardstruktur je Systemprompt

1. Ziel
2. Muss-Kriterien
3. Soll-Kriterien
4. Ausgabeformat
5. Negativliste
6. Prioritäten bei Konflikten

## Empfehlungen

- Prompts in Markdown halten und kurz, präzise, testbar formulieren.
- YAML-Frontmatter mit mindestens `description` verwenden.
- Output-Anforderungen immer eindeutig und maschinenprüfbar beschreiben.
- Fachlogik und Formatregeln nicht vermischen.
- Bei lokalen Modulprompts ebenfalls `prompt-...` bzw. `systemprompt-...` verwenden.
- In inhaltlichen Prompts die Verknüpfung Kompetenz -> Aufgabe -> Skript explizit als Pflichtkriterium aufnehmen.

## Startpunkt

- Für neue Systemprompts die Vorlage `systemprompt-template.prompt.md` verwenden.
- Rollen-/Verantwortungsebene liegt in `.github/agents/`.